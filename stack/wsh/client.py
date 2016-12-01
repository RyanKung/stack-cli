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
        await asyncio.sleep(0.5)
        res = input('In: ')
        return res


async def ws_client(session, host='ws://127.0.0.1',
                    port='8964', project='default', cmd=None):
    addr = 'ws://{host}:{port}/wsh/{project}'.format(
        host=host, port=port, project=project)

    async def send(ws, raw):
        ws.send_str(raw)
        async for msg in ws:
            if msg.tp == aiohttp.MsgType.text:
                if msg.data in ['close', 'quit', 'exit']:
                    await ws.close()
                    break
                else:
                    print(msg.data)
                    break
            elif msg.tp == aiohttp.MsgType.closed:
                print(msg)
                sys.exit(1)
            elif msg.tp == aiohttp.MsgType.error:
                print(msg)
                sys.exit(0)

    async with session.ws_connect(addr) as ws:
        if cmd:
            await send(ws, cmd)
        async for raw in aioInput():
            await send(ws, raw)
    return ws

async def fire(session, host='ws//127.0.0.1',
               port='8964', project='default', cmd='help'):
    addr = 'ws://{host}:{port}/wsh/{project}'.format(
        host=host, port=port, project=project)
    async with session.ws_connect(addr) as ws:
        ws.send_str(cmd)
    return ws


def main(host='127.0.0.1', port='8964', project='default', cmd=None):
    loop = asyncio.get_event_loop()
    with aiohttp.ClientSession(loop=loop) as client:
        loop.run_until_complete(ws_client(
            session=client, host=host, port=port, project=project, cmd=cmd))

if __name__ == '__main__':
    main()
