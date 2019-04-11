import argparse
import os.path
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(func=parser.print_help)

    parser.add_argument(
        '--python-binary',
    )
    parser.add_argument(
        '--target-name',
    )
    parser.add_argument(
        '--version',
    )

    args = parser.parse_args()

    path = os.path.dirname(args.python_binary)
    _, extension = os.path.splitext(args.python_binary)
    version = args.version.split('.')

    for i in range(len(version)):
        version_text = '.'.join(version[:i + 1])
        target = os.path.join(
            path,
            args.target_name + version_text + extension,
        )

        print('copying: {!r} -> {!r}'.format(
            args.python_binary,
            target,
        ))
        shutil.copy(args.python_binary, target)


sys.exit(main())
