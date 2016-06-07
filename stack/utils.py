# coding: utf8

import os
import sysconfig

__all__ = ['warn', 'info', 'error', 'get_env', 'check_exec']


def warn(s: str):
    '''
    Show warning with yellow color
    '''
    print("\033[93m Warning: {}\033[00m" .format(s))


def info(s: str):
    '''
    Show info message with yellow color
    '''
    print("\033[92m Info: {}\033[00m" .format(s))


def error(s: str):
    '''
    show error message with red color
    '''
    print("\033[91m Error: {}\033[00m" .format(s))


def get_env() -> str:
    '''
    Get virtualenv path
    '''
    env = os.environ.get('VIRTUAL_ENV', '')
    if env:
        return env + '/bin/'
    else:
        return ''


def check_exec(e: str) -> bool:
    '''
    Check the exec file is exist
    '''
    return e in os.listdir(sysconfig.get_path('scripts'))
