"""Publish the exact signed and verified 1.2.1 test APK without recompiling it."""
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
APK_NAME = 'ver-mais-v1.2.1-guia-teste.apk'
TARGET_SHA = '58a233ddb24779002a4cf4991b8768645a6b64a465049ff219d752176182c0d5'
TARGET_SIZE = 80396313
TAG = 'v1.2.1'
BASE_URL = 'https://github.com/Vermais/ver-mais-site/releases/download/v1.2.0/ver-mais-v1.2.0-guia-teste.apk'
BASE_SHA = '45311cde13e74f875146c8e316acd9e942755a2be3c214dd50d01deaf6f26d24'


SOURCES = [('https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip', '6e1ce909032e1afa7a88e68a3d628ecafff302bdf195befab308826c395e93b7'), ('https://repo.maven.apache.org/maven2/com/alphacephei/vosk-android/0.3.75/vosk-android-0.3.75.aar', 'ab2f8b91ac8051561aa325546b35fed9a68b36b8121bac5c6fb927525c4adfad'), ('https://repo.maven.apache.org/maven2/net/java/dev/jna/jna/5.18.1/jna-5.18.1.aar', '7f053e3ec99e14dd71259c82c1c8a02738d64a13c31226b2acc170f3060951e0')]

def download_sources():
    sources = []
    for url, expected in SOURCES:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == expected, 'Dependency hash mismatch'
        sources.append(data)
    return sources


def reconstruct(old, sources):
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
        elif op == b'E':
            source, offset, length = struct.unpack_from('<BII', patch, position)
            position += 9
            dependency = sources[source]
            assert offset + length <= len(dependency)
            output.extend(dependency[offset:offset+length])
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
    if len(sys.argv) == 4 and sys.argv[1] == '--verify':
        apk = reconstruct(Path(sys.argv[2]).read_bytes(), [Path(sys.argv[3], url.rsplit("/", 1)[1]).read_bytes() for url, _ in SOURCES])
        print('Verified signed APK:', TARGET_SHA, len(apk))
        return
    assert os.environ.get('GITHUB_REPOSITORY') == 'Vermais/ver-mais-site'
    with urllib.request.urlopen(BASE_URL, timeout=90) as response:
        apk = reconstruct(response.read(), download_sources())
    endpoint = 'https://api.github.com/repos/Vermais/ver-mais-site/releases'
    try:
        release = api('GET', endpoint + '/tags/' + TAG)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        release = api('POST', endpoint, {
            'tag_name': TAG, 'target_commitish': os.environ['GITHUB_SHA'],
            'name': 'Ver+ 1.2.1 — Chamada por voz do Guia (teste)',
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
