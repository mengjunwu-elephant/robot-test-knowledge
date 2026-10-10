"""Read-only OOXML style review against the team baseline or an approved project field profile."""
import argparse, hashlib, json, posixpath, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from review_workbook import NS, R, xy, addr, box, read_workbook

PROFILE=Path(__file__).resolve().parents[1]/'references/gripper-v1.4.1-format.json'

def load_styles(path):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>64*1024*1024:raise ValueError('expanded workbook exceeds 64MB')
        root=ET.fromstring(z.read('xl/styles.xml'))
        fonts=root.find('m:fonts',NS);borders=root.find('m:borders',NS);fills=root.find('m:fills',NS)
        styles=[]
        for xf in root.find('m:cellXfs',NS):
            font=fonts[int(xf.get('fontId','0'))];border=borders[int(xf.get('borderId','0'))]
            def val(tag,default=None):
                e=font.find('m:'+tag,NS);return e.get('val',default) if e is not None else default
            alignment=xf.find('m:alignment',NS);edges={}
            for side in ('left','right','top','bottom'):
                e=border.find('m:'+side,NS);color=e.find('m:color',NS) if e is not None else None
                edges[side]={'style':e.get('style') if e is not None else None,'rgb':color.get('rgb') if color is not None else None}
            pattern=fills[int(xf.get('fillId','0'))].find('m:patternFill',NS)
            b=font.find('m:b',NS)
            styles.append({'font':{'name':val('name'),'sz':val('sz')},'bold':b is not None and b.get('val','1') not in ('0','false'),'alignment':alignment.attrib if alignment is not None else {},'border':edges,'fill':pattern.get('patternType','none') if pattern is not None else 'none'})
        rels={e.get('Id'):e.get('Target') for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sh in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            target=rels[sh.get(R)];member=posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/'+target)
            if not member.startswith('xl/'):raise ValueError('unexpected worksheet location')
            root=ET.fromstring(z.read(member));cells={c.get('r'):styles[int(c.get('s','0'))] for c in root.findall('m:sheetData/m:row/m:c',NS)}
            result[sh.get('name')]={'styles':cells,'conditional':bool(root.findall('m:conditionalFormatting',NS)), 'rich_text':bool(root.findall('.//m:is/m:r',NS)) or 'xl/sharedStrings.xml' in z.namelist() and bool(ET.fromstring(z.read('xl/sharedStrings.xml')).findall('.//m:si/m:r',NS))}
        return result

def team_profile(data, baseline, layouts):
    result={'sheets':{}}
    roles=baseline['roles']
    for name,sheet in data.items():
        cells=sheet['cells'];layout=layouts.get(name)
        if layout:
            start=layout.get('start_row',1);header=layout['header_rows'];labels=layout['fields']
            if not isinstance(header,int) or not isinstance(start,int) or start<1 or header<start or not isinstance(labels,dict) or not labels:raise ValueError('invalid approved layout '+name)
        else:
            scores={row:sum(1 for ref,value in cells.items() if xy(ref)[0]==row and value in roles) for row in range(1,6)}
            candidates=[row for row,score in scores.items() if score>=2]
            if not candidates:continue
            start=min(candidates)
            header=start
            # Header labels merged vertically extend the header area.
            for merge in sheet['merges']:
                b=box(merge)
                if b[0]==start and b[2]>start and b[2]<=start+1:header=max(header,b[2])
            if scores.get(start+1,0)>=2:header=max(header,start+1)
            labels={}
            for ref,value in cells.items():
                row,col=xy(ref)
                if start<=row<=header and value:
                    labels[addr(1,col)[:-1]]=value
        fields={}
        for col,label in labels.items():
            if not isinstance(col,str) or not col.isalpha() or not col.isupper() or not isinstance(label,str):raise ValueError('invalid field layout '+name)
            rule={'font':baseline['font'],'bold':False,'alignment':{'horizontal':roles.get(label,'left'),'vertical':'center','wrapText':'1'},'border_style':'thin','border_rgb':baseline['body_border_rgb']}
            fields[col]={'label':label,'expected':rule,'unresolved':label not in roles}
        maxcol=max(xy(col+'1')[1] for col in fields)
        for col in range(1,maxcol+1):
            key=addr(1,col)[:-1]
            if key not in fields:fields[key]={'label':'未映射字段','expected':{'font':baseline['font'],'bold':False,'alignment':{'horizontal':'left','vertical':'center','wrapText':'1'},'border_style':'thin','border_rgb':baseline['body_border_rgb']},'unresolved':True}
        result['sheets'][name]={'start_row':start,'header_rows':header,'headers':{},'fields':fields,'header_border_rgb':baseline['header_border_rgb']}
    return result

def review(path,sheet_names=None,mapping=None,profile_path=None,baseline='gripper',layouts=None):
    path=Path(path);before=hashlib.sha256(path.read_bytes()).hexdigest()
    data=read_workbook(path);styles=load_styles(path)
    if profile_path:profile=json.loads(Path(profile_path).read_text(encoding='utf-8'))
    elif baseline=='team':profile=team_profile(data,json.loads((PROFILE.parent/'team-format.json').read_text(encoding='utf-8')),layouts or {})
    elif baseline=='gripper':profile=json.loads(PROFILE.read_text(encoding='utf-8'))
    else:raise ValueError('unknown baseline')
    mapping=mapping or {}
    if not isinstance(mapping,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in mapping.items()):raise ValueError('mapping must be a sheet-name object')
    names=sheet_names if sheet_names is not None else [n for n in data if n not in ('测试需求与环境','填写说明与示例')]
    if not names:raise ValueError('no case sheets selected')
    issues=[];checked=0
    def issue(code,name,ref,message,severity='error'):
        issues.append({'code':code,'sheet':name,'cell':ref,'message':message,'severity':severity})
    for name in names:
        if name not in data:raise ValueError('missing selected sheet '+name)
        expected=profile['sheets'].get(mapping.get(name,name))
        if expected is None:issue('UNMAPPED_FORMAT',name,'A1','没有批准的格式配方','warning');continue
        sheet=data[name];actual=styles[name];header=expected['header_rows'];fields=expected['fields']
        for col,field in fields.items():
            if field.get('unresolved'):issue('UNMAPPED_FIELD',name,col+str(header),'字段含义未确认；只检查通用字体与边框，对齐仍待确认','warning')
        if actual['conditional'] or actual['rich_text']:issue('VISUAL_OVERRIDE',name,'A1','存在条件格式或富文本；实际显示未验证','warning')
        # Verify field location before applying per-column recipes; environment names may be renamed.
        for ref,h in expected['headers'].items():
            row,col=xy(ref)
            flexible=row==1 and header==2 and sheet['cells'].get(addr(2,col))=='实际结果'
            if not flexible and sheet['cells'].get(ref,'')!=h['label']:issue('FORMAT_FIELD',name,ref,'字段位置与配方不同，需先确认映射')
        rows=sorted({xy(ref)[0] for ref,value in sheet['cells'].items() if value and xy(ref)[0]>header})
        if not rows:issue('EMPTY_FORMAT_SCOPE',name,'A1','没有可核对的用例正文','warning');continue
        last=max(rows);maxcol=max(xy(col+'1')[1] for col in fields)
        merges=[box(m) for m in sheet['merges']]
        for row in range(expected.get('start_row',1),last+1):
            for col in range(1,maxcol+1):
                ref=addr(row,col);merged=next((m for m in merges if m[0]<=row<=m[2] and m[1]<=col<=m[3]),None)
                anchor=not merged or (row,col)==merged[:2]
                st=actual['styles'].get(ref)
                if st is None:issue('STYLE_MISSING',name,ref,'用例网格缺少显式单元格样式');continue
                body=row>header
                rule=fields[addr(1,col)[:-1]]['expected'] if body else expected.get('header_expected',{'font':{'name':'Microsoft YaHei','sz':'10'},'bold':True,'alignment':{'horizontal':'center','vertical':'center','wrapText':'1'},'border_style':'thin','border_rgb':expected.get('header_border_rgb','FFB8C7D9')})
                checked+=1
                if anchor:
                    for key in ('name','sz'):
                        if st['font'][key]!=rule['font'][key]:issue('FONT_'+key.upper(),name,ref,'字体/字号应为 '+str(rule['font'][key]))
                    if st['bold']!=rule['bold']:issue('FONT_BOLD',name,ref,'表头加粗，正文不加粗')
                    for key in ('horizontal','vertical','wrapText'):
                        if body and key=='horizontal' and fields[addr(1,col)[:-1]].get('unresolved'):continue
                        if st['alignment'].get(key)!=rule['alignment'].get(key):issue('ALIGN_'+key.upper(),name,ref,'应为 '+key+'='+str(rule['alignment'].get(key)))
                    if body and st['fill']!='none':issue('BODY_FILL',name,ref,'正式正文应无背景填充')
                for side in ('left','right','top','bottom'):
                    if merged and not {'left':col==merged[1],'right':col==merged[3],'top':row==merged[0],'bottom':row==merged[2]}[side]:continue
                    edge=st['border'][side]
                    if edge['style']!=rule['border_style'] or edge['rgb']!=rule['border_rgb']:issue('BORDER',name,ref,side+'边应为指定颜色的细线')
    after=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'baseline':'project-profile' if profile_path else baseline,'selected_sheets':names,'field_mapping':{n:{c:f.get('label','') for c,f in profile['sheets'].get(mapping.get(n,n),{}).get('fields',{}).items()} for n in names},'static_format_passed':not any(i['severity']=='error' for i in issues),'unresolved':any(i['severity']=='warning' for i in issues),'checked_cells':checked,'source_sha256':before,'source_unchanged':before==after,'issues':issues,'scope':'direct font/alignment/fill and perimeter borders; no visual, semantic, formula or hardware validation'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workbook',type=Path,required=True);p.add_argument('--sheet',action='append');p.add_argument('--mapping',type=Path);p.add_argument('--report',type=Path);p.add_argument('--baseline',choices=['team','gripper'],default='team');p.add_argument('--profile',type=Path);p.add_argument('--layout',type=Path);a=p.parse_args()
    try:
        if a.report and (a.report.suffix.lower()!='.json' or a.report.resolve()==a.workbook.resolve() or any(a.report.resolve()==p.resolve() for p in (a.mapping,a.profile,a.layout) if p)):raise ValueError('report must be a separate JSON file')
        result=review(a.workbook,a.sheet,json.loads(a.mapping.read_text(encoding='utf-8')) if a.mapping else None,a.profile,a.baseline,json.loads(a.layout.read_text(encoding='utf-8')) if a.layout else None)
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if a.report:a.report.write_text(text+'\n',encoding='utf-8')
        print(text);raise SystemExit(0 if result['static_format_passed'] and not result['unresolved'] else 1)
    except (ValueError,OSError,KeyError,IndexError,TypeError,zipfile.BadZipFile,ET.ParseError) as e:p.exit(2,'Format review stopped: '+str(e)+'\n')
