"""Publish the exact signed and verified 1.1.2 test APK without recompiling it."""
from pathlib import Path
import base64
import bz2
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
APK_NAME = 'ver-mais-v1.1.2-teste.apk'
TARGET_SHA = 'c92689bbc2989957aef346d5d6cd25d32d85083cbcbafe6a2f9d519c0e720525'
TARGET_SIZE = 33931109
TAG = 'v1.1.2'
BASE_URL = 'https://github.com/Vermais/ver-mais-site/releases/download/v1.1.1/ver-mais-v1.1.1-teste.apk'
BASE_SHA = 'eb95be16ab19b9837524f383bce1c54a22ad18d9e9a0b675044c6eb33904bfdb'


def signed_integer(data):
    assert len(data)==8
    value=int.from_bytes(data,'little') & ((1<<63)-1)
    return -value if data[7]&128 else value

def reconstruct(old):
    assert hashlib.sha256(old).hexdigest()==BASE_SHA, 'Base APK hash mismatch'
    patch=base64.b64decode(''.join(p.read_text(encoding='ascii') for p in sorted((ROOT/'parts').glob('*.txt'))),validate=True)
    assert patch[:8]==b'BSDIFF40'
    control_length,diff_length,new_size=[signed_integer(patch[i:i+8]) for i in (8,16,24)]
    assert 0<=control_length<=len(patch) and 0<=diff_length<=len(patch) and new_size==TARGET_SIZE
    control=bz2.decompress(patch[32:32+control_length])
    difference=bz2.decompress(patch[32+control_length:32+control_length+diff_length])
    extra=bz2.decompress(patch[32+control_length+diff_length:])
    output=bytearray(new_size)
    old_position=new_position=control_position=diff_position=extra_position=0
    while new_position<new_size:
        assert control_position+24<=len(control)
        add,copy,seek=[signed_integer(control[control_position+i:control_position+i+8]) for i in (0,8,16)]
        control_position+=24
        assert add>=0 and copy>=0 and new_position+add+copy<=new_size
        assert diff_position+add<=len(difference) and extra_position+copy<=len(extra)
        output[new_position:new_position+add]=difference[diff_position:diff_position+add]
        for i in range(add):
            j=old_position+i
            if 0<=j<len(old): output[new_position+i]=(output[new_position+i]+old[j])&255
        new_position+=add;old_position+=add;diff_position+=add
        output[new_position:new_position+copy]=extra[extra_position:extra_position+copy]
        new_position+=copy;extra_position+=copy;old_position+=seek
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
            'name': 'Ver+ 1.1.2 — Progresso da captura Bluetooth (teste)',
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
