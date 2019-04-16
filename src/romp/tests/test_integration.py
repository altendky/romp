import os.path
import subprocess
import sys


here = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))


def test_all():
    command_name = 'print_sys_version.py'
    command_path = os.path.join(here, command_name)

    subprocess.check_call(
        [
            sys.executable,
            '-m', 'romp',
            '--command', 'python {}'.format(command_name),
            '--interpreter', 'CPython',
            '--version', '3.7',
            '--architecture', '64',
            '--exclude', 'Windows', 'CPython', '3.7', '64',
            '--include', 'Linux', 'PyPy', '3.5', '64',
            '--archive-paths-root', here,
            command_path,
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
