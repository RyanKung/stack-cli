# coding utf8
from functools import reduce, wraps, partial
from operator import add
from typing import Callable, Iterable
from argparse import ArgumentParser
import asyncio
from types import coroutine

__all__ = ['ignore', 'as_command_wrapper', 'syncio', 'sync2async']

loop = asyncio.get_event_loop()


def syncio(fn, loop):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return loop.run_until_complete(fn(*args, **kwargs))

    return wrapper


def sync2async(fn: Callable) -> coroutine:
    async def handler(*args, **kwargs):
        def wrapper(ft: asyncio.Future):
            print('call wrapper')
            res = fn(*args, **kwargs)
            ft.set_result(res)
            loop.stop()
        future = asyncio.Future()
        loop.call_later(0, partial(wrapper, future))
        return future
    return handler

syncio = partial(syncio, loop=loop)


def ignore(fn: Callable, res=None) -> Callable:
    '''
    Ignore any exceptions and return the default value

    >>> @partial(ignore, res='')

    ... def tester():
    ...    assert True == False
    ...    return
    >>> assert tester() == ''
    '''
    @wraps(fn)
    def handler(*args, **kwargs) -> Callable:
        try:
            return fn(*args, **kwargs)
        except:
            return res
    return handler


def command_argument_paraser(fn: Callable, parser: ArgumentParser) -> list:
    '''
    Read the __doc__ part of function, and register it to the ArgumentParser
    '''

    @partial(ignore, res='')
    def doc_parser(doc: str) -> str:
        '''
        allow doc format: @xxxx and :xxxx
        eg:
            @parms: foo
            :parms: foo
            @argument: foo
        '''
        kvs = doc.strip().split(', ')
        if kvs[0].startswith(('@', ':')):
            return add([kvs[0].split(' ')[1]], kvs[1:])
        else:
            return doc.strip()

    def parse_doc(params: Iterable) -> (tuple, dict):
        '''
        map str to args list and kwargs dict, then
        '''
        args = (p for p in params if '=' not in p)
        kwargs = dict((tuple(p.split('=')) for p in params if '=' in p))
        return args, kwargs

    def add_params(parser: ArgumentParser, param: Iterable) -> ArgumentParser:
        '''
        apply the argument
        '''
        args, kwargs = parse_doc(param)
        parser.add_argument(*args, **kwargs, type=str)
        return parser

    docs = tuple(map(doc_parser, filter(bool, fn.__doc__.split('\n'))))
    name = fn.__name__
    params = filter(lambda x: isinstance(x, list), docs)
    helps = filter(lambda x: isinstance(x, str), docs)
    command = parser.add_parser(name, help=reduce(add, helps))
    return reduce(add_params, params, command)


def command_argument_register(fn: Callable, mdict: dict) -> None:
    mdict.update({fn.__name__: fn})


def as_command_wrapper(fn: Callable, parser: ArgumentParser, mdict={}) -> Callable:
    '''
    mark a function as command
    '''
    command_argument_paraser(fn, parser)
    command_argument_register(fn, mdict)

    @wraps(fn)
    def handler(*args: Iterable, **kwargs: dict) -> Callable:
        return fn(*args, **kwargs)

    return handler


def as_wsh_command_wrapper(fn: Callable, mdict={}) -> Callable:
    '''
    mark a function as wsh command
    '''
    command_argument_register(fn, mdict)

    @wraps(fn)
    def handler(*args: Iterable, **kwargs: dict) -> Callable:
        return fn(*args, **kwargs)

    return handler


if __name__ == '__main__':
    import doctest
    doctest.testmod()
