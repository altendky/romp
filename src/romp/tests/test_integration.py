import os.path
import subprocess
import sys
import tarfile
import tempfile

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


def test_artifacts_coalesced():
    with tempfile.NamedTemporaryFile(delete=False) as temporary_file:
        temporary_file.close()
        artifact_archive_path = temporary_file.name

        command = '; '.join((
            'echo red > ${UUID}.txt',
            (
                'python -c'
                """ 'import sys; print(".".join(str(v) for v in sys.version_info[:2]))'"""
                ' >> ${UUID}.txt'
            )
        ))

        subprocess.check_call(
            [
                sys.executable,
                '-m', 'romp',
                '--command', command,
                '--platform', 'Linux',
                '--interpreter', 'CPython',
                '--version', '3.6',
                '--version', '3.7',
                '--architecture', 'x86_64',
                '--artifact-paths', '*.txt',
                '--artifact', artifact_archive_path,
            ],
        )

        with tarfile.open(name=artifact_archive_path, mode='r:gz') as tar:
            contents = {
                tuple(tar.extractfile(info).read().strip().splitlines())
                for info in tar.getmembers()
            }

    assert contents == {
        (b'red', b'3.7'),
        (b'red', b'3.6'),
    }
