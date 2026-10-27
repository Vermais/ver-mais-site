"""Publish the already signed, SHA-256 verified APK without recompilation."""
from pathlib import Path
import base64, bz2, hashlib, json, os, sys, urllib.request, urllib.error

ROOT=Path(__file__).resolve().parent
BASE_URL='https://github.com/Vermais/ver-mais-site/releases/download/v1.0.6/ver-mais-v1.0.6-teste.apk'
BASE_SHA='1306f461944aee35756e03a989df1db7ae97cbbef51ff84dcbed78fb5ad080f5'
TARGET_SHA='ec0e50dc0900d0d19749d997aac64ee2669fd74935eb50fb48758a794a708559'
TARGET_SIZE=51634415

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

def api(method,url,body=None,content_type='application/json'):
    if isinstance(body,dict): body=json.dumps(body).encode()
    request=urllib.request.Request(url,data=body,method=method,headers={
        'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],
        'Accept':'application/vnd.github+json','Content-Type':content_type,
        'User-Agent':'VerMais-release-publisher','X-GitHub-Api-Version':'2022-11-28'})
    with urllib.request.urlopen(request,timeout=120) as response: return json.load(response)

def main():
    if len(sys.argv)==3 and sys.argv[1]=='--verify':
        apk=reconstruct(Path(sys.argv[2]).read_bytes())
        print('Verified signed APK:',hashlib.sha256(apk).hexdigest(),len(apk))
        return
    assert os.environ.get('GITHUB_REPOSITORY')=='Vermais/ver-mais-site'
    with urllib.request.urlopen(BASE_URL,timeout=90) as response: old=response.read()
    apk=reconstruct(old)
    endpoint='https://api.github.com/repos/Vermais/ver-mais-site/releases'
    try: release=api('GET',endpoint+'/tags/v1.0.7')
    except urllib.error.HTTPError as error:
        if error.code!=404: raise
        release=api('POST',endpoint,{
            'tag_name':'v1.0.7','target_commitish':os.environ['GITHUB_SHA'],
            'name':'Ver+ 1.0.7 — Descrições com mais contexto (teste)',
            'body':(ROOT/'release-notes.md').read_text(encoding='utf-8'),
            'draft':True,'prerelease':True})
    existing={a['name']:a for a in release.get('assets',[])}
    assets=[
        ('ver-mais-v1.0.7-teste.apk',bytes(apk),'application/vnd.android.package-archive'),
        ('DESEMPENHO_E_VALIDACAO.md',(ROOT/'DESEMPENHO_E_VALIDACAO.md').read_bytes(),'text/markdown'),
        ('SHA256SUMS.txt',(TARGET_SHA+'  ver-mais-v1.0.7-teste.apk\n').encode(),'text/plain')]
    for name,data,mime in assets:
        expected='sha256:'+hashlib.sha256(data).hexdigest()
        if name in existing:
            assert existing[name].get('digest')==expected, 'Existing asset differs; refusing overwrite'
            continue
        uploaded=api('POST',release['upload_url'].split('{')[0]+'?name='+name,data,mime)
        assert uploaded['size']==len(data)
        if uploaded.get('digest'): assert uploaded['digest']==expected
    api('PATCH',endpoint+'/'+str(release['id']),{'draft':False,'prerelease':True})
    print('Published verified test release:',release['html_url'])

if __name__=='__main__': main()

