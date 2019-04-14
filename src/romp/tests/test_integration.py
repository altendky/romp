import subprocess
import sys


def test_all():
    subprocess.check_call(
        [
            sys.executable,
            '-m', 'romp',
            '--command', 'python -c "import sys; print(sys.version)"',
            '--interpreter', 'CPython',
            '--version', '3.7',
            '--architecture', '64',
            '--exclude', 'Windows', 'CPython', '3.7', '64',
            '--include', 'Linux', 'PyPy', '3.5', '64',
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
