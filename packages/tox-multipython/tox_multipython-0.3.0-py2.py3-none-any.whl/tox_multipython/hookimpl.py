from __future__ import print_function
import logging
import os

import pluggy
from virtualenv_multipython.tag import match_tag, get_tag_path


# tox version

import tox

TOX3 = tox.__version__.startswith('3.')


# type checking

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # ruff: noqa: F401 = Union is actually used for typing below
    from typing import Union


# debug logging

DEBUG = bool(os.environ.get('MULTIPYTHON_DEBUG', False))
if DEBUG:
    try:
        from loguru import logger
    except ImportError:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging  # type: ignore

    debug = logger.debug
    exception = logger.exception


# hooks

hookimpl = pluggy.HookimplMarker('tox')


if TOX3:

    @hookimpl
    def tox_get_python_executable(envconfig):  # type: ignore
        """Return a python executable for the given python base name."""
        if DEBUG:
            debug('Requested Python executable: {}'.format(envconfig.__dict__))
        path = None
        tag = envconfig.envname

        if match_tag(tag):
            if DEBUG:
                debug('Candidate tag: {}'.format(tag))
            try:
                path = get_tag_path(tag)
            except Exception:
                if DEBUG:
                    exception('Failed to determine path for tag "{}"'.format(tag))

        if DEBUG:
            if path:
                debug('Found Python executable: {}'.format(path))
            else:
                debug('Failed to propose Python executable')
        return path
