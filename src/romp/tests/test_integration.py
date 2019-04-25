import os.path
import subprocess
import sys

import pytest


here = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))


def test_all():
    command_name = 'print_sys_version.py'
    command_path = os.path.join(here, command_name)

    subprocess.check_call(
        [
            sys.executable,
            '-m', 'romp',
            '--command', 'python {}'.format(command_name),
            '--interpreter', 'cpYThon',
            '--version', '3.7',
            '--architecture', 'x86_64',
            '--exclude', 'Windows', 'CPython', '3.7', 'x86_64',
            '--include', 'Linux', 'PyPy', '3.5', 'x86_64',
            '--archive-paths-root', here,
            '--archive-path', command_path,
            # '--environments', '|'.join((
            #     'Linux-CPython-3.7-64',
            #     'macOS-CPython-3.5-64',
            #     'Linux-PyPy-3.5-64',
            # )),
            # ENVVAR '--personal-access-token', '',
            # ENVVAR '--build-request-url', '',
            # ENVVAR '--username', '',
            # default '--check-period', '',
            # ENVVAR '--source-branch, '',
            # ENVVAR '--definition-id', '',
            # skip '--archive', '',
            # skip '--artifact', '',
        ],
    )


def test_failure_fails():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            [
                sys.executable,
                '-m', 'romp',
                '--command', 'false',
                '--platform', 'Linux',
                '--interpreter', 'CPython',
                '--version', '3.7',
                '--architecture', 'x86_64',
            ],
        )
