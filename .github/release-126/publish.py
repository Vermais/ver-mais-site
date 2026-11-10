"""Publish the exact signed and verified 1.2.6 test APK without recompiling it."""
from pathlib import Path
import base64
import zlib
import struct
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
APK_NAME = 'ver-mais-v1.2.6-teste.apk'
TARGET_SHA = 'ee53828a7541495a133e3311514fe5285a026c0116341e82c82fc4cce0358e68'
TARGET_SIZE = 80456000
TAG = 'v1.2.6'
BASE_URL = 'https://github.com/Vermais/ver-mais-site/releases/download/v1.2.2/ver-mais-v1.2.2-guia-teste.apk'
BASE_SHA = 'a3d4698a34115c2ca6e9da27dbbb4989931c8eb151e56ad228f4570d3b68bd6e'


def reconstruct(old):
    assert hashlib.sha256(old).hexdigest()==BASE_SHA, 'Base APK hash mismatch'
    encoded=''.join(p.read_text(encoding='ascii') for p in sorted((ROOT/'parts').glob('*.txt')))
    patch=zlib.decompress(base64.b64decode(encoded,validate=True))
    position=0; output=bytearray()
    while position<len(patch):
        op=patch[position:position+1];position+=1
        if op==b'L':
            length=struct.unpack_from('<I',patch,position)[0];position+=4
            assert position+length<=len(patch)
            output.extend(patch[position:position+length]);position+=length
        elif op in (b'C',b'D'):
            offset,length=struct.unpack_from('<II',patch,position);position+=8
            assert offset+length<=len(old)
            if op==b'C':output.extend(old[offset:offset+length])
            else:
                assert position+length<=len(patch)
                output.extend((a+b)&255 for a,b in zip(old[offset:offset+length],patch[position:position+length]));position+=length
        else:raise ValueError('Unknown patch operation')
        assert len(output)<=TARGET_SIZE
    assert len(output)==TARGET_SIZE
    assert hashlib.sha256(output).hexdigest()==TARGET_SHA, 'Reconstructed APK hash mismatch'
    return output


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
