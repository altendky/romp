import functools
import getpass

import click

import romp._core


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
    return create_option(
        '--username',
        default=getpass.getuser(),
        envvar=envvar,
        help='Username for build URL authentication',
    )


def create_environments_option(
        envvar='ROMP_ENVIRONMENTS',
):
    return create_option(
        '--environments',
        default='|Linux-3.6-x64|macOS-3.6-x64',
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
):
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
        environments=environments,
        source_branch=source_branch,
        definition_id=definition_id,
    )

    build.wait_for_lock_build(check_period=check_period)

    if artifact is not None:
        build.get_lock_build_artifact(artifact_file=artifact)
