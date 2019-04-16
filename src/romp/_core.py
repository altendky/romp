import glob
import io
import json
import os
import tarfile
import time
import zipfile

import requests
import requests.auth


def write_tarball_bytes(file, paths):
    with tarfile.TarFile(fileobj=file, mode='w') as archive:
        for path in paths:
            archive.add(path)


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
            print("build url:", self.url)
            response = requests.get(self.url)

            response.raise_for_status()
            print(response.content)
            response_json = response.json()

            status = response_json['status']

            if status == 'completed':
                break

            print()
            print('Url:', self.human_url)
            print('Build Status: ' + status)
            print(
                '    waiting {} seconds to check again for completion'.format(
                    check_period,
                ),
            )
            time.sleep(check_period)

    def get_lock_build_artifact(self, artifact_file):
        # 'https://dev.azure.com/altendky/a27e6706-93a8-46b1-8098-e5134713123d/_apis/build/builds/222/artifacts?artifactName=all&fileId=615BBA316A140A61F371BA354124349281B001BE9689366DA9660AC506A1ECCE01&fileName=lock.tar.gz&api-version=5.0-preview.3'
        # url = (
        #     'https://dev.azure.com'
        #     '/altendky/romp/_apis/build/builds/{build_id}/artifacts'
        # ).format(build_id=self.id)
        url = os.path.join(self.url, 'artifacts')

        print('artifact url:', url)

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

        artifact_file.write(response.content)


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
        print(name, '->', zip_info.filename)
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

    print('response_json:', json.dumps(response_json, indent=4))

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
):
    parameters = {
        'ROMP_COMMAND': command,
        'ROMP_ENVIRONMENTS': environments,
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

    print('response-----')
    print('status:', response.status_code)
    print('text:')
    print(response.text)
    response.raise_for_status()
    response_json = response.json()
    print('json:')
    print(json.dumps(response_json, indent=4))

    return Build.from_response_json(response_json=response_json)
