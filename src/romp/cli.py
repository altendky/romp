import functools
import getpass
import json

import click

import romp._core
import romp._matrix


@functools.wraps(click.option)
def create_option(*args, **kwargs):
    kwargs['help'] = kwargs['help'].strip()
    kwargs['help'] += ' (${})'.format(kwargs['envvar'])
    kwargs['help'] = kwargs['help'].strip()

    kwargs.setdefault('show_default', True)

    return click.option(*args, **kwargs)


def create_personal_access_token_option(
        envvar='ROMP_PERSONAL_ACCESS_TOKEN',
):
    return create_option(
        '--personal-access-token',
        '--pat',
        'personal_access_token',
        envvar=envvar,
        hide_input=True,
        prompt='Personal Access Token',
        help='A personal access token (PAT) with rights to initiate builds',
    )


def create_build_request_url_option(
        envvar='ROMP_BUILD_REQUEST_URL',
):
    return create_option(
        '--build-request-url',
        default=(
                'https://dev.azure.com'
                '/altendky/romp/_apis/build/builds?api-version=5.0'
        ),
        envvar=envvar,
        help='The URL for submitting a build request',
    )


def create_command_option(
        envvar='ROMP_COMMAND',
):
    return create_option(
        '--command',
        default=(
            "python -c 'import sys; print(sys.version); print(sys.platform)'"
        ),
        envvar=envvar,
        help='The command to be run for each target',
    )


def create_username_option(
        envvar='ROMP_USERNAME',
):
    kwargs = {
        'envvar': envvar,
        'help': 'Username for build URL authentication',
    }

    try:
        kwargs['default'] = getpass.getuser()
    except ImportError:
        kwargs['required'] = True

    return create_option(
        '--username',
        **kwargs
    )


def create_environments_option(
        envvar='ROMP_ENVIRONMENTS',
):
    return create_option(
        '--environments',
        envvar=envvar,
        help='Targets to run on',
    )


def create_check_period_option(
        envvar='ROMP_CHECK_PERIOD',
):
    return create_option(
        '--check-period',
        default=15,
        envvar=envvar,
        help='The period used to poll the build for completion',
    )


def create_source_branch_option(
        envvar='ROMP_SOURCE_BRANCH',
):
    return create_option(
        '--source-branch',
        default='develop',
        envvar=envvar,
        help='The romp source branch to use for the build',
    )


def create_definition_id_option(
        envvar='ROMP_DEFINITION_ID',
):
    return create_option(
        '--definition-id',
        default=3,
        envvar=envvar,
        help='The definition id of the build to be triggered',
    )


def create_archive_option(
        envvar='ROMP_ARCHIVE',
):
    return create_option(
        '--archive',
        envvar=envvar,
        help='The archive to be uploaded to the build',
        type=click.File('rb'),
    )


def create_artifact_option(
        envvar='ROMP_ARTIFACT_PATH',
):
    return create_option(
        '--artifact',
        envvar=envvar,
        help='The path at which to save the resulting artifact',
        type=click.File('wb'),
    )


platforms_choice = click.Choice(
    choices=romp._matrix.all_platforms,
    case_sensitive=False,
)


def create_matrix_platforms_option(
        envvar='ROMP_MATRIX_PLATFORMS',
):
    return create_option(
        '--platform',
        'matrix_platforms',
        default=romp._matrix.all_platforms,
        envvar=envvar,
        help='Platforms to matrix across',
        multiple=True,
        type=platforms_choice,
    )


interpreters_choice = click.Choice(
    choices=romp._matrix.all_interpreters,
    case_sensitive=False,
)


def create_matrix_interpreters_option(
        envvar='ROMP_MATRIX_INTERPRETERS',
):
    return create_option(
        '--interpreter',
        'matrix_interpreters',
        default=romp._matrix.all_interpreters,
        envvar=envvar,
        help='Interpreters to matrix across',
        multiple=True,
        type=interpreters_choice,
    )


versions_choice = click.Choice(
    choices=romp._matrix.all_versions,
    case_sensitive=False,
)


def create_matrix_versions_option(
        envvar='ROMP_MATRIX_VERSIONS',
):
    return create_option(
        '--version',
        'matrix_versions',
        default=romp._matrix.all_versions,
        envvar=envvar,
        help='Versions to matrix across',
        multiple=True,
        type=versions_choice,
    )


all_architectures = [
    str(architecture)
    for architecture in romp._matrix.all_architectures
]


architectures_choice = click.Choice(
    choices=all_architectures,
    case_sensitive=False,
)


def create_matrix_architectures_option(
        envvar='ROMP_MATRIX_ARCHITECTURES',
):
    return create_option(
        '--architecture',
        'matrix_architectures',
        default=all_architectures,
        envvar=envvar,
        help='Architectures to matrix across',
        multiple=True,
        type=architectures_choice,
    )


def create_matrix_element_option(
        long,
        destination,
        envvar,
        help,
        multiple=True,
):
    return create_option(
        long,
        destination,
        envvar=envvar,
        help=help,
        multiple=multiple,
        type=(
            platforms_choice,
            interpreters_choice,
            versions_choice,
            architectures_choice
        ),
    )


def create_matrix_include_option(
        envvar='ROMP_MATRIX_INCLUDES',
):
    return create_matrix_element_option(
        long='--include',
        destination='matrix_includes',
        envvar=envvar,
        help='Complete environments to include in the matrix',
    )


def create_matrix_exclude_option(
        envvar='ROMP_MATRIX_EXCLUDES',
):
    return create_matrix_element_option(
        long='--exclude',
        destination='matrix_excludes',
        envvar=envvar,
        help='Complete environments to exclude from the matrix',
    )


@click.command()
@create_personal_access_token_option()
@create_build_request_url_option()
@create_command_option()
@create_username_option()
@create_environments_option()
@create_check_period_option()
@create_source_branch_option()
@create_definition_id_option()
@create_archive_option()
@create_artifact_option()
@create_matrix_platforms_option()
@create_matrix_interpreters_option()
@create_matrix_versions_option()
@create_matrix_architectures_option()
@create_matrix_include_option()
@create_matrix_exclude_option()
def main(
        personal_access_token,
        build_request_url,
        command,
        username,
        environments,
        check_period,
        source_branch,
        definition_id,
        archive,
        artifact,
        matrix_platforms,
        matrix_interpreters,
        matrix_versions,
        matrix_architectures,
        matrix_includes,
        matrix_excludes,
):
    matrix_specified = any(
        len(dimension) > 0
        for dimension in (
            matrix_platforms,
            matrix_interpreters,
            matrix_versions,
            matrix_architectures,
        )
    )

    if environments is not None and matrix_specified:
        # TODO: this isn't really nice, maybe drop environments all together?
        #       or maybe it turns into '--include Windows,CPython,3.7,6.4' etc?
        click.echo('Specify either an environments list or matrix parameters')
        return 1

    matrix_architectures = [int(a) for a in matrix_architectures]

    environments = romp._matrix.build_environments(
        platforms=matrix_platforms,
        interpreters=matrix_interpreters,
        versions=matrix_versions,
        architectures=matrix_architectures,
    )

    include_environments = [
        romp._matrix.Environment(
            platform=platform,
            interpreter=interpreter,
            version=version,
            architecture=int(architecture),
        )
        for platform, interpreter, version, architecture in matrix_includes
    ]

    exclude_environments = [
        romp._matrix.Environment(
            platform=platform,
            interpreter=interpreter,
            version=version,
            architecture=int(architecture),
        )
        for platform, interpreter, version, architecture in matrix_excludes
    ]

    environments = [
        environment
        for environment in environments + include_environments
        if environment not in exclude_environments
    ]

    environments_string = romp._matrix.string_from_environments(environments)

    archive_url = None
    if archive is not None:
        archive_bytes = archive.read()
        archive_url = romp._core.post_file(data=archive_bytes)

    print(archive_url)

    build = romp._core.request_remote_lock_build(
        archive_url=archive_url,
        username=username,
        personal_access_token=personal_access_token,
        build_request_url=build_request_url,
        command=command,
        environments=environments_string,
        source_branch=source_branch,
        definition_id=definition_id,
    )

    build.wait_for_lock_build(check_period=check_period)

    if artifact is not None:
        build.get_lock_build_artifact(artifact_file=artifact)
