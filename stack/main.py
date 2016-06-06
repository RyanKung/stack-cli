# coding: utf8
import os
import sys
import sysconfig
from functools import partial
from runpy import run_path
from typing import Callable
from . import parser, subparsers, as_command, __version__
from .utils import get_env

__all__ = ['router', 'main']


def update_stackfile(pattern: dict, stackfile: str='stackfile.py') -> dict:
    '''
    Check wheather the stackfile exist,
    If exist, update the pattern dict with tasks contained in the stack file
    '''
    if os.path.exists(stackfile):
        tasks = run_path(stackfile)
        pattern.update(tasks)
        return pattern
    return pattern


def update_execfile(pattern: dict, prefix: str='') -> dict:
    '''
    Check and add execable files to the stackfile commandline
    '''
    def get_execs() -> list:
        def exec_filter(x):
            '''
            >>> assert exec_filter('abc') == True
            >>> assert exec_filter('adfa-') == False
            >>> assert exec_filter('abc.py') == False
            '''
            for i in ['-', '.py']:
                if i in x:
                    return i not in x
            else:
                return True

        return tuple(filter(exec_filter, os.listdir(sysconfig.get_path('scripts'))))

    def gen_command(e: str, args: list):
        return os.system(prefix + e + ' %s' % ' '.join(sys.argv[2:]))

    exec_fns = {e: partial(gen_command, e) for e in get_execs()}
    tuple(map(lambda x: subparsers.add_parser(x, help='Run %s' % x), get_execs()))
    pattern.update(exec_fns)
    return pattern


@as_command
def fab(args) -> None:
    '''
    Drop to Fabric
    '''
    prefix = get_env()
    os.system(prefix + 'fab %s' % ' '.join(sys.argv[2:]))


@as_command
def version(args) -> None:
    '''
    Show stack-cli version
    '''
    print(__version__)


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


def main(argv: list=sys.argv,
         pattern: dict={'fab': fab, 'version': version},
         allow: tuple=('stackfile', 'execfile'),
         stackfile: str='stackfile.py') -> None:
    '''
    @pattern: dict of registed fns
    @stackfile: the path of stackfile
    '''
    if 'stackfile' in allow:
        update_stackfile(pattern, stackfile=stackfile)
    if 'execfile' in allow:
        update_execfile(pattern, prefix=get_env())

    return router(pattern, argv)

if __name__ == '__main__':
    main()
