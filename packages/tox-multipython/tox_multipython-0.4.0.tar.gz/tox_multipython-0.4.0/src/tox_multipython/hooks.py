from __future__ import print_function
import logging
import os

import pluggy

from virtualenv_multipython.tag import match_tag, get_tag_expected_command, get_tag_path

# tox version

import tox

TOX3 = tox.__version__.startswith('3.')
TOX4 = tox.__version__.startswith('4.')

if TOX4:
    from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner


# type checking

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # ruff: noqa: F401 = Optional is actually used for typing below
    from typing import List, Optional

    from tox.tox_env.register import ToxEnvRegister


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

impl = pluggy.HookimplMarker('tox')


if TOX3:

    @impl
    def tox_get_python_executable(envconfig):  # type: ignore
        """Return python executable for the given python base name."""
        if DEBUG:
            debug('Looking for executable based on: {}'.format(envconfig.__dict__))

        requests = [envconfig.basepython] + envconfig.envname.split('-')
        path = get_python_path(requests)

        if path:
            return path


if TOX4:

    class MultiPythonRunner(VirtualEnvRunner):
        @staticmethod
        def id():  # type: () -> str
            return 'multipython'

        @classmethod
        def extract_base_python(cls, env_name):  # type: (str) -> Optional[str]
            candidates = [f for f in env_name.split() if match_tag(f)]
            if len(candidates) >= 2:
                raise ValueError('conflicting factors in "{}"'.format(env_name))
            elif len(candidates) == 1:
                path = get_python_path(candidates)
                if path:
                    return path
                return get_tag_expected_command(candidates[0])
            return None

    @impl
    def tox_register_tox_env(register):  # type: (ToxEnvRegister) -> None
        register.add_run_env(MultiPythonRunner)
        register.default_env_runner = MultiPythonRunner.id()
        if DEBUG:
            debug('Registered MultiPythonRunner environment type')


# shared functionality


def get_python_path(requests):  # type: (List[str]) -> Optional[str]
    if DEBUG:
        debug('Looking for tag in candidates: {}'.format(requests))
    path = None

    for python in requests:
        if match_tag(python):
            if DEBUG:
                debug('Matched multipython tag: {}'.format(python))
            try:
                path = get_tag_path(python)
            except Exception:
                if DEBUG:
                    exception('Failed to determine path for tag "{}"'.format(python))
            if path and os.path.exists(path):
                break

    if DEBUG:
        if path:
            debug('Found Python executable: {}'.format(path))
        else:
            debug('Failed to propose Python executable')
    return path
