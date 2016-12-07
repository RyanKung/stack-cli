import sys
from io import StringIO
import asyncio
from typing import Callable
from types import CoroutineType

__all__ = ['AioIOWrapper']


class AioIOWrapper(object):
    def __init__(self, fn):
        self.stderr = StringIO()
        self.stdout = StringIO()
        self.fn = fn
        self.check_coroutine(fn)

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
#        sys.stderr = self.stderr
        res = fn()
        if isinstance(res, CoroutineType):
            return res
        res and self.stdout.write(res)  # for returning `str` and `None` case
        self.stdout.write('EOF')

    def check_coroutine(self, fn):
        if hasattr(fn, '__wrapped__') and getattr(fn.__wrapped__, 'is_coroutine', None):
            self.is_coroutine = True
        else:
            self.is_coroutine = False

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
        if hasattr(fn, '__wrapped__'):
            fn.__wrapped__.ws = sock
        called = AioIOWrapper(fn)
        if called.is_coroutine:
            await fn()
        else:
            async for out in called:
                out and sock.send_str(out)
            sock.send_str('\0')
