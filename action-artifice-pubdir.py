#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import SimpleHTTPServer
import SocketServer

import posixpath
import argparse
import urllib
import os
import socket,errno

from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer


class RootedHTTPServer(HTTPServer):

    def __init__(self, base_path, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.RequestHandlerClass.base_path = base_path


class RootedHTTPRequestHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self.base_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path


def startServer(HandlerClass=RootedHTTPRequestHandler, ServerClass=RootedHTTPServer):

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default=8300, type=int)
    parser.add_argument('--dir', '-d', default=os.getcwd()+'/public', type=str)
    args = parser.parse_args()

    server_address = ('', args.port)

    httpd = None

    try:
        httpd = ServerClass(args.dir, server_address, HandlerClass)
    except socket.error as error:
        if error.errno == errno.EADDRINUSE:
            print "[Artifice Pubdir]: " + os.strerror(error.errno)
            return None
        else:
            raise

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

if __name__ == '__main__':
    startServer()