# coding: utf8

import argparse
from .client import main as client
from .server import main as server

parser = argparse.ArgumentParser(description='wsh')
subparsers = parser.add_subparsers(title='Available options:', help='Run `wsh COMMAND -h` to get help')
subparsers.add_argument('--server', metavar='server', help='run as server')
subparsers.add_argument('--client', metavar='client', help='run as client')
subparsers.add_argument('--host', metavar='host')
subparsers.add_argument('--port', metavar='port')


def main(args=parser.parse_args()):
    if args.server:
        return server(host=args.host, port=args.port)
    if args.client:
        return client(host=args.host, port=args.port)
