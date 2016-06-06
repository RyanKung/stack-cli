# coding: utf8

import os

__all__ = ['get_env']


def get_env() -> str:
    '''
    Get virtualenv path
    '''
    return os.environ.get('VIRTUAL_ENV', '')
