"""Read-only OOXML style review against the approved gripper field profile."""
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

def review(path,sheet_names=None,mapping=None):
    path=Path(path);before=hashlib.sha256(path.read_bytes()).hexdigest()
    profile=json.loads(PROFILE.read_text(encoding='utf-8'));data=read_workbook(path);styles=load_styles(path)
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
        for row in range(1,last+1):
            for col in range(1,maxcol+1):
                ref=addr(row,col);merged=next((m for m in merges if m[0]<=row<=m[2] and m[1]<=col<=m[3]),None)
                anchor=not merged or (row,col)==merged[:2]
                st=actual['styles'].get(ref)
                if st is None:issue('STYLE_MISSING',name,ref,'用例网格缺少显式单元格样式');continue
                body=row>header
                rule=fields[addr(1,col)[:-1]]['expected'] if body else {'font':{'name':'Microsoft YaHei','sz':'10'},'bold':True,'alignment':{'horizontal':'center','vertical':'center','wrapText':'1'},'border_style':'thin','border_rgb':'FFB8C7D9'}
                checked+=1
                if anchor:
                    for key in ('name','sz'):
                        if st['font'][key]!=rule['font'][key]:issue('FONT_'+key.upper(),name,ref,'字体/字号应为 '+str(rule['font'][key]))
                    if st['bold']!=rule['bold']:issue('FONT_BOLD',name,ref,'表头加粗，正文不加粗')
                    for key in ('horizontal','vertical','wrapText'):
                        if st['alignment'].get(key)!=rule['alignment'].get(key):issue('ALIGN_'+key.upper(),name,ref,'应为 '+key+'='+str(rule['alignment'].get(key)))
                    if body and st['fill']!='none':issue('BODY_FILL',name,ref,'正式正文应无背景填充')
                for side in ('left','right','top','bottom'):
                    if merged and not {'left':col==merged[1],'right':col==merged[3],'top':row==merged[0],'bottom':row==merged[2]}[side]:continue
                    edge=st['border'][side]
                    if edge['style']!=rule['border_style'] or edge['rgb']!=rule['border_rgb']:issue('BORDER',name,ref,side+'边应为指定颜色的细线')
    after=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'static_format_passed':not any(i['severity']=='error' for i in issues),'unresolved':any(i['severity']=='warning' for i in issues),'checked_cells':checked,'source_sha256':before,'source_unchanged':before==after,'issues':issues,'scope':'direct font/alignment/fill and perimeter borders; no visual, semantic, formula or hardware validation'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workbook',type=Path,required=True);p.add_argument('--sheet',action='append');p.add_argument('--mapping',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    try:
        if a.report and (a.report.suffix.lower()!='.json' or a.report.resolve()==a.workbook.resolve() or a.mapping and a.report.resolve()==a.mapping.resolve()):raise ValueError('report must be a separate JSON file')
        result=review(a.workbook,a.sheet,json.loads(a.mapping.read_text(encoding='utf-8')) if a.mapping else None)
        text=json.dumps(result,ensure_ascii=False,indent=2)
        if a.report:a.report.write_text(text+'\n',encoding='utf-8')
        print(text);raise SystemExit(0 if result['static_format_passed'] and not result['unresolved'] else 1)
    except (ValueError,OSError,KeyError,IndexError,TypeError,zipfile.BadZipFile,ET.ParseError) as e:p.exit(2,'Format review stopped: '+str(e)+'\n')
