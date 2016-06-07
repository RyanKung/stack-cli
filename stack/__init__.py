# coding: utf8
"""
    stack-cli
    ~~~~~~~~~

    `stack-cli` is the core part of `Stack` project, which provides
    to the `stack` files.

    You can write a `stackfile.py` like this:

    from stack.decorators import as_command

    @as_command
    def do(args):
        '''
        sth
        @argument --sth, help=dowhat, metavar=something
        '''
        print('do %s' % args.sth)


    The `stack-cli` will parse the `__doc__` of function to the arguments
    and passes to the `argparse` moudle

"""
from functools import partial
from .decorators import as_command_wrapper, as_wsh_command_wrapper
from argparse import ArgumentParser

__all__ = ['__version__', 'parser', 'as_command', 'pattern']

__version__ = '0.2.2b2'
pattern = {}
wsh_pattern = {}
parser = ArgumentParser(description='Stack-cli - The Python Tool Stack-cli %s' % __version__)
parser.usage = 'stack [-h]'
subparsers = parser.add_subparsers(title='Available options:', help='Run `stack COMMAND -h` to get help')
as_command = partial(as_command_wrapper, parser=subparsers, mdict=pattern)
wsh_command = partial(as_wsh_command_wrapper, mdict=wsh_pattern)
