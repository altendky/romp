import json
import os
import sys


vm_image = {
    'Linux': 'ubuntu-16.04',
    'macOS': 'macOS-10.13',
    'Windows': 'vs2017-win2016',
}


architecture = {
    32: 'x86',
    64: 'x64',
}


class Environment:
    def __init__(self, platform, version, architecture):
        self.platform = platform
        self.vm_image = vm_image[platform]
        self.version = version
        self.architecture = architecture

    @classmethod
    def from_string(cls, environment_string):
        platform, version, bit_width = environment_string.split('-')
        return cls(
            platform=platform,
            version=version,
            architecture=architecture[int(bit_width)]
        )

    def to_matrix_entry(self):
        return (
            '{platform} {version} {architecture}'.format(
                platform=self.platform,
                version=self.version,
                architecture=self.architecture,
            ),
            {
                'platform': self.platform,
                'vmImage': self.vm_image,
                'versionSpec': self.version,
                'architecture': self.architecture,
            }
        )


def main():
    environments = os.environ['ROMP_ENVIRONMENTS']

    environments = [
        Environment.from_string(environment_string=environment)
        for environment in environments.split('|')
    ]

    matrix_entries = dict(
        environment.to_matrix_entry()
        for environment in environments
    )

    json_matrix = json.dumps(matrix_entries)

    command = (
        '##vso[task.setVariable variable=JobsToRun;isOutput=True]'
        + json_matrix
    )

    print(command.lstrip('#'))
    print(command)


if __name__ == '__main__':
    sys.exit(main())
