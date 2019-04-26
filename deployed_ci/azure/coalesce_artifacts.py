import argparse
import glob
import os.path
import sys
import tarfile


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(func=parser.print_help)

    parser.add_argument(
        '--source-directory',
    )

    parser.add_argument(
        '--target'
    )

    args = parser.parse_args()

    artifact_archives = glob.glob(
        os.path.join(args.source_directory, 'artifacts.*.tar.gz'),
    )

    with tarfile.open(name=args.target, mode='w:gz') as target:
        for artifact_archive in artifact_archives:
            with tarfile.open(name=artifact_archive, mode='r:gz') as source:
                for info in source.getmembers():
                    target.addfile(info, source.extractfile(info))


if __name__ == '__main__':
    sys.exit(main())
