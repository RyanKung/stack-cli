# coding utf8


from aiohttp import web
import asyncio
import os
from aiohttp import MultiDict
from aiohttp.web_urldispatcher import UrlDispatcher
from urllib.parse import parse_qsl
from typing import Callable
from types import CoroutineType
from functools import partial
from ..utils import io_echo
from io import StringIO
from functools import wraps
import sys

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
        return partial(fns.get(fn_name, lambda: 'None'), *args, **kwargs)
    else:
        args = args[1:]
        return wraps(fn)(partial(fn, *args))


class AioIOWrapper(object):
    def __init__(self, fn):
        self.stderr = StringIO()
        self.stdout = StringIO()
        self.fn = fn
        self.is_async = False

    async def __aiter__(self):
        self.called = await self.io_wrapper(self.fn)
        return self

    async def __anext__(self):
        if self.stdout.closed:
            raise StopAsyncIteration
        raw = self.read()
        if not raw:
            await asyncio.sleep(0.5)
        if 'EOF' not in raw:  # ignore '\0` case
            return raw
        else:
            res = raw[:-3]
            self.flush()
            return res

    async def io_wrapper(self, fn: [Callable, CoroutineType]):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        res = fn()
        if isinstance(res, CoroutineType):
            self.is_async = True
            return res
        else:
            res and self.stdout.write(res)  # for returning `str` and `None` case
            self.stdout.write('EOF')

    def read(self):
        out = self.stdout.getvalue()
        err = self.stderr.getvalue()
        res = out or err
        if res:
            return res

    def flush(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.stdout.close()
        self.stderr.close()

    @staticmethod
    async def run(fn, sock):
        if fn.__wrapped__:
            fn.__wrapped__.ws = sock
        called = AioIOWrapper(fn)
        async for out in called:
            out and sock.send_str(out)
        if not called.is_async:
            sock.send_str('\0')


def io_wrapper(fn: Callable, callback: Callable, ws) -> str:
    outio = StringIO()
    errio = StringIO()
    sys.stderr = errio
    sys.stdout = outio
    try:
        fn.__wrapped__.ws = ws
    except:
        pass

    res = fn() or outio.getvalue() + errio.getvalue()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    outio.close()
    errio.close()
    del outio
    del errio
    try:
        if fn.__wrapped__.async:
            return
    except:
        pass
    return callback(res)


async def wsh(request, handler=print, project='default'):
    project = request.match_info.get('project', project)
    ws = web.WebSocketResponse()

    def send(ws, text):
        ws.send_str(text)
        ws.send_str('\0')

    await ws.prepare(request)
    async for msg in ws:
        if msg.tp == web.MsgType.text:
            await AioIOWrapper.run(fn=handler(msg.data), sock=ws)
        elif msg.tp == web.MsgType.binary:
            await AioIOWrapper.run(fn=handler(msg.data), sock=ws)
        elif msg.tp == web.MsgType.close:
            print('websocket connection closed')
    return ws

async def api(request, handler=print, project='default'):
    project = request.match_info.get('project', project)
    data = MultiDict(parse_qsl(request.query_string))
    cmd = data.get('cmd', '')
    _, ret = io_wrapper(handler(cmd), callback=lambda x: web.Response(body=x.encode()))
    return ret


def main(host='127.0.0.1', port=8964, pattern={}, project='default'):
    loop = asyncio.new_event_loop()
    app = web.Application(router=router, loop=loop)
    app.router.add_route('GET', '/wsh/{project}',
                         partial(wsh, project=project, handler=partial(command_parser, fns=pattern)))
    app.router.add_route('GET', '/api/{project}',
                         partial(api, project=project, handler=partial(command_parser, fns=pattern)))
    print('running on pid %s' % os.getpid())
    return web.run_app(app, host=host, port=int(port))


if __name__ == '__main__':
    main()
