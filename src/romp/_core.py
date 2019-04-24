import glob
import io
import json
import logging
import os
import os.path
import tarfile
import time
import zipfile

import requests
import requests.auth


logger = logging.getLogger(__name__)


def write_tarball_bytes(file, paths, paths_root):
    with tarfile.TarFile(fileobj=file, mode='w') as archive:
        for path in paths:
            archive.add(name=path, arcname=os.path.relpath(path, paths_root))


class Build:
    def __init__(self, id, url, human_url):
        self.id = id
        self.url = url
        self.human_url = human_url

    @classmethod
    def from_response_json(cls, response_json):
        id = response_json['id']
        url = response_json['url']
        human_url = response_json['_links']['web']['href']

        return cls(id=id, url=url, human_url=human_url)

    def wait_for_lock_build(self, check_period=15):
        while True:
            logger.info("build url: %s", self.url)
            response = requests.get(self.url)

            response.raise_for_status()
            logger.info(response.content)
            response_json = response.json()

            status = response_json['status']

            if status == 'completed':
                return response_json

            logger.info('')
            logger.info('Url: %s', self.human_url)
            logger.info('Build Status: %s', status)
            logger.info(
                '    waiting %s seconds to check again for completion',
                check_period,
            )
            time.sleep(check_period)

    def get_lock_build_artifact(self, artifact_file):
        # 'https://dev.azure.com/altendky/a27e6706-93a8-46b1-8098-e5134713123d/_apis/build/builds/222/artifacts?artifactName=all&fileId=615BBA316A140A61F371BA354124349281B001BE9689366DA9660AC506A1ECCE01&fileName=lock.tar.gz&api-version=5.0-preview.3'
        # url = (
        #     'https://dev.azure.com'
        #     '/altendky/romp/_apis/build/builds/{build_id}/artifacts'
        # ).format(build_id=self.id)
        url = os.path.join(self.url, 'artifacts')

        logger.info('artifact url: %s', url)

        response = requests.get(
            url=url,
            params={
                'api-version': '5.0',
            }
        )
        response.raise_for_status()

        artifact_name = 'lock_files'

        response_json = response.json()
        for artifact in response_json['value']:
            if artifact['name'] != artifact_name:
                continue

            artifact_download_url = artifact['resource']['downloadUrl']

            break
        else:
            raise Exception('artifact not found: ' + artifact_name)

        response = requests.get(artifact_download_url)
        i = io.BytesIO(response.content)

        with zipfile.ZipFile(file=i) as artifacts:
            opened = artifacts.open(
                os.path.join(artifact_name, 'artifacts.tar.gz'),
            )
            artifact_file.write(opened.read())


def strip_zip_info_prefixes(prefix, zip_infos):
    prefix = prefix.rstrip(os.sep) + os.sep
    result = []

    for zip_info in zip_infos:
        name = zip_info.filename

        if os.path.commonpath((name, prefix)) == '':
            raise Exception('unexpected path: ' + name)

        if len(name) <= len(prefix):
            continue

        if name.endswith(os.sep):
            continue

        zip_info.filename = os.path.relpath(name, prefix)
        logger.info('%s -> %s', name, zip_info.filename)
        result.append(zip_info)

    return result


def post_file(data):
    response = requests.post(
        url='https://file.io/',
        params={'expires': '1w'},
        files={'file': ('archive.tar.gz', data)},
    )

    response.raise_for_status()
    response_json = response.json()

    if not response_json['success']:
        raise Exception('failed to upload archive')

    logger.info('response_json: %s', json.dumps(response_json, indent=4))

    return response_json['link']


def request_remote_lock_build(
        archive_url,
        username,
        personal_access_token,
        build_request_url,
        command,
        environments,
        source_branch,
        definition_id,
        artifact_paths,
):
    parameters = {
        'ROMP_COMMAND': command,
        'ROMP_ENVIRONMENTS': environments,
        'ROMP_ARTIFACT_PATHS': ' '.join(path for path in artifact_paths),
    }

    if archive_url is not None:
        parameters['ROMP_ARCHIVE_URL'] = archive_url

    response = requests.post(
        url=build_request_url,
        auth=requests.auth.HTTPBasicAuth(
            username,
            personal_access_token,
        ),
        json={
            "definition": {"id": definition_id},
            "sourceBranch": source_branch,
            "parameters": json.dumps(parameters),
        },
    )

    logger.info('response-----')
    logger.info('status: %s', response.status_code)
    logger.info('text:')
    logger.info(response.text)
    response.raise_for_status()
    response_json = response.json()
    logger.info('json:')
    logger.info(json.dumps(response_json, indent=4))

    return Build.from_response_json(response_json=response_json)
