"""Read-only OOXML case review. Python 3.10+, no imports from target projects."""
import argparse, hashlib, json, posixpath, re, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
TEMPLATES={'general':'通用软件测试用例模板_v1.0.xlsx','firmware':'固件测试用例模板_v1.0.xlsx','ros':'ROS测试用例模板_v1.0.xlsx'}
STATES={'Pass','Fail','Blocked','Not Executed','N/A'}
SKIP={'测试需求与环境','填写说明与示例'}
def xy(ref):
    match=re.fullmatch(r'([A-Z]+)([1-9]\d*)',ref)
    if not match:raise ValueError('invalid cell '+ref)
    col=0
    for c in match[1]:col=col*26+ord(c)-64
    return int(match[2]),col
def addr(row,col):
    text=''
    while col:col,rem=divmod(col-1,26);text=chr(65+rem)+text
    return text+str(row)
def box(ref):
    start,_,end=ref.partition(':');a=xy(start);b=xy(end or start)
    return a[0],a[1],b[0],b[1]
def clean(value):return '' if value is None else str(value).strip()
def read_workbook(path):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>64*1024*1024:raise ValueError('workbook expanded size exceeds 64MB')
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in root]
        rels={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets={}
        for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            target=rels[s.attrib[R]]
            member=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/'+target)
            if not member.startswith('xl/'):raise ValueError('unexpected worksheet location')
            root=ET.fromstring(z.read(member));cells={};formulas=[]
            for c in root.findall('m:sheetData/m:row/m:c',NS):
                v=c.find('m:v',NS);inline=c.find('m:is',NS)
                value=v.text if v is not None and v.text is not None else ''.join(t.text or '' for t in inline.findall('.//m:t',NS)) if inline is not None else ''
                if c.attrib.get('t')=='s' and value:value=strings[int(value)]
                if c.find('m:f',NS) is not None:formulas.append(c.attrib['r'])
                cells[c.attrib['r']]=clean(value)
            sheets[s.attrib['name']]={'cells':cells,'merges':[m.attrib['ref'] for m in root.findall('m:mergeCells/m:mergeCell',NS)],'formulas':formulas}
        return sheets
def cell(sheet,row,col):
    key=addr(row,col)
    for merge in sheet['merges']:
        r1,c1,r2,c2=box(merge)
        if r1<=row<=r2 and c1<=col<=c2:key=addr(r1,c1);break
    return sheet['cells'].get(key,''),key
REQUIRED_ROLES={'用例编号','指令序号','功能名称','测试接口','测试目的','优先级','前置条件','测试步骤','预期结果','所属模块','ROS 接口名称','消息／服务／动作类型','接口名称','测试项','老化脚本逻辑','预期结果／判定标准'}
EXECUTION_ROLES={'实际结果','执行状态','回归测试记录','异常／回归记录','测试证据'}
ROLE_ALIASES={'功能':'功能名称','API':'测试接口','api':'测试接口','接口':'测试接口','前提条件':'前置条件','编号':'用例编号','ID':'用例编号','id':'用例编号','操作步骤':'测试步骤','步骤':'测试步骤','预期':'预期结果','证据':'测试证据','回归记录':'回归测试记录','测试目标':'测试目的','目的':'测试目的','priority':'优先级'}

def column_number(col):
    if not isinstance(col,str) or not re.fullmatch(r'[A-Z]{1,3}',col):raise ValueError('invalid column '+str(col))
    n=xy(col+'1')[1]
    if n>16384:raise ValueError('column outside Excel range')
    return n

def occupied_columns(sheet,start=1):
    cols={xy(ref)[1] for ref,value in sheet['cells'].items() if value and xy(ref)[0]>=start}
    cols.update(xy(ref)[1] for ref in sheet.get('formulas',[]) if xy(ref)[0]>=start)
    for merge in sheet['merges']:
        a,b,c,d=box(merge)
        if c>=start and sheet['cells'].get(addr(a,b)):
            cols.update(range(b,d+1))
    return {addr(1,c)[:-1] for c in cols}

def excluded_columns(layout,fields):
    excluded=layout.get('excluded_columns',{})
    if not isinstance(excluded,dict):raise ValueError('excluded_columns must give a reason per column')
    for col,reason in excluded.items():
        column_number(col)
        if not isinstance(reason,str) or not reason.strip():raise ValueError('excluded column needs a reason')
        if col in fields:raise ValueError('column is both checked and excluded: '+col)
    return excluded

def approved_template(sheet,layout):
    if not isinstance(layout,dict):raise ValueError('layout must be an object')
    start=layout.get('start_row',1);end=layout.get('header_rows');fields=layout.get('fields')
    if type(start) is not int or type(end) is not int or not 1<=start<=end<=1048576:raise ValueError('invalid header rows')
    if not isinstance(fields,dict) or not fields:raise ValueError('layout needs fields')
    excluded=excluded_columns(layout,fields)
    required=layout.get('required_roles')
    known=REQUIRED_ROLES|EXECUTION_ROLES|{'备注','说明'}
    if not isinstance(required,list) or not required or any(not isinstance(v,str) or ROLE_ALIASES.get(v,v) not in REQUIRED_ROLES for v in required):raise ValueError('layout needs approved required_roles')
    required={ROLE_ALIASES.get(v,v) for v in required}
    headers=dict(layout.get('headers',{}));labels={}
    for ref,label in headers.items():
        row,col=xy(ref)
        if not start<=row<=end or not isinstance(label,str):raise ValueError('invalid approved header')
    for col,field in fields.items():
        n=column_number(col)
        if isinstance(field,str):label=role=field
        elif isinstance(field,dict):label=field.get('label');role=field.get('role')
        else:raise ValueError('invalid field')
        if not isinstance(label,str) or not label.strip() or not isinstance(role,str):raise ValueError('field needs label and role')
        role=ROLE_ALIASES.get(role,role);known_label=ROLE_ALIASES.get(label,label)
        if known_label in known and known_label!=role:raise ValueError('known field cannot change meaning')
        refs=[addr(row,n) for row in range(start,end+1) if sheet['cells'].get(addr(row,n))]
        ref=refs[-1] if refs else addr(end,n)
        if ref in headers and headers[ref]!=label:raise ValueError('contradictory header declaration')
        headers[ref]=label;labels[n]=role
    merges=layout.get('header_merges')
    if not isinstance(merges,list):raise ValueError('layout needs header_merges, use [] for unmerged headers')
    for merge in merges:
        a,b,c,d=box(merge)
        if not start<=a<=c<=end or b>d:raise ValueError('invalid header merge')
    groups={};used=set()
    for group in layout.get('execution_groups',[]):
        if not isinstance(group,dict) or not {'status','actual'}<=set(group):raise ValueError('execution group needs status and actual')
        converted={key:column_number(value) for key,value in group.items()}
        for key,col in converted.items():
            if key not in {'status','actual','evidence'} or labels.get(col)!={'status':'执行状态','actual':'实际结果','evidence':'测试证据'}[key]:raise ValueError('execution group role mismatch')
            if col in used:raise ValueError('execution column belongs to multiple groups')
            used.add(col)
        groups[converted['status']]=converted
    return {'cells':headers,'merges':merges,'formulas':[],'header_rows':end,'start_row':start,'labels':labels,'required_roles':required,'execution_groups':groups,'excluded_columns':excluded,'known_roles':known}

def inspect_sheet(name,sheet,template,mode='design'):
    issues=[];count=0
    def issue(code,row,col,message,severity='error'):
        issues.append({'severity':severity,'code':code,'sheet':name,'cell':addr(row,col),'message':message})
    header_rows=template.get('header_rows',2 if any(v=='实际结果' and xy(k)[0]==2 for k,v in template['cells'].items()) else 1)
    start=template.get('start_row',1);custom='labels' in template;excluded=template.get('excluded_columns',{})
    for key,expected in template['cells'].items():
        row,col=xy(key)
        if row<start or row>header_rows or not expected:continue
        actual=sheet['cells'].get(key,'')
        if re.fullmatch(r'环境\d+（请改名）',expected):
            if not actual:issue('HEADER',row,col,'环境组名称为空')
        elif actual!=expected:issue('HEADER',row,col,f'字段应为 {expected!r}，实际 {actual!r}')
    for key,actual in sheet['cells'].items():
        row,col=xy(key)
        if start<=row<=header_rows and addr(1,col)[:-1] not in excluded and actual and not template['cells'].get(key):issue('HEADER_EXTRA',row,col,'出现模板没有的额外表头字段')
    expected_merges={m for m in template['merges'] if box(m)[2]<=header_rows}
    actual_merges={m for m in sheet['merges'] if start<=box(m)[0]<=header_rows and not all(addr(1,c)[:-1] in excluded for c in range(box(m)[1],box(m)[3]+1))}
    if expected_merges!=actual_merges:issue('HEADER_MERGE',1,1,'表头合并结构与所选模板不同，需确认字段映射')
    labels=template.get('labels',{xy(k)[1]:v for k,v in template['cells'].items() if start<=xy(k)[0]<=header_rows and v})
    required_labels=template.get('required_roles',REQUIRED_ROLES)
    required={c for c,label in labels.items() if label in required_labels}
    id_cols=[c for c,label in labels.items() if label in {'用例编号','指令序号'}]
    execution={c for c,label in labels.items() if label in {'实际结果','执行状态','回归测试记录','异常／回归记录','测试证据'} or label.startswith('python')}
    design_cols={c for c,label in labels.items() if label in REQUIRED_ROLES}
    if custom:
        fields={addr(1,c)[:-1] for c in labels}
        for col in sorted(occupied_columns(sheet,start)-fields-set(excluded),key=column_number):issue('UNMAPPED_COLUMN',header_rows,column_number(col),'实际字段未映射，不能称完整检查','warning')
        for role in required_labels-set(labels.values()):issue('MISSING_ROLE',header_rows,1,'批准必需字段未映射：'+role)
        for col,label in labels.items():
            if label not in template['known_roles']:issue('UNMAPPED_ROLE',header_rows,col,'字段语义未确认：'+label,'warning')
            if label in {'执行状态','实际结果','测试证据'} and not any(col in group.values() for group in template['execution_groups'].values()):issue('UNMAPPED_EXECUTION',header_rows,col,'未声明该执行字段对应的状态/实际结果/证据分组','warning')
    candidates=sorted({xy(k)[0] for k,v in sheet['cells'].items() if xy(k)[0]>header_rows and v})
    seen={};active=[]
    for row in candidates:
        if not any(cell(sheet,row,col)[0] for col in design_cols):
            if any(cell(sheet,row,col)[0] for col in execution):issue('ORPHAN_RESULT',row,min(execution),'有执行记录但没有对应设计项')
            continue
        active.append(row);count+=1
        for col in sorted(required):
            value,key=cell(sheet,row,col)
            if not value:issue('REQUIRED',row,col,'缺少 '+labels[col])
            elif any(token in value for token in ('待确认','待填写','REQUIRED_RELEASE_VALUE')):issue('UNCONFIRMED',row,col,'内容未确认，不能作为执行基线','warning')
        for col in id_cols:
            value,key=cell(sheet,row,col)
            if value and value in seen and seen[value]!=key:issue('DUPLICATE_ID',row,col,'同表编号重复且不是同一合并组')
            elif value:seen[value]=key
        for col,label in labels.items():
            value,_=cell(sheet,row,col)
            if label=='优先级' and value and value not in {'P0','P1','P2','P3'}:issue('PRIORITY',row,col,'优先级必须为P0—P3')
            if mode=='design' and col in execution and value:issue('DESIGN_RESULT',row,col,'未执行设计副本应清空执行记录；历史原件不得自动清空')
            if label=='执行状态':
                if value and value not in STATES:issue('STATE',row,col,'不在批准状态集合中')
                group=template.get('execution_groups',{}).get(col) if custom else {'actual':col-1,'evidence':col+2 if labels.get(col+2)=='测试证据' else None}
                if group is None:continue
                actual_col=group['actual'];actual,_=cell(sheet,row,actual_col)
                if value in {'Not Executed','N/A'} and actual:issue('UNEXECUTED_RESULT',row,actual_col,'未执行/N/A不得填实际结果')
                evidence_col=group.get('evidence')
                if value in {'Fail','Blocked'} and evidence_col and not cell(sheet,row,evidence_col)[0]:issue('EVIDENCE',row,evidence_col,'失败/阻塞缺少证据')
                if value=='Pass' and not actual:issue('PASS_WITHOUT_ACTUAL',row,col,'Pass缺少实际观察；有观察也不能证明真实执行')
        for col in sheet.get('formulas',[]):
            if xy(col)[0]==row:issue('FORMULA_NOT_EVALUATED',row,xy(col)[1],'公式仅保留缓存读取，未重新计算','warning')
    independent=execution|{c for c,l in labels.items() if l in {'测试步骤','预期结果','预期结果／判定标准'}}
    for merge in sheet['merges']:
        r1,c1,r2,c2=box(merge)
        if r2>r1 and r2>header_rows and sum(r1<=r<=r2 for r in active)>1 and any(c1<=c<=c2 for c in independent):issue('MERGED_JUDGEMENT',r1,c1,'跨独立测试项合并步骤、预期或结果')
    return {'sheet':name,'case_items':count,'issues':issues,'field_mapping':{addr(1,c)[:-1]:role for c,role in labels.items()},'excluded_columns':excluded}
def review(path,category,mapping=None,mode='design',allow_empty=False,layouts=None,sheet_names=None):
    path=Path(path);before=hashlib.sha256(path.read_bytes()).hexdigest()
    sheets=read_workbook(path);templates=read_workbook(Path(__file__).resolve().parents[1]/'assets/templates'/TEMPLATES[category]);mapping=mapping or {}
    if not isinstance(mapping,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in mapping.items()):raise ValueError('mapping must be a JSON object of sheet names')
    layouts={} if layouts is None else layouts
    if not isinstance(layouts,dict) or any(n not in sheets for n in layouts):raise ValueError('layout contains unknown sheet')
    names=sheet_names if sheet_names is not None else list(sheets)
    if not names or any(n not in sheets for n in names):raise ValueError('invalid selected sheets')
    issues=[];counts=[]
    for name in names:
        sheet=sheets[name]
        target=mapping.get(name,name)
        if target in SKIP and name not in layouts:continue
        if target not in templates and name not in layouts:
            issues.append({'severity':'warning','code':'UNMAPPED_SHEET','sheet':name,'cell':'A1','message':'未映射到模板；保留原件并请求用户选择'});continue
        template=approved_template(sheet,layouts[name]) if name in layouts else templates[target]
        result=inspect_sheet(name,sheet,template,mode);counts.append({k:v for k,v in result.items() if k!='issues'});issues.extend(result['issues'])
    if not sum(i['case_items'] for i in counts) and not allow_empty:issues.append({'severity':'error','code':'EMPTY_DESIGN','sheet':'','cell':'','message':'没有识别到正式用例；空模板不能当设计交付'})
    after=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'static_checks_passed':not any(i['severity']=='error' for i in issues),'unresolved':any(i['severity']=='warning' for i in issues),'scope_complete':not any(i['severity']=='warning' for i in issues) and not any(s['excluded_columns'] for s in counts),'mode':mode,'source_sha256':before,'source_unchanged':before==after,'sheets':counts,'issues':issues,'scope':'read-only structure and selected cell rules; no formula recalculation, full style/visual, semantic or hardware validation'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workbook',type=Path,required=True);p.add_argument('--category',choices=TEMPLATES,required=True);p.add_argument('--mapping',type=Path);p.add_argument('--layout',type=Path);p.add_argument('--sheet',action='append');p.add_argument('--mode',choices=['design','executed'],default='design');p.add_argument('--allow-empty',action='store_true');p.add_argument('--report',type=Path);a=p.parse_args()
    try:
        if a.report and a.report.resolve()==a.workbook.resolve():raise ValueError('report must not overwrite source workbook')
        if a.report and a.report.suffix.lower()!='.json':raise ValueError('report must be a .json file')
        if a.report and any(a.report.resolve()==p.resolve() for p in (a.mapping,a.layout) if p):raise ValueError('report must not overwrite mapping or layout')
        mapping=json.loads(a.mapping.read_text(encoding='utf-8')) if a.mapping else None
        result=review(a.workbook,a.category,mapping,a.mode,a.allow_empty,json.loads(a.layout.read_text(encoding='utf-8')) if a.layout else None,a.sheet);text=json.dumps(result,ensure_ascii=False,indent=2)
        if a.report:a.report.write_text(text+'\n',encoding='utf-8')
        print(text);raise SystemExit(0 if result['static_checks_passed'] and not result['unresolved'] else 1)
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile,ET.ParseError) as e:p.exit(2,'Review stopped: '+str(e)+'\n')
