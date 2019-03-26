import os.path
import subprocess
import sys


def publish(force=False):
    no_tag = subprocess.call(
        [
            'git',
            'describe',
            '--tags',
            '--candidates', '0',
        ],
        timeout=15,
    )

    if no_tag:
        if force:
            print('Not on a tag, but --force...')
        else:
            print('Not on a tag, doing nothing.')
            return
    else:
        print('On a tag.')

    print('Uploading to PyPI.')

    subprocess.check_call(
        [
            os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'twine'),
            'upload',
            os.path.join(os.path.dirname(__file__), 'dist', '*'),
        ],
        timeout=45,
    )


if __name__ == '__main__':
    sys.exit(publish())
