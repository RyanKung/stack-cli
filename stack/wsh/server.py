# coding utf8


from aiohttp import web
import asyncio
import os
from aiohttp.web_urldispatcher import UrlDispatcher
from typing import Callable
from functools import partial
from ..utils import io_echo
from functools import wraps
import sys
from .wrappers import AioIOWrapper

__all__ = ['router']

router = UrlDispatcher(app=NotImplemented)
print = partial(print, file=sys.__stdout__)


def out(s: str):
    '''
    Show info message with yellow color
    '''
    return io_echo("\033[92mOut: {}\033[00m" .format(s))


def command_parser(cmd: str, fns: dict) -> Callable:
    '''
    get target function from funs dict and \
    map command like "cmd arg0 arg1 arg2 --key1=v1 --key2=v2" to \
    partial(fn, arg0, arg1, arg2, key1=v1, key2=v2)

    '''
    args = cmd.strip().split(' ')
    fn_name = args[0]
    fn = fns.get(fn_name, None)
    if not fn:
        return wraps(print)(partial(lambda: print(NotImplemented)))

    if fn.strict:
        args = [i for i in args[1:] if not i.startswith('-')]
        kwargs = dict([i.replace('-', '').split('=') for i in args[1:] if i.startswith('-')])
        return wraps(fn)(partial(fns.get(fn_name, lambda: 'None'), *args, **kwargs))
    else:
        args = args[1:]
        return wraps(fn)(partial(fn, *args))


async def wsh(request, handler=print, project='default'):
    project = request.match_info.get('project', project)
    ws = web.WebSocketResponse()

    def send(ws, text):
        ws.send_str(text)
        ws.send_str('\0')

    await ws.prepare(request)
    async for msg in ws:
        if msg.tp == web.MsgType.text:
            try:
                await AioIOWrapper.run(fn=handler(msg.data), sock=ws)
            except Exception as ex:
                ws.send_str(str(ex))
                raise(ex)
        elif msg.tp == web.MsgType.binary:
            try:
                await AioIOWrapper.run(fn=handler(msg.data), sock=ws)
            except Exception as ex:
                ws.send_str(str(ex))
                raise(ex)
        elif msg.tp == web.MsgType.close:
            print('websocket connection closed')
    return ws


def main(host='127.0.0.1', port=8964, pattern={}, project='default'):
    router.add_route('GET', '/wsh/{project}',
                     partial(wsh, project=project, handler=partial(command_parser, fns=pattern)))
    print('running on pid %s' % os.getpid())
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = web.Application(router=router, loop=asyncio.get_event_loop())
    return web.run_app(app, host=host, port=int(port))


if __name__ == '__main__':
    main()
