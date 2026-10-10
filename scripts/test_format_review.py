import importlib.util, json, sys, tempfile, unittest, zipfile
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/testcase-iteration'
sys.path.insert(0,str(SKILL/'scripts'))
import review_format as checker
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
def node(tag,**attrs):return E.Element('{'+NS+'}'+tag,{k:str(v) for k,v in attrs.items()})

class FormatTests(unittest.TestCase):
    def fixture(self,mutate=None,merged=False):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);path=Path(tmp.name)/'cases.xlsx'
        st=node('styleSheet');fonts=E.SubElement(st,'{'+NS+'}fonts')
        for bold in (True,False):
            f=E.SubElement(fonts,'{'+NS+'}font');f.append(node('name',val='Microsoft YaHei'));f.append(node('sz',val='10'))
            if bold:f.append(node('b'))
        fills=E.SubElement(st,'{'+NS+'}fills');f=E.SubElement(fills,'{'+NS+'}fill');f.append(node('patternFill',patternType='none'))
        borders=E.SubElement(st,'{'+NS+'}borders')
        for rgb in ('FFB8C7D9','FF000000'):
            b=E.SubElement(borders,'{'+NS+'}border')
            for side in ('left','right','top','bottom'):
                edge=node(side,style='thin');edge.append(node('color',rgb=rgb));b.append(edge)
        xfs=E.SubElement(st,'{'+NS+'}cellXfs')
        for font,border,h in ((0,0,'center'),(1,1,'center'),(1,1,'left')):
            x=node('xf',fontId=font,borderId=border,fillId=0);x.append(node('alignment',horizontal=h,vertical='center',wrapText='1'));xfs.append(x)
        sheet=node('worksheet');rows=E.SubElement(sheet,'{'+NS+'}sheetData')
        labels=['指令序号','功能名称','测试接口','测试目的','优先级','前置条件','测试步骤','预期结果','环境一','','','','环境二','','','','备注']
        for r in range(1,5 if merged else 4):
            row=node('row',r=r);rows.append(row)
            for col in range(1,18):
                style=0 if r<=2 else 1 if col in (1,2,3,5) else 2
                c=node('c',r=checker.addr(r,col),s=style,t='inlineStr');inline=node('is');t=node('t')
                t.text=labels[col-1] if r==1 else {9:'实际结果',10:'执行状态',11:'回归测试记录',12:'测试证据',13:'实际结果',14:'执行状态',15:'回归测试记录',16:'测试证据'}.get(col,'') if r==2 else '1' if col==1 else ''
                inline.append(t);c.append(inline);row.append(c)
        if merged:
            mc=node('mergeCells');mc.append(node('mergeCell',ref='B3:B4'));sheet.append(mc)
        if mutate:mutate(st,sheet)
        wb=node('workbook');sheets=E.SubElement(wb,'{'+NS+'}sheets');s=node('sheet',name='串口指令测试结果',sheetId=1);s.set(checker.R,'rId1');sheets.append(s)
        rels=E.Element('Relationships');E.SubElement(rels,'Relationship',Id='rId1',Target='worksheets/sheet1.xml')
        with zipfile.ZipFile(path,'w') as z:
            for name,root in [('xl/styles.xml',st),('xl/workbook.xml',wb),('xl/_rels/workbook.xml.rels',rels),('xl/worksheets/sheet1.xml',sheet)]:z.writestr(name,E.tostring(root))
        return path
    def codes(self,path):return {i['code'] for i in checker.review(path,baseline='gripper')['issues']}
    def test_valid_and_read_only(self):
        p=self.fixture();before=p.read_bytes();r=checker.review(p,baseline='gripper')
        self.assertTrue(r['static_format_passed']);self.assertTrue(r['source_unchanged']);self.assertEqual(before,p.read_bytes())
    def test_font_size_and_name(self):
        def change(st,sh):
            f=st.find('m:fonts',checker.NS)[1];f.find('m:name',checker.NS).set('val','Carlito');f.find('m:sz',checker.NS).set('val','11')
        self.assertTrue({'FONT_NAME','FONT_SZ'}<=self.codes(self.fixture(change)))
    def test_alignment_and_wrap(self):
        def change(st,sh):
            a=st.find('m:cellXfs',checker.NS)[2].find('m:alignment',checker.NS);a.set('horizontal','center');a.set('wrapText','0')
        self.assertTrue({'ALIGN_HORIZONTAL','ALIGN_WRAPTEXT'}<=self.codes(self.fixture(change)))
    def test_missing_border(self):
        def change(st,sh):st.find('m:borders',checker.NS)[1].find('m:bottom',checker.NS).attrib.clear()
        self.assertIn('BORDER',self.codes(self.fixture(change)))
    def test_body_fill(self):
        def change(st,sh):st.find('m:fills',checker.NS)[0].find('m:patternFill',checker.NS).set('patternType','solid')
        self.assertIn('BODY_FILL',self.codes(self.fixture(change)))
    def test_merged_perimeter(self):
        self.assertTrue(checker.review(self.fixture(merged=True),baseline='gripper')['static_format_passed'])
        def change(st,sh):
            for c in sh.findall('.//m:c',checker.NS):
                if c.get('r')=='B4':c.set('s','0')
        self.assertIn('BORDER',self.codes(self.fixture(change,True)))
    def test_missing_and_unknown_sheet(self):
        p=self.fixture()
        with self.assertRaises(ValueError):checker.review(p,['missing'],baseline='gripper')
        self.assertTrue(checker.review(p,baseline='gripper',mapping={'串口指令测试结果':'unknown'})['unresolved'])
    def test_changed_header(self):
        def change(st,sh):sh.find('.//m:c/m:is/m:t',checker.NS).text='不同字段'
        self.assertIn('FORMAT_FIELD',self.codes(self.fixture(change)))
    def team_case(self,unknown=False,bad_font=False):
        def change(st,sh):
            for row in sh.findall('m:sheetData/m:row',checker.NS):
                for c in list(row):
                    if checker.xy(c.get('r'))[1]>3:row.remove(c)
                    else:
                        rn,col=checker.xy(c.get('r'))
                        if rn==1:
                            c.find('m:is/m:t',checker.NS).text={1:'编号',2:'测试目的',3:'未知自定义字段' if unknown else '优先级'}[col]
                        else:c.set('s','2' if col==2 else '1')
            if bad_font:st.find('m:fonts',checker.NS)[1].find('m:sz',checker.NS).set('val','11')
        path=self.fixture(change)
        with zipfile.ZipFile(path) as z:entries={n:z.read(n) for n in z.namelist()}
        wb=E.fromstring(entries['xl/workbook.xml']);wb.find('m:sheets/m:sheet',checker.NS).set('name','任意软件功能')
        entries['xl/workbook.xml']=E.tostring(wb)
        with zipfile.ZipFile(path,'w') as z:
            for n,b in entries.items():z.writestr(n,b)
        return path
    def test_team_non_gripper_and_reordered_fields(self):
        p=self.team_case();before=p.read_bytes();r=checker.review(p,baseline='team')
        self.assertTrue(r['static_format_passed'],r['issues']);self.assertFalse(r['unresolved'],r['issues']);self.assertGreater(r['checked_cells'],0);self.assertEqual(before,p.read_bytes())
    def test_team_unknown_field_does_not_claim_complete(self):
        r=checker.review(self.team_case(unknown=True),baseline='team')
        self.assertTrue(r['unresolved']);self.assertIn('UNMAPPED_FIELD',{i['code'] for i in r['issues']});self.assertGreater(r['checked_cells'],0)
    def test_team_detects_font_error_without_gripper_name(self):
        r=checker.review(self.team_case(bad_font=True),baseline='team')
        self.assertFalse(r['static_format_passed']);self.assertIn('FONT_SZ',{i['code'] for i in r['issues']})
    def test_team_explicit_layout(self):
        p=self.team_case();r=checker.review(p,baseline='team',layouts={'任意软件功能':{'header_rows':1,'fields':{'A':'编号','B':'测试目的','C':'优先级'}}})
        self.assertTrue(r['static_format_passed']);self.assertFalse(r['unresolved'])

    def test_cli_defaults_to_team_for_other_project(self):
        import subprocess
        p=self.team_case();report=p.parent/'report.json'
        run=subprocess.run([sys.executable,'-X','utf8',str(SKILL/'scripts/review_format.py'),'--workbook',str(p),'--sheet','任意软件功能','--report',str(report)],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(report.read_text(encoding='utf-8'))
        self.assertEqual(result['baseline'],'team');self.assertEqual(result['field_mapping']['任意软件功能']['B'],'测试目的')

    def test_python_default_is_team(self):
        r=checker.review(self.team_case())
        self.assertEqual(r['baseline'],'team');self.assertGreater(r['checked_cells'],0);self.assertFalse(r['unresolved'])
    def test_incorrect_layout_cannot_pass(self):
        r=checker.review(self.team_case(),layouts={'任意软件功能':{'header_rows':1,'fields':{'A':'优先级','B':'测试目的','C':'编号'}}})
        self.assertFalse(r['static_format_passed']);self.assertIn('FORMAT_FIELD',{i['code'] for i in r['issues']})
    def test_alias_layout_checks_actual_header(self):
        p=self.team_case(unknown=True)
        layout={'任意软件功能':{'header_rows':1,'fields':{'A':'编号','B':'测试目的','C':{'label':'未知自定义字段','role':'优先级'}}}}
        r=checker.review(p,layouts=layout)
        self.assertTrue(r['static_format_passed']);self.assertFalse(r['unresolved'])
        layout['任意软件功能']['fields']['C']['label']='不存在的字段'
        self.assertFalse(checker.review(p,layouts=layout)['static_format_passed'])
    def test_unknown_layout_sheet_rejected(self):
        with self.assertRaises(ValueError):checker.review(self.team_case(),layouts={'错名Sheet':{'header_rows':1,'fields':{'A':'编号'}}})

if __name__=='__main__':unittest.main()
