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
    def __init__(self, type_, cwd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_ = type_
        self.cwd = cwd

    def on_any_event(self, event):
        subprocess.run(['make', self.type_], cwd=self.cwd)


class RootedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    @property
    def root_dir(self):
        return '{cwd}/_build/{type_}'.format(
            cwd=self.cwd,
            type_=self.type_,
        )

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
@click.option('-r', '--root', 'root', default='.')
def main(type_, port, root):
    patterns = [
        '*.rst',
        os.path.abspath(os.path.join(root, 'conf.py')),
    ]
    ignore_patterns = ['_build/*']
    event_handler = SphinxEventHandler(
        type_,
        root,
        patterns=patterns,
        ignore_patterns=ignore_patterns,
    )

    observer = Observer()
    observer.schedule(event_handler, root, recursive=True)
    observer.start()

    handler = RootedHTTPRequestHandler
    handler.cwd = root
    handler.type_ = type_

    server = socketserver.TCPServer(("", port), handler)

    click.echo(click.style(
        "Listening for changes to {}.".format(
            ", ".join(patterns)
        ),
        bold=True,
        fg='green',
    ))
    click.echo(click.style(
        "Serving from _build/{} on http://localhost:{}...".format(
            type_,
            port,
        ),
        bold=True,
        fg='green',
    ))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo(click.style("Exiting..."))
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
