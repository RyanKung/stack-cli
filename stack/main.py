# coding: utf8
import os
import sys
import sysconfig
from functools import partial
from runpy import run_path
from typing import Callable
from . import parser, subparsers, as_command, wsh_command, __version__, pattern, wsh_pattern
from .utils import get_env
from .decorators import ignore
from .wsh.client import main as client
from .wsh.server import main as server


__all__ = ['router', 'main']


@partial(ignore, res={})
def parse_stackfile(stackfile: str) -> dict:
    if os.path.exists(stackfile):
        tasks = run_path(stackfile)
        return tasks
    return {}


def update_stackfile(pattern: dict, stackfile: str='stackfile.py') -> dict:
    '''
    Check wheather the stackfile exist,
    If exist, update the pattern dict with tasks contained in the stack file
    '''
    pattern.update(parse_stackfile(stackfile))
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


@wsh_command
@as_command
def version(args=None) -> None:
    '''
    Show stack-cli version
    '''
    print(__version__)


@wsh_command
def commands() -> str:
    return ','.join(wsh_pattern.keys())


@as_command
def wsh(args) -> None:
    '''
    Run websocket based server
    @argument --server, metavar=server, default=1, help=run as server
    @argument --client, metavar=client, help=run as client
    @argument --host, metavar=host, default=127.0.0.1, help=host
    @argument --port, metavar=port, default=8964, help=port
    @argument --project, metavar=project, default=default, help=the project path
    @argument --daemon, default=1, help=run server with daemo mode
    '''
    def runserver():
        return server(host=args.host, port=args.port, pattern=wsh_pattern, project=args.project)

    if args.project != 'default':
        parse_stackfile('%s/stackfile.py' % args.project)
    if args.client:
        return client(host=args.host, port=args.port, project=args.project)
    if args.server:
        if bool(int(args.daemon)):
            pid = os.fork()
            if not pid:
                os.system('echo %s > stack-daemon.pid' % os.getpid())
                return runserver()
            else:
                sys.exit(1)
        else:
            return runserver()


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


def main(argv=sys.argv,
         pattern=pattern,
         allow=('stackfile', 'execfile'),
         stackfile='stackfile.py') -> None:
    '''
    @pattern: dict of registed fns
    @stackfile: the path of stackfile
    '''
    if 'stackfile' in allow:
        update_stackfile(pattern, stackfile=stackfile)
    if 'execfile' in allow and pattern.get('execfile', True):
        update_execfile(pattern, prefix=get_env())

    return router(pattern, argv)

if __name__ == '__main__':
    main()
