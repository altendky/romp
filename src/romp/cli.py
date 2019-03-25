import functools
import getpass

import click

import romp._core


@functools.wraps(click.option)
def create_option(*args, envvar, help, show_default=True, **kwargs):
    help = help.strip()
    help += ' (${})'.format(envvar)
    help = help.strip()

    return click.option(
        *args,
        envvar=envvar,
        help=help,
        show_default=show_default,
        **kwargs,
    )


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
            "python -c 'import sys; print(sys.version); print(sys.platform)'",
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


@click.command()
@create_personal_access_token_option()
@create_build_request_url_option()
@create_command_option()
@create_username_option()
@create_environments_option()
@create_check_period_option()
@create_source_branch_option()
@create_definition_id_option()
def main(
        personal_access_token,
        build_request_url,
        command,
        username,
        environments,
        check_period,
        source_branch,
        definition_id,
):
    archive_bytes = romp._core.make_remote_lock_archive()
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

    build.get_lock_build_artifact()
