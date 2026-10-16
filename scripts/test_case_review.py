import importlib.util, json, subprocess, sys, tempfile, unittest
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SKILL=ROOT/'skills/testcase-iteration'
spec=importlib.util.spec_from_file_location('case_review',SKILL/'scripts/review_workbook.py');reviewer=importlib.util.module_from_spec(spec);spec.loader.exec_module(reviewer)
class CaseReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.templates=reviewer.read_workbook(SKILL/'assets/templates/通用软件测试用例模板_v1.0.xlsx')
    def case(self):
        s=deepcopy(self.templates['功能模块（复制后改名）'])
        s['cells'].update({'A3':'CASE-001','B3':'配置','C3':'验证缺失配置时提示','D3':'P1','E3':'/','F3':'1.删除副本配置 2.启动','G3':'按已确认需求提示且不启动','H1':'模拟环境A','L1':'模拟环境B'})
        return s
    def check(self,s,mode='design'):
        return reviewer.inspect_sheet('配置模块',s,self.templates['功能模块（复制后改名）'],mode)
    def codes(self,s,mode='design'):return {i['code'] for i in self.check(s,mode)['issues']}
    def test_original_templates_read_only(self):
        import hashlib
        manifest=json.loads((SKILL/'references/source-manifest.json').read_text(encoding='utf-8'))
        for category,name in reviewer.TEMPLATES.items():
            p=SKILL/'assets/templates'/name
            source=next(i for i in manifest['files'] if i['name']==name)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),source['sha256'])
            result=reviewer.review(p,category,allow_empty=True)
            self.assertTrue(result['source_unchanged']);self.assertTrue(result['static_checks_passed'],result['issues']);self.assertFalse(result['unresolved'])
    def test_clean_case_with_environment_rename(self):self.assertEqual(self.check(self.case())['issues'],[])
    def test_missing_purpose_and_priority(self):
        s=self.case();s['cells']['C3']='';s['cells']['D3']='P4'
        self.assertTrue({'REQUIRED','PRIORITY'}<=self.codes(s))
    def test_header_drift(self):
        s=self.case();s['cells']['G1']='实际结果';self.assertIn('HEADER',self.codes(s))
    def test_extra_column_is_reported(self):
        s=self.case();s['cells']['Q1']='测试方法';self.assertIn('HEADER_EXTRA',self.codes(s))
    def test_default_template_reports_body_and_formula_outside_header(self):
        for formula in (False,True):
            s=self.case();s['cells']['Q3']='' if formula else 'additional business data'
            if formula:s['formulas'].append('Q3')
            self.assertIn('UNMAPPED_COLUMN',self.codes(s))

    def test_identity_fields_have_separate_duplicate_namespaces(self):
        s={'cells':{'A1':'用例编号','B1':'指令序号','C1':'测试步骤','D1':'预期结果',
                    'A2':'1','B2':'1','C2':'invoke','D2':'expected'},'merges':[],'formulas':[]}
        layout={'header_rows':1,'fields':{'A':'用例编号','B':'指令序号','C':'测试步骤','D':'预期结果'},
                'required_roles':['用例编号','指令序号','测试步骤','预期结果'],'header_merges':[]}
        template=reviewer.approved_template(s,layout)
        def duplicates():
            return [i for i in reviewer.inspect_sheet('IDs',s,template)['issues'] if i['code']=='DUPLICATE_ID']
        self.assertEqual(duplicates(),[])
        s['cells'].update({'A3':'2','B3':'2','C3':'invoke again','D3':'expected again'})
        self.assertEqual(duplicates(),[])
        s['cells']['B3']='1'
        self.assertEqual([i['cell'] for i in duplicates()],['B3'])
        s['merges'].append('B2:B3');s['cells']['B3']=''
        self.assertEqual(duplicates(),[])

    def test_stale_pass_is_rejected_in_design(self):
        s=self.case();s['cells'].update({'H3':'旧版正常','I3':'Pass'});self.assertIn('DESIGN_RESULT',self.codes(s))
    def test_unexecuted_has_no_actual(self):
        s=self.case();s['cells'].update({'H3':'正常','I3':'Not Executed'});self.assertIn('UNEXECUTED_RESULT',self.codes(s,'executed'))
    def test_failure_requires_evidence(self):
        s=self.case();s['cells'].update({'H3':'错误','I3':'Fail'});self.assertIn('EVIDENCE',self.codes(s,'executed'))
    def test_duplicate_id(self):
        s=self.case()
        for c in 'ABCDEFG':s['cells'][c+'4']=s['cells'][c+'3']
        self.assertIn('DUPLICATE_ID',self.codes(s))
    def test_merged_description_inherits_but_result_must_be_independent(self):
        s=self.case()
        for c in 'ABCDEFG':s['cells'][c+'4']=s['cells'][c+'3']
        s['cells']['C4']='验证恢复';s['merges'].extend(['A3:A4','B3:B4']);s['cells']['A4']='';s['cells']['B4']=''
        self.assertNotIn('DUPLICATE_ID',self.codes(s));self.assertEqual(self.check(s)['case_items'],2)
        s['merges'].append('H3:H4');self.assertIn('MERGED_JUDGEMENT',self.codes(s))
    def test_unknown_contract_not_ready(self):
        s=self.case();s['cells']['G3']='待确认返回值';self.assertIn('UNCONFIRMED',self.codes(s))
    def test_skip_examples_and_unsupported_sheet(self):
        p=SKILL/'assets/templates/通用软件测试用例模板_v1.0.xlsx'
        result=reviewer.review(p,'general',{'专项测试':'自定义未知模板'},allow_empty=True)
        self.assertIn('UNMAPPED_SHEET',{i['code'] for i in result['issues']});self.assertTrue(result['unresolved'])
        self.assertNotIn('填写说明与示例',[s['sheet'] for s in result['sheets']])
    def test_cli_refuses_overwriting_workbook(self):
        p=SKILL/'assets/templates/通用软件测试用例模板_v1.0.xlsx';before=p.read_bytes()
        result=subprocess.run([sys.executable,'-X','utf8',str(SKILL/'scripts/review_workbook.py'),'--workbook',str(p),'--category','general','--report',str(p)],capture_output=True)
        self.assertEqual(result.returncode,2);self.assertEqual(p.read_bytes(),before)
    def mapped_case(self):
        sheet={'cells':{'A1':'期望描述','B1':'执行判定','C1':'案例号','D1':'操作记录','E1':'观察值','F1':'凭证','A2':'1.返回已批准值','C2':'Q-01','D2':'1.调用已批准查询'},'merges':[],'formulas':[]}
        layout={'header_rows':1,'fields':{'A':{'label':'期望描述','role':'预期结果'},'B':{'label':'执行判定','role':'执行状态'},'C':{'label':'案例号','role':'用例编号'},'D':{'label':'操作记录','role':'测试步骤'},'E':{'label':'观察值','role':'实际结果'},'F':{'label':'凭证','role':'测试证据'}},'required_roles':['用例编号','测试步骤','预期结果'],'header_merges':[],'execution_groups':[{'status':'B','actual':'E','evidence':'F'}]}
        return sheet,layout
    def mapped_review(self,s,l,mode='design'):
        return reviewer.inspect_sheet('模拟软件',s,reviewer.approved_template(s,l),mode)
    def test_approved_aliases_reorder_and_no_write(self):
        s,l=self.mapped_case();before=deepcopy(s)
        self.assertEqual(self.mapped_review(s,l)['issues'],[]);self.assertEqual(s,before)
    def test_mapped_execution_group_uses_declared_columns(self):
        s,l=self.mapped_case();s['cells'].update({'B2':'Fail','E2':'观察到错误'})
        issues=self.mapped_review(s,l,'executed')['issues']
        self.assertIn('F2',{i['cell'] for i in issues if i['code']=='EVIDENCE'})
        s['cells']['F2']='模拟记录-01';self.assertEqual(self.mapped_review(s,l,'executed')['issues'],[])
        s['cells']['B2']='Not Executed';self.assertIn('E2',{i['cell'] for i in self.mapped_review(s,l,'executed')['issues'] if i['code']=='UNEXECUTED_RESULT'})
    def test_missing_mapping_and_required_role_are_visible(self):
        s,l=self.mapped_case();del l['fields']['A']
        codes={i['code'] for i in self.mapped_review(s,l)['issues']}
        self.assertTrue({'UNMAPPED_COLUMN','MISSING_ROLE'}<=codes)
    def test_wrong_alias_label_and_known_role_rebinding(self):
        s,l=self.mapped_case();l['fields']['C']['label']='不存在'
        self.assertIn('HEADER',{i['code'] for i in self.mapped_review(s,l)['issues']})
        l['fields']['C']={'label':'优先级','role':'用例编号'}
        with self.assertRaises(ValueError):reviewer.approved_template(s,l)
    def test_missing_execution_group_does_not_guess_adjacent_column(self):
        s,l=self.mapped_case();l['execution_groups']=[]
        self.assertIn('UNMAPPED_EXECUTION',{i['code'] for i in self.mapped_review(s,l)['issues']})
    def test_unknown_role_and_empty_contract_are_not_accepted(self):
        s,l=self.mapped_case();l['fields']['F']['role']='未知字段';l['execution_groups']=[]
        self.assertIn('UNMAPPED_ROLE',{i['code'] for i in self.mapped_review(s,l)['issues']})
        l['required_roles']=[]
        with self.assertRaises(ValueError):reviewer.approved_template(s,l)
    def test_layout_cli_preserves_workbook_and_checks_selected_sheet(self):
        import zipfile, xml.etree.ElementTree as ET
        s,l=self.mapped_case()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);book=root/'cases.xlsx';ns=reviewer.NS['m']
            sh=ET.Element('{'+ns+'}worksheet');data=ET.SubElement(sh,'{'+ns+'}sheetData')
            for rownum in (1,2):
                row=ET.SubElement(data,'{'+ns+'}row',r=str(rownum))
                for ref,value in s['cells'].items():
                    if reviewer.xy(ref)[0]==rownum:
                        c=ET.SubElement(row,'{'+ns+'}c',r=ref,t='inlineStr');i=ET.SubElement(c,'{'+ns+'}is');ET.SubElement(i,'{'+ns+'}t').text=value
            wb=ET.Element('{'+ns+'}workbook');sheets=ET.SubElement(wb,'{'+ns+'}sheets');sn=ET.SubElement(sheets,'{'+ns+'}sheet',name='模拟软件',sheetId='1');sn.set(reviewer.R,'r1')
            rels=ET.Element('Relationships');ET.SubElement(rels,'Relationship',Id='r1',Target='worksheets/sheet1.xml')
            with zipfile.ZipFile(book,'w') as z:
                for n,v in [('xl/workbook.xml',wb),('xl/_rels/workbook.xml.rels',rels),('xl/worksheets/sheet1.xml',sh)]:z.writestr(n,ET.tostring(v))
            layout=root/'layout.json';layout.write_text(json.dumps({'模拟软件':l}),encoding='utf-8');out=root/'out.json';before=book.read_bytes()
            cmd=[sys.executable,'-X','utf8',str(SKILL/'scripts/review_workbook.py'),'--workbook',str(book),'--category','general','--layout',str(layout),'--sheet','模拟软件','--report',str(out)]
            run=subprocess.run(cmd,capture_output=True);self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads(out.read_text(encoding='utf-8'));self.assertTrue(result['scope_complete']);self.assertEqual(result['sheets'][0]['case_items'],1);self.assertEqual(book.read_bytes(),before)

    def test_unpaired_evidence_column_is_not_silently_ignored(self):
        s,l=self.mapped_case();del l['execution_groups'][0]['evidence']
        self.assertIn('UNMAPPED_EXECUTION',{i['code'] for i in self.mapped_review(s,l)['issues']})

if __name__=='__main__':unittest.main()
