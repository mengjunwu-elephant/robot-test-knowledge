import argparse, ast, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(root=ROOT,sources=False):
 errors=[];checks=0
 try:
  marketplace=json.loads((root/'.cursor-plugin/marketplace.json').read_text(encoding='utf-8'))
  cursor=json.loads((root/'.cursor-plugin/plugin.json').read_text(encoding='utf-8'))
  portable=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
  checks+=5
  if marketplace['plugins'][0]['source']!='.':errors.append('Cursor marketplace must resolve repository root')
  if marketplace['plugins'][0]['name']!=cursor['name'] or cursor['name']!=portable['name']:errors.append('Cursor plugin name mismatch')
  if cursor['version']!=portable['version']:errors.append('Cursor plugin version mismatch')
  if cursor['skills']!='./skills/':errors.append('Cursor must reuse canonical skills directory')
  if len(marketplace['plugins'])!=1:errors.append('unexpected Cursor marketplace entries')
 except (OSError,ValueError,KeyError,IndexError,TypeError) as e:
  errors.append('invalid Cursor manifest: '+str(e))
 required=['standards','fundamentals','skills','templates','scripts','projects','README.md','CHANGELOG.md','AGENTS.md','docs/方案总文档.md','docs/项目交接文档.md']
 for p in required:
  checks+=1
  if not (root/p).exists():errors.append('missing '+p)
 for p in (root/'scripts').glob('*.py'):
  checks+=1
  try:ast.parse(p.read_text(encoding='utf-8'))
  except SyntaxError as e:errors.append(str(e))
 for name in ['testcase-iteration','pytest-generation']:
  folder=root/'skills'/name;manifest=folder/'SKILL.md';text=manifest.read_text(encoding='utf-8')
  checks+=1
  if not re.match(r'---\nname: '+name+r'\ndescription: .+\n---\n',text):errors.append('invalid frontmatter '+name)
  for p in folder.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
    checks+=1;relative=p.relative_to(root/'skills');copy=root/'.agents/skills'/relative
    if not copy.exists() or copy.read_bytes()!=p.read_bytes():errors.append('mirror mismatch '+str(relative))
    if p.suffix=='.py':
     try:ast.parse(p.read_text(encoding='utf-8'))
     except SyntaxError as e:errors.append(str(e))
  for link in re.findall(r'\]\(([^)]+)\)',text):
   if '://' not in link and not (folder/link).exists():errors.append('broken skill reference '+link)
 # The installed skill copies must follow the canonical public rule sources.
 for source,target in [('standards/team-rules.md','skills/testcase-iteration/references/team-rules.md'),('standards/team-rules.md','skills/pytest-generation/references/team-rules.md'),('standards/testing-contract.md','skills/pytest-generation/references/automation-contract.md')]:
  checks+=1
  if not (root/target).exists() or (root/source).read_bytes()!=(root/target).read_bytes():errors.append('canonical rule mismatch '+target)
 if sources:
  data=json.loads((root/'projects/source-manifest.json').read_text(encoding='utf-8'))
  for item in data['files']:
   p=Path(data['roots'][item['project']])/item['path'];checks+=1
   if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('source drift '+item['project']+'/'+item['path'])
 return {'passed':not errors,'checks':checks,'errors':errors,'scope':'static files only; no source project imports, collection, hardware or network'}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--sources',action='store_true');args=parser.parse_args()
 result=validate(sources=args.sources);(ROOT/'offline-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['passed'] else 1)
