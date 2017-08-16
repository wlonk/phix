#!/usr/bin/env python3

import os
import urllib
import posixpath
import http.server
import socketserver
import subprocess

import click

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class SphinxEventHandler(PatternMatchingEventHandler):
    def __init__(self, type_, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_ = type_

    def on_any_event(self, event):
        subprocess.run(['make', self.type_])


class RootedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    @property
    def root_dir(self):
        return '_build/{type_}'.format(type_=self.type_)

    def apply_root(self, path):
        return posixpath.join(
            self.root_dir,
            posixpath.relpath(path, '/'),
        )

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        path = self.apply_root(path)
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
        path = self.apply_root(path)
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


@click.command()
@click.version_option()
@click.option('-t', '--type', 'type_', default='dirhtml')
@click.option('-p', '--port', 'port', default=8000)
def main(type_, port):
    event_handler = SphinxEventHandler(
        type_,
        patterns=['*.rst'],
        ignore_patterns=['_build/*'],
    )

    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()

    handler = RootedHTTPRequestHandler
    handler.type_ = type_

    server = socketserver.TCPServer(("", port), handler)

    try:
        server.serve_forever()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
