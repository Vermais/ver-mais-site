"""Publish the verified Ver+ 1.2.7 APK using the previous signed release."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
APK_NAME = 'ver-mais-v1.2.7-telas-figma.apk'
TARGET_SHA = '087785740c2264cf4a1c7416f6e4a62fd75fb1e96127f50191f247cd2df47592'
TARGET_SIZE = 80481852
TAG = 'v1.2.7'
BASE_URL = 'https://github.com/Vermais/ver-mais-site/releases/download/v1.2.6/ver-mais-v1.2.6-teste.apk'
BASE_SHA = 'ee53828a7541495a133e3311514fe5285a026c0116341e82c82fc4cce0358e68'


def reconstruct(old):
    assert hashlib.sha256(old).hexdigest() == BASE_SHA, 'Base APK hash mismatch'
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        subprocess.run(['git', 'init', '-q'], cwd=path, check=True)
        (path / 'app.apk').write_bytes(old)
        patch = b''.join(part.read_bytes() for part in sorted((ROOT / 'parts').glob('*.txt')))
        subprocess.run(['git', 'apply', '--binary', '-'], input=patch, cwd=path, check=True)
        apk = (path / 'app.apk').read_bytes()
    assert len(apk) == TARGET_SIZE
    assert hashlib.sha256(apk).hexdigest() == TARGET_SHA, 'Reconstructed APK hash mismatch'
    return apk


def api(method, url, body=None, content_type='application/json'):
    if isinstance(body, dict):
        body = json.dumps(body).encode()
    request = urllib.request.Request(url, data=body, method=method, headers={
        'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
        'Accept': 'application/vnd.github+json', 'Content-Type': content_type,
        'User-Agent': 'VerMais-release-publisher', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--verify':
        apk = reconstruct(Path(sys.argv[2]).read_bytes())
        print('Verified signed APK:', TARGET_SHA, len(apk))
        return
    assert os.environ.get('GITHUB_REPOSITORY') == 'Vermais/ver-mais-site'
    with urllib.request.urlopen(BASE_URL, timeout=90) as response:
        apk = reconstruct(response.read())
    endpoint = 'https://api.github.com/repos/Vermais/ver-mais-site/releases'
    try:
        release = api('GET', endpoint + '/tags/' + TAG)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        release = api('POST', endpoint, {
            'tag_name': TAG, 'target_commitish': os.environ['GITHUB_SHA'],
            'name': 'Ver+ 1.2.6 — Guia por voz (teste)',
            'body': (ROOT / 'release-notes.md').read_text(encoding='utf-8'),
            'draft': True, 'prerelease': True})
    existing = {asset['name']: asset for asset in release.get('assets', [])}
    assets = [
        (APK_NAME, bytes(apk), 'application/vnd.android.package-archive'),
        ('SHA256SUMS.txt', (TARGET_SHA + '  ' + APK_NAME + '\n').encode(), 'text/plain')]
    for name, data, mime in assets:
        expected = 'sha256:' + hashlib.sha256(data).hexdigest()
        if name in existing:
            assert existing[name].get('digest') == expected, 'Existing asset differs; refusing overwrite'
            assert existing[name]['size'] == len(data)
            continue
        uploaded = api('POST', release['upload_url'].split('{')[0] + '?name=' + name, data, mime)
        assert uploaded['size'] == len(data)
        if uploaded.get('digest'):
            assert uploaded['digest'] == expected
    api('PATCH', endpoint + '/' + str(release['id']), {'draft': False, 'prerelease': True})
    print('Published verified test release:', release['html_url'])


if __name__ == '__main__':
    main()
