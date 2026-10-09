"""Fetch latest official release; verify assets before reusing offline installer."""
import argparse, hashlib, json, re, tempfile, urllib.request, zipfile, sys
from pathlib import Path
REPO = 'mengjunwu-elephant/robot-test-knowledge'
def fetch(url):
    if not url.startswith('https://github.com/'+REPO+'/releases/download/') and url != 'https://api.github.com/repos/'+REPO+'/releases/latest':
        raise ValueError('unexpected download origin')
    request=urllib.request.Request(url,headers={'User-Agent':'robot-test-knowledge-updater'})
    with urllib.request.urlopen(request,timeout=30) as response:
        return response.read(32*1024*1024+1)
def validate_extract(data, destination):
    import io
    if len(data)>32*1024*1024: raise ValueError('package too large')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if sum(i.file_size for i in z.infolist())>64*1024*1024: raise ValueError('expanded package too large')
        for i in z.infolist():
            p=Path(i.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in i.filename or not i.filename.startswith('robot-test-knowledge/') or (i.external_attr>>16)&0o170000==0o120000:
                raise ValueError('unsafe archive entry')
        z.extractall(destination)
def update(user_root, apply=False, fetcher=fetch):
    release=json.loads(fetcher('https://api.github.com/repos/'+REPO+'/releases/latest'))
    version=release['tag_name'].removeprefix('v')
    if release.get('draft') or release.get('prerelease') or not re.fullmatch(r'\d+\.\d+\.\d+',version): raise ValueError('not an official version')
    assets={a['name']:a['browser_download_url'] for a in release['assets']}
    name=f'robot-test-knowledge-{version}.zip'
    if not apply: return {'latest':version,'applied':False}
    checksum=fetcher(assets['SHA256SUMS.txt']).decode('utf-8').splitlines()
    expected=[line.split()[0] for line in checksum if len(line.split())==2 and line.split()[1]==name]
    data=fetcher(assets[name])
    if len(expected)!=1 or hashlib.sha256(data).hexdigest()!=expected[0]: raise ValueError('release checksum mismatch')
    with tempfile.TemporaryDirectory() as folder:
        validate_extract(data,folder)
        package=Path(folder)/'robot-test-knowledge'
        if json.loads((package/'plugin.json').read_text(encoding='utf-8'))['version']!=version: raise ValueError('release version mismatch')
        from install import install
        return install(package,user_root,True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--user-root',type=Path,default=Path.home());a=p.parse_args()
    try: print(json.dumps(update(a.user_root,a.apply),ensure_ascii=False,indent=2))
    except Exception as e: p.exit(1,'Update stopped; previous installation retained: '+str(e)+'\n')
