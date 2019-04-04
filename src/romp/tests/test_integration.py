import subprocess
import sys


def test_all():
    subprocess.run(
        [
            sys.executable,
            '-m', 'romp',
            '--command', 'python -c "import sys; print(sys.version)"',
            '--environments', 'Linux-3.7-64|macOS-3.5-64|Windows-3.4-32',
            # ENVVAR '--personal-access-token', '',
            # ENVVAR '--build-request-url', '',
            # ENVVAR '--username', '',
            # default '--check-period', '',
            # ENVVAR '--source-branch, '',
            # ENVVAR '--definition-id', '',
            # skip '--archive', '',
            # skip '--artifact', '',
        ],
        check=True,
    )
