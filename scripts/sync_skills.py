import argparse, hashlib, json, re, subprocess
from pathlib import Path, PurePosixPath
NAMES=('testcase-iteration','pytest-generation')
def git(repo,*args):
 return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.PIPE)
def sync(repo,revision,target,apply=False):
 if not re.fullmatch(r'[0-9a-f]{40}',revision):raise ValueError('revision must be full 40-character lowercase commit')
 if git(repo,'rev-parse',revision+'^{commit}').decode().strip()!=revision:raise ValueError('not an exact commit')
 target=Path(target).resolve();dest=target/'.agents/skills';lock=target/'knowledge.lock.json'
 if lock.exists():raise FileExistsError('existing knowledge.lock.json; review upgrade in a separate branch')
 payload={}
 listing=git(repo,'ls-tree','-r','-z',revision,'--','skills').decode('utf-8').rstrip('\0').split('\0')
 for line in listing:
  meta,name=line.split('\t',1);mode,kind,oid=meta.split()
  relative=PurePosixPath(name).relative_to('skills')
  if not relative.parts or relative.parts[0] not in NAMES:continue
  if mode!='100644' or kind!='blob' or '..' in relative.parts:raise ValueError('unsafe package entry '+name)
  payload[relative.as_posix()]=git(repo,'cat-file','blob',oid)
 for name in NAMES:
  if name+'/SKILL.md' not in payload:raise ValueError('missing skill '+name)
  if (dest/name).exists():raise FileExistsError('refusing overwrite '+name)
 info={'schema_version':1,'revision':revision,'files':{n:hashlib.sha256(b).hexdigest() for n,b in payload.items()}}
 if apply:
  # Preflight completes before writes. Never delete or overwrite target content.
  dest.mkdir(parents=True,exist_ok=True)
  created=[]
  try:
   for name in NAMES:
    p=dest/name;p.mkdir();created.append(p)
   for name,data in payload.items():
    p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)
   with lock.open('x',encoding='utf-8') as f:json.dump(info,f,ensure_ascii=False,indent=2);f.write('\n')
  except Exception:
   # Remove only files created by this invocation, never existing target paths.
   for folder in created:
    for p in sorted(folder.rglob('*'),key=lambda x:len(x.parts),reverse=True):
     if p.is_file():p.unlink()
     elif p.is_dir():p.rmdir()
    folder.rmdir()
   raise
 return {'apply':apply,'target':str(target),**info}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--revision',required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
 print(json.dumps(sync(a.repo,a.revision,a.target,a.apply),ensure_ascii=False,indent=2))
