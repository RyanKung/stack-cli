# coding: utf8
import os
import sys
from runpy import run_path
from typing import Callable
from . import parser, as_command

__all__ = ['update_stackfile', 'router', 'main']


def update_stackfile(pattern: dict) -> dict:
    '''
    Check wheather the stackfile exist,
    If exist, update the pattern dict with tasks contained in the stack file
    '''
    if os.path.exists('./stackfile.py'):
        tasks = run_path('stackfile.py')
        pattern.update(tasks)
        return pattern
    return pattern


@as_command
def fab(args) -> None:
    '''
    Drop to Fabric
    '''
    os.system('fab %s' % ' '.join(sys.argv[2:]))


def router(pattern: dict, argv: list) -> Callable:
    '''
    Match function from funtion_hash_dict
    {
       'fn_1': fn_1()
    }
    '''
    args, unknown = parser.parse_known_args()
    if not len(argv) > 1:
        print(parser.format_help())
        return
    return pattern.get(argv[1], fab)(args)


def main(argv: list=sys.argv) -> None:
    pattern = {'fab': fab}
    return router(update_stackfile(pattern), argv)

if __name__ == '__main__':
    main()
