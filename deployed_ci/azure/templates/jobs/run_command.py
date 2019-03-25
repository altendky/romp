import sys

import attr
import yaml


@attr.s
class Platform:
    name = attr.ib()
    vm_image = attr.ib()


@attr.s
class PythonVersion:
    version = attr.ib()
    architecture = attr.ib()

    def version_string(self):
        return '.'.join(str(x) for x in self.version)

    def to_string(self):
        return '{}-{}'.format(self.version_string(), self.architecture)


def display_name(platform, python_version):
    return '{}: Python {}'.format(
        platform.name,
        python_version.to_string(),
    )


def environment_string(platform, python_version):
    return '{}_{}'.format(
        platform.name,
        python_version.to_string(),
    )


def job_name(platform, python_version):
    return '{}_Python_{}'.format(
        platform.name,
        python_version.to_string(),
    ).lower().replace('.', '_').replace('-', '_')


@attr.s
class MatrixJob:
    platform = attr.ib()
    python_version = attr.ib()

    def job_name(self):
        return job_name(
            platform=self.platform,
            python_version=self.python_version,
        )

    def display_name(self):
        return display_name(
            platform=self.platform,
            python_version=self.python_version,
        )

    def environment_string(self):
        return environment_string(
            platform=self.platform,
            python_version=self.python_version,
        )

    def to_dict(self):
        return {
            # "${{{{ if contains(variables.ROMP_ENVIRONMENTS, '|{}') }}}}".format(self.environment_string()): {
            # "${{{{ if contains(dependencies.ROMP_ENVIRONMENTS['v.v'], '|{}') }}}}".format(self.environment_string()): {
                self.job_name(): {
                    'platform': self.platform.name,
                    'vmImage': self.platform.vm_image,
                    'versionSpec': self.python_version.version_string(),
                    'architecture': self.python_version.architecture,
                    'displayName': self.display_name(),
                    'job': self.job_name(),
                    'environment': self.environment_string(),
                },
            # },
        }


@attr.s
class Job:
    platform = attr.ib()
    python_version = attr.ib()
    depends_on = attr.ib()

    def display_name(self):
        return display_name(
            platform=self.platform,
            python_version=self.python_version,
        )

    def environment_string(self):
        return environment_string(
            platform=self.platform,
            python_version=self.python_version,
        )

    def job_name(self):
        return job_name(
            platform=self.platform,
            python_version=self.python_version,
        )

    def to_dict(self):
        use_python_task = UsePythonTask(python_version=self.python_version)

        return {
            'job': self.job_name(),
            'condition': "contains(dependencies.ROMP_ENVIRONMENTS.outputs['setvarStep.myOutputVar'], '{}')".format('|' + self.environment_string()),
            'dependsOn': self.depends_on,
            'displayName': self.display_name(),
            'pool': {
                'vmImage': self.platform.vm_image,
            },
            'steps': [
                use_python_task.to_dict(),
                {
                    'template': '../steps/in_archive_from_artifact.yml',
                },
                {
                    'bash': '${ROMP_COMMAND}',
                    'displayName': 'Run command',
                },
                {
                    'task': 'CopyFiles@2',
                    'inputs': {
                        'contents': 'requirements/*.txt',
                        'targetFolder': '$(Build.ArtifactStagingDirectory)',
                    },
                },
                {
                    'task': 'PublishBuildArtifacts@1',
                    'inputs': {
                        'artifactName': 'results',
                        'pathToPublish': '$(Build.ArtifactStagingDirectory)',
                    },
                },
            ],
        }


@attr.s
class UsePythonTask:
    python_version = attr.ib()

    def to_dict(self):
        return {
            'task': 'UsePythonVersion@0',
            'inputs': {
                'architecture': self.python_version.architecture,
                'versionSpec': self.python_version.version_string(),
            },
        }


def main():
    platforms = [
        Platform(name='Linux', vm_image='ubuntu-16.04'),
        Platform(name='macOS', vm_image='macOS-10.13'),
        Platform(name='Windows', vm_image='vs2017-win2016'),
    ]

    python_versions = [
        PythonVersion(version=version, architecture=architecture)
        for version in [(3, 6), (3, 7)]
        for architecture in ['x64']
    ]

    job = Job(
        platform=platforms[0],
        python_version=python_versions[0],
        depends_on='ROMP_ENVIRONMENTS',
    )

    jobs = [
        Job(
            platform=platform,
            python_version=python_version,
            depends_on='ROMP_ENVIRONMENTS',
        )
        for platform in platforms
        for python_version in python_versions
    ]

    serialized_jobs = {
        'jobs': [
            job.to_dict()
            for job in jobs
        ],
    }

    yaml.safe_dump(
        serialized_jobs,
        stream=sys.stdout,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    )

    return

    matrix_jobs = [

        MatrixJob(platform=platform, python_version=python_version)
        for platform in platforms
        for python_version in python_versions
    ]

    matrix_value = {}

    for job in matrix_jobs:
        matrix_value.update(job.to_dict())

    strategy = {
        'strategy': {
            # 'matrix': dict(job.to_list() for job in matrix_jobs),
            'matrix': matrix_value,
        },
    }

    jobs = {
        'jobs': [
            {
                'job': '${{ parameters.job }}',
                'displayName': '${{ parameters.displayName }}',
                'dependsOn': 'ROMP_ENVIRONMENTS',
                'pool': {
                    'vmImage': '${{ parameters.vmImage }}',
                },
                'condition': "contains(dependencies.ROMP_ENVIRONMENTS.outputs['v.v'], '|${{ parameters.environment }}')",
                **strategy,
                'steps': [
                    {
                        'task': 'UsePythonVersion@0',
                        'inputs': {
                            'versionSpec': '${{ parameters.versionSpec }}',
                            'architecture': '${{ parameters.architecture }}',
                        },
                    },
                    {
                        'template': '../steps/in_archive_from_artifact.yml',
                    },
                    {
                        'bash': '${{ parameters.command }}',
                        'displayName': 'Run Command',
                    },
                    {
                        'task': 'CopyFiles@2',
                        'inputs': {
                            'contents': 'requirements/*.txt',
                            'targetFolder': '$(Build.ArtifactStagingDirectory)',
                        },
                    },
                    {
                        'task': 'PublishBuildArtifacts@1',
                        'inputs': {
                            'pathToPublish': '$(Build.ArtifactStagingDirectory)',
                            'artifactName': 'results',
                        },
                    },
                ],
            },
        ],
    }

    yaml.safe_dump(strategy, stream=sys.stdout)


if __name__ == '__main__':
    sys.exit(main())
