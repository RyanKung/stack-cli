# coding utf8
from functools import reduce, wraps, partial
from operator import add
from typing import Callable, Iterable
from argparse import ArgumentParser

__all__ = ['ignore', 'as_command_wrapper']


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


def as_command_wrapper(fn: Callable, parser: ArgumentParser) -> Callable:
    '''
    mark a function as command
    '''
    command_argument_paraser(fn, parser)

    @wraps(fn)
    def handler(*args: Iterable, **kwargs: dict) -> Callable:
        return fn(*args, **kwargs)

    return handler


if __name__ == '__main__':
    import doctest
    doctest.testmod()
