import getpass

import click

import romp._core


@click.command()
@click.option(
    '--personal-access-token',
    '--pat',
    'personal_access_token',
    prompt='Personal Access Token',
    hide_input=True,
)
@click.option(
    '--build-request-url',
    default=(
        'https://dev.azure.com'
        '/altendky/romp/_apis/build/builds?api-version=5.0'
    )
)
@click.option(
    '--command',
    default=(
        "python -c 'import sys; print(sys.version); print(sys.platform)'"
    ),
)
@click.option(
    '--username',
    default=getpass.getuser(),
)
@click.option(
    '--environments',
    default='|Linux-3.6-x64|macOS-3.6-x64',
)
@click.option(
    '--check-period',
    default=15,
)
@click.option(
    '--source-branch',
    default='develop',
)
@click.option(
    '--definition-id',
    default=3,
)
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
