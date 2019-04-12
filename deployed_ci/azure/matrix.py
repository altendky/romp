import collections
import json
import os
import sys


vm_images = collections.OrderedDict((
    ('Linux', 'ubuntu-16.04'),
    ('macOS', 'macOS-10.13'),
    ('Windows', 'vs2017-win2016'),
))


interpreters = collections.OrderedDict((
    ('CPython', 'CPython'),
    ('PyPy', 'PyPy'),
))

versions = {
    'CPython': ('2.7', '3.4', '3.5', '3.6', '3.7'),
    'PyPy': ('2.7', '3.5'),
}

architectures = collections.OrderedDict((
    (32, 'x86'),
    (64, 'x64'),
))

urls = collections.OrderedDict((
    (('Linux', 'PyPy', '2.7', 'x64'), 'https://bitbucket.org/pypy/pypy/downloads/pypy2.7-v7.0.0-linux64.tar.bz2'),
    (('Linux', 'PyPy', '3.5', 'x64'), 'https://bitbucket.org/pypy/pypy/downloads/pypy3.5-v7.0.0-linux64.tar.bz2'),
    (('macOS', 'PyPy', '2.7', 'x64'), 'https://bitbucket.org/pypy/pypy/downloads/pypy2.7-v7.0.0-osx64.tar.bz2'),
    (('macOS', 'PyPy', '3.5', 'x64'), 'https://bitbucket.org/pypy/pypy/downloads/pypy3.5-v7.0.0-osx64.tar.bz2'),
    (('Windows', 'PyPy', '2.7', 'x86'), 'https://bitbucket.org/pypy/pypy/downloads/pypy2.7-v7.0.0-win32.zip'),
    (('Windows', 'PyPy', '3.5', 'x86'), 'https://bitbucket.org/pypy/pypy/downloads/pypy3.5-v7.0.0-win32.zip'),
))

extracters = {
    'Linux': 'tar -xvf',
    'macOS': 'tar -xvf',
    'Windows': 'unzip',
}


class Environment:
    def __init__(self, platform, interpreter, version, architecture):
        self.platform = platform
        self.vm_image = vm_images[platform]
        self.interpreter = interpreter
        self.version = version
        self.architecture = architecture

    @classmethod
    def from_string(cls, environment_string):
        platform, interpreter, version, bit_width = (
            environment_string.split('-')
        )
        return cls(
            platform=platform,
            interpreter=interpreter,
            version=version,
            architecture=architectures[int(bit_width)]
        )

    def python_binary(self):
        if self.interpreter == 'CPython':
            binary = 'python'
        elif self.interpreter == 'PyPy':
            binary = 'pypy'

            if self.version.startswith('3'):
                binary += '3'

        if self.platform == 'Windows':
            binary += '.exe'

        return binary

    def tox_env(self):
        env = 'py'
        if self.interpreter == 'PyPy':
            env += 'py'

        env += self.version.replace('.', '')

        return env

    def to_matrix_entry(self):
        return (
            '{platform} {interpreter} {version} {architecture}'.format(
                platform=self.platform,
                interpreter=self.interpreter,
                version=self.version,
                architecture=self.architecture,
            ),
            {
                'platform': self.platform,
                'interpreter': self.interpreter,
                'vmImage': self.vm_image,
                'versionSpec': self.version,
                'architecture': self.architecture,
                'python_binary': self.python_binary(),
                'python_url': urls.get((
                    self.platform,
                    self.interpreter,
                    self.version,
                    self.architecture,
                ), ''),
                'extracter': extracters[self.platform],
                'TOXENV': self.tox_env(),
            },
        )


def main():
    environments = os.environ['ROMP_ENVIRONMENTS']

    environments = [
        Environment.from_string(environment_string=environment)
        for environment in environments.split('|')
    ]

    matrix_entries = collections.OrderedDict(
        environment.to_matrix_entry()
        for environment in environments
    )

    json_matrix = json.dumps(matrix_entries)

    command = (
        '##vso[task.setVariable variable=JobsToRun;isOutput=True]'
        + json_matrix
    )

    print(command.lstrip('#'))
    print(json.dumps(matrix_entries, indent=4))
    print(command)


if __name__ == '__main__':
    sys.exit(main())
