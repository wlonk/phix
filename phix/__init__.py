#!/usr/bin/env python3

import os
import urllib
import posixpath
import http.server
import socketserver
import subprocess

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


# TODO: make these configurable
TYPE = 'dirhtml'
PORT = 8000


class SphinxEventHandler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        subprocess.run(['make', TYPE])


class RootedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    root_dir = f'_build/{TYPE}'

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        path = self.root_dir + path
        super().list_directory(path)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing.
        # Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        # This line added to parent class:
        path = self.root_dir + path
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory
                # name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


def main():
    event_handler = SphinxEventHandler(
        patterns=['*.rst'],
        ignore_patterns=['_build/*'],
    )

    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()

    handler = RootedHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()
