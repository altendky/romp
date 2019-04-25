romp
====

|PyPI| |Pythons| |Azure| |codecov| |GitHub|

Run on multiple platforms

I use `pip-tools`_ but also want to keep my compiled requirements for multiple
platforms.  Instead of sharing directories between machines or otherwise
shuttling files around I chose to create ``romp`` which will let me submit
arbitrary work to `Azure Pipelines`_ to get access to multiple platforms.
Personally, I will use this primarily behind `boots`_.

Below is an example usage.  It will run a single job under Linux with 64-bit
CPython 3.6.  The job will execute ``echo red > blue.txt`` and will collect
``*.txt`` from the job and save it locally to ``artifacts.tar.gz``.

.. code-block::

    $ venv/bin/romp --platform linux --interpreter cpython --version 3.6 --architecture x86_64 --command 'echo red > blue.txt' --artifact-paths '*.txt' --artifact artifacts.tar.gz
    Requesting build
    Waiting for build: https://dev.azure.com/altendky/f1722f91-62fe-4a15-8937-252c96b31292/_build/results?buildId=2938
    Handling artifact

Since ``romp`` leverages `Azure Pipelines`_ to get access to all the platforms,
server-side setup is required.  You will need an Azure account and to create
a pipeline (build) within that account using a ``romp`` repository (official
or your own fork).  Configure the pipeline to use
``deployed_ci/azure/azure-pipelines-lock.yml``.  It is configured such that
commits do not trigger builds.  ``romp``'s own CI and testing is driven by
``azure-pipelines.yml`` in the project root but this file can be ignored for
regular use.  Once the pipeline is setup you will need to `create a Personal
Access Token (PAT)`_ to use for authentication when running ``romp``.  The PAT
will need the build read and execute scope enabled.

For local setup, the command line options can be set by environment variables.
For many options this will not make sense but for a few it will.  Specifically
consider the follow options which will often be consistent for all calls.

- ``ROMP_BUILD_REQUEST_URL``
   - ``'https://dev.azure.com/altendky/romp-on/_apis/build/builds?api-version=5.0'``
- ``ROMP_DEFINITION_ID``
   - ``5``
- ``ROMP_PERSONAL_ACCESS_TOKEN``
   - ``fp6al3jxta2zliz6rh5hr6ewd5nw2hsmasse2laiyoyg7otneqjq``
- ``ROMP_USERNAME``
   - ``altendky``

.. code-block::

    $ venv/bin/romp --help
    Usage: romp [OPTIONS]

    Options:
      --personal-access-token, --pat TEXT
                                      A personal access token (PAT) with rights to
                                      initiate builds
                                      ($ROMP_PERSONAL_ACCESS_TOKEN)
      --build-request-url TEXT        The URL for submitting a build request
                                      ($ROMP_BUILD_REQUEST_URL)  [default: https:/
                                      /dev.azure.com/altendky/romp/_apis/build/bui
                                      lds?api-version=5.0]
      --command TEXT                  The command to be run for each target
                                      ($ROMP_COMMAND)  [default: python -c 'import
                                      sys; print(sys.version);
                                      print(sys.platform)']
      --username TEXT                 Username for build URL authentication
                                      ($ROMP_USERNAME)  [default: altendky]
      --environments TEXT             Targets to run on.  Mostly use the matrix
                                      options instead.  This may be removed.
                                      ($ROMP_ENVIRONMENTS)
      --check-period INTEGER          The period used to poll the build for
                                      completion ($ROMP_CHECK_PERIOD)  [default:
                                      15]
      --source-branch TEXT            The romp source branch to use for the build
                                      ($ROMP_SOURCE_BRANCH)  [default: develop]
      --definition-id INTEGER         The definition id of the build to be
                                      triggered ($ROMP_DEFINITION_ID)  [default:
                                      3]
      --archive-file FILENAME         The archive to be uploaded to the build
                                      ($ROMP_ARCHIVE)
      --artifact FILENAME             The path at which to save the resulting
                                      artifact ($ROMP_ARTIFACT_PATH)
      --artifact-paths TEXT           Paths on remote system to build the artifact
                                      archive from.  Wildcards are supported via
                                      bash. ($ROMP_ARTIFACT_PATHS)
      --platform [Linux|macOS|Windows]
                                      Platforms to matrix across
                                      ($ROMP_MATRIX_PLATFORMS)  [default: Linux,
                                      macOS, Windows]
      --interpreter [CPython|PyPy]    Interpreters to matrix across
                                      ($ROMP_MATRIX_INTERPRETERS)  [default:
                                      CPython, PyPy]
      --version [2.7|3.4|3.5|3.6|3.7]
                                      Versions to matrix across
                                      ($ROMP_MATRIX_VERSIONS)  [default: 2.7, 3.4,
                                      3.5, 3.6, 3.7]
      --architecture [x86|x86_64]     Architectures to matrix across
                                      ($ROMP_MATRIX_ARCHITECTURES)  [default: x86,
                                      x86_64]
      --include <PLATFORM INTERPRETER VERSION ARCHITECTURE>
                                      Complete environments to include in the
                                      matrix ($ROMP_MATRIX_INCLUDES)
      --exclude <PLATFORM INTERPRETER VERSION ARCHITECTURE>
                                      Complete environments to exclude from the
                                      matrix ($ROMP_MATRIX_EXCLUDES)
      --archive-paths-root DIRECTORY  Files in the uploaded archive will be stored
                                      with paths relative to this path.
                                      ($ROMP_ARCHIVE_PATHS_ROOT)
      --archive-path TEXT             Files to include in the archive which will
                                      be extracted prior on the remote system
                                      prior to running the remote command.
                                      ($ROMP_ARCHIVE_PATHS)
      --verbose                       Increase logging verbosity by up to 2 levels
                                      ($ROMP_VERBOSITY)
      --help                          Show this message and exit.

.. _pip-tools: https://github.com/jazzband/pip-tools
.. _Azure Pipelines: https://azure.microsoft.com/en-us/services/devops/pipelines/
.. _boots: https://github.com/altendky/boots
.. _`create a Personal Access Token (PAT)`: https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops

.. |PyPI| image:: https://img.shields.io/pypi/v/romp.svg
   :alt: PyPI version
   :target: https://pypi.org/project/romp/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/romp.svg
   :alt: supported Python versions
   :target: https://pypi.org/project/romp/

.. |Azure| image:: https://dev.azure.com/altendky/romp/_apis/build/status/altendky.romp?branchName=develop
   :alt: Azure build status
   :target: https://dev.azure.com/altendky/romp/_build

.. |codecov| image:: https://codecov.io/gh/altendky/romp/branch/develop/graph/badge.svg
   :alt: codecov coverage status
   :target: https://codecov.io/gh/altendky/romp

.. |GitHub| image:: https://img.shields.io/github/last-commit/altendky/romp/develop.svg
   :alt: source on GitHub
   :target: https://github.com/altendky/romp
