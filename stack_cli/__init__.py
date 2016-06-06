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
from .decorators import as_command_wrapper
from argparse import ArgumentParser

__all__ = ['__version__', 'parser', 'as_command']

__version__ = '0.1'
parser = ArgumentParser(description='Stack-cli - The Python Tool Stack-cli')
parser.usage = 'stack [-h]'
subparsers = parser.add_subparsers(title='Available options:', help='Run `stack COMMAND -h` to get help')
as_command = partial(as_command_wrapper, parser=subparsers)
