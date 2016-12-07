# coding utf8
import aiohttp
import asyncio
import sys


class aioInput(object):
    async def __aiter__(self):
        return self

    async def __anext__(self):
        raw = await self.get_input()
        if not raw == 'quit':
            return raw
        else:
            raise StopAsyncIteration

    async def get_input(self):
        res = input('\33[92mIn: \033[00m|')
        return res

async def listen_ws(ws, repl=True):
    async for msg in ws:
        if msg.tp == aiohttp.MsgType.text:
            sys.stdout.write("%s" % msg.data)
        if msg.tp == aiohttp.MsgType.binary:
            sys.stdout.write("%s" % str(msg.data))
        elif msg.tp == aiohttp.MsgType.closed:
            sys.exit(1)
        elif msg.tp == aiohttp.MsgType.error:
            print(msg)
            break
        if msg.data == '\0':
            await listen_kbd(ws)
        if msg.data == 'quit':
            sys.exit(1)


async def listen_kbd(ws):
    async for raw in aioInput():
        ws.send_str(raw)
        await listen_ws(ws)

async def ws_client(session, host='ws://127.0.0.1',
                    port='8964', project='default', cmd=None):
    addr = 'ws://{host}:{port}/wsh/{project}'.format(
        host=host, port=port, project=project)

    async with session.ws_connect(addr) as ws:
        if cmd:
            ws.send_str(cmd)
            await listen_ws(ws, repl=False)
        else:
            await listen_kbd(ws)
    return ws


def main(host='127.0.0.1', port='8964', project='default', cmd=None):
    loop = asyncio.get_event_loop()
    with aiohttp.ClientSession(loop=loop) as client:
        loop.run_until_complete(ws_client(
            session=client, host=host,
            port=port, project=project,
            cmd=cmd))

if __name__ == '__main__':
    main()
