import hashlib, json, subprocess, tempfile
from pathlib import Path
from sync_skills import sync
from validate_offline import validate
ROOT=Path(__file__).resolve().parents[1]
def run():
 checks=[]
 with tempfile.TemporaryDirectory(prefix='robot-knowledge-') as tmp:
  root=Path(tmp);repo=root/'repo';repo.mkdir()
  import shutil
  shutil.copytree(ROOT/'skills',repo/'skills',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.PIPE).decode().strip()
  git('init','-b','main');git('add','skills');git('-c','user.name=Offline Test','-c','user.email=offline@example.invalid','commit','-m','fixture')
  commit=git('rev-parse','HEAD');target=root/'target'
  sync(repo,commit,target);assert not target.exists();checks.append('dry run creates no files')
  result=sync(repo,commit,target,True)
  for name,digest in result['files'].items():assert hashlib.sha256((target/'.agents/skills'/name).read_bytes()).hexdigest()==digest
  checks.append('exact commit export and lock hashes')
  try:sync(repo,commit,target,True)
  except FileExistsError:checks.append('existing lock refuses overwrite')
  else:raise AssertionError('overwrite accepted')
  other=root/'conflict';(other/'.agents/skills/testcase-iteration').mkdir(parents=True)
  try:sync(repo,commit,other,True)
  except FileExistsError:checks.append('existing skill refuses overwrite before writes')
  else:raise AssertionError('skill conflict accepted')
  assert not (other/'.agents/skills/pytest-generation').exists()
  try:sync(repo,'main',root/'invalid',True)
  except ValueError:checks.append('floating branch refused')
  else:raise AssertionError('floating branch accepted')
  copy=root/'knowledge';shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','__pycache__'))
  f=copy/'.agents/skills/testcase-iteration/SKILL.md';f.write_text('changed',encoding='utf-8')
  assert not validate(copy)['passed'];checks.append('skill mirror drift detected')
 result={'passed':True,'checks':checks,'scope':'isolated temporary Git repository; no source project changes'}
 (ROOT/'sync-test-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':run()
