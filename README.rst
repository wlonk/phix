====
phix
====

author: Kit La Touche

Overview
--------

Make writing your Sphinx docs a little easier.

This is a command line tool to build and serve your Sphinx docs. Run
this from inside the directory where your Sphinx Makefile is, and it
will build your docs on any ``*.rst`` change, and serve them at
``http://localhost:8000``.

Options:

*  ``-t``, ``--type``: the make subcommand to run, and the ``_build``
   subdirectory to serve. Defaults to ``dirhtml``.
*  ``-p``, ``--port``: the port to serve the docs on. Defaults to
   ``8000``.
*  ``--help``: Show the help.
*  ``--version``: Show the version.

Installation / Usage
--------------------

To install use pip::

    $ pip install phix


Or clone the repo::

    $ git clone https://github.com/wlonk/phix.git
    $ python setup.py install

Then run it::

   $ phix

Contributing
------------

Fork it, make a PR, and I'll take a look!
