import collections
import functools
import getpass
import glob
import io
import itertools
import json
import logging
import sys

import click
import click.types

import romp._core
import romp._matrix


logger = logging.getLogger(__name__)


# https://github.com/pallets/click/pull/1278
class Choice(click.types.ParamType):
    """The choice type allows a value to be checked against a fixed set
    of supported values. All of these values have to be strings.

    You should only pass a list or tuple of choices. Other iterables
    (like generators) may lead to surprising results.

    See :ref:`choice-opts` for an example.

    :param case_sensitive: Set to false to make choices case
        insensitive. Defaults to true.
    :param coerce_case: Resulting values are exactly as passed to `choices`
        rather than as collected from the command line.  Defaults to false.
    """

    name = 'choice'

    def __init__(self, choices, case_sensitive=True, coerce_case=False):
        self.choices = choices
        self.case_sensitive = case_sensitive
        self.coerce_case = coerce_case

    def get_metavar(self, param):
        return '[%s]' % '|'.join(self.choices)

    def get_missing_message(self, param):
        return 'Choose from:\n\t%s.' % ',\n\t'.join(self.choices)

    def convert(self, value, param, ctx):
        # Exact match
        if value in self.choices:
            return value

        # Match through normalization and case sensitivity
        # first do token_normalize_func, then lowercase
        # preserve original `value` to produce an accurate message in
        # `self.fail`
        normed_value = value
        normed_choices = self.choices

        if ctx is not None and \
           ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = [ctx.token_normalize_func(choice) for choice in
                              self.choices]

        if not self.case_sensitive:
            normed_value = normed_value.lower()
            normed_choices = [choice.lower() for choice in normed_choices]

        for normed_choice, choice in zip(normed_choices, self.choices):
            if normed_value == normed_choice:
                if self.coerce_case:
                    return choice

                return normed_value

        self.fail('invalid choice: %s. (choose from %s)' %
                  (value, ', '.join(self.choices)), param, ctx)

    def __repr__(self):
        return 'Choice(%r)' % list(self.choices)


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
        help=(
            'Targets to run on.  Mostly use the matrix options instead.'
            '  This may be removed.'
        ),
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
        '--archive-file',
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


def create_artifact_paths_option(
        envvar='ROMP_ARTIFACT_PATHS',
):
    return create_option(
        '--artifact-paths',
        envvar=envvar,
        help=(
            'Paths on remote system to build the artifact archive from.'
            '  Wildcards are supported via bash.'
        ),
        multiple=True,
    )


platforms_choice = Choice(
    choices=romp._matrix.all_platforms,
    case_sensitive=False,
    coerce_case=True,
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


interpreters_choice = Choice(
    choices=romp._matrix.all_interpreters,
    case_sensitive=False,
    coerce_case=True,
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


versions_choice = Choice(
    choices=romp._matrix.all_versions,
    case_sensitive=False,
    coerce_case=True,
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


architectures_choice = Choice(
    choices=all_architectures,
    case_sensitive=False,
    coerce_case=True,
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
        metavar='<PLATFORM INTERPRETER VERSION ARCHITECTURE>',
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


def create_archive_paths_root_option(
        envvar='ROMP_ARCHIVE_PATHS_ROOT',
):
    return create_option(
        '--archive-paths-root',
        envvar=envvar,
        help=(
            'Files in the uploaded archive will be stored with paths'
            ' relative to this path.'
        ),
        type=click.Path(exists=True, file_okay=False),
    )


def create_archive_paths_option(
        envvar='ROMP_ARCHIVE_PATHS',
):
    return create_option(
        '--archive-path',
        'archive_paths',
        envvar=envvar,
        help=(
            'Files to include in the archive which will be extracted prior'
            ' on the remote system prior to running the remote command.'
        ),
        multiple=True,
    )


def create_verbose_option(
        envvar='ROMP_VERBOSITY',
):
    return create_option(
        '--verbose',
        'verbosity',
        count=True,
        envvar=envvar,
        help='Increase logging verbosity by up to {} levels'.format(
            len(verbosity_levels) - 1,
        ),
        show_default=False,
    )


verbosity_levels = [
    (2, logging.DEBUG),
    (1, logging.INFO),
    (0, logging.WARNING),
]


def logging_level_from_verbosity(verbosity):
    for verbosity_cutoff, logging_level in verbosity_levels:
        if verbosity >= verbosity_cutoff:
            return logging_level


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
@create_artifact_paths_option()
@create_matrix_platforms_option()
@create_matrix_interpreters_option()
@create_matrix_versions_option()
@create_matrix_architectures_option()
@create_matrix_include_option()
@create_matrix_exclude_option()
@create_archive_paths_root_option()
@create_archive_paths_option()
@create_verbose_option()
def main(
        personal_access_token,
        build_request_url,
        command,
        username,
        environments,
        check_period,
        source_branch,
        definition_id,
        archive_file,
        artifact,
        artifact_paths,
        matrix_platforms,
        matrix_interpreters,
        matrix_versions,
        matrix_architectures,
        matrix_includes,
        matrix_excludes,
        archive_paths_root,
        archive_paths,
        verbosity,
):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level_from_verbosity(verbosity))
    root_logger.addHandler(logging.StreamHandler())

    archive_paths = list(itertools.chain.from_iterable(
        glob.glob(path)
        for path in archive_paths
    ))

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
        sys.exit(1)

    if archive_file is not None and len(archive_paths) > 0:
        click.echo('Specify either an archive file or archive paths')
        sys.exit(1)

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
            architecture=architecture,
        )
        for platform, interpreter, version, architecture in matrix_includes
    ]

    exclude_environments = [
        romp._matrix.Environment(
            platform=platform,
            interpreter=interpreter,
            version=version,
            architecture=architecture,
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
    archive_bytes = None
    if archive_file is not None:
        archive_bytes = archive_file.read()
    elif len(archive_paths) > 0:
        click.echo('Archiving paths for upload')
        archive_bytesio = io.BytesIO()
        romp._core.write_tarball_bytes(
            file=archive_bytesio,
            paths=archive_paths,
            paths_root=archive_paths_root,
        )
        archive_bytes = archive_bytesio.getvalue()

    if archive_bytes is not None:
        click.echo('Uploading archive')
        archive_url = romp._core.post_file(data=archive_bytes)
        click.echo('Archive URL: {}'.format(archive_url))

    click.echo('Requesting build')
    build = romp._core.request_remote_lock_build(
        archive_url=archive_url,
        username=username,
        personal_access_token=personal_access_token,
        build_request_url=build_request_url,
        command=command,
        environments=environments_string,
        source_branch=source_branch,
        definition_id=definition_id,
        artifact_paths=artifact_paths,
    )

    click.echo('Waiting for build: {}'.format(build.human_url))

    response_json = build.wait_for_lock_build(check_period=check_period)

    if artifact is not None:
        click.echo('Handling artifact')
        build.get_lock_build_artifact(artifact_file=artifact)

    if response_json['result'] != 'succeeded':
        sys.exit(1)

    sys.exit(0)
