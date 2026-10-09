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
if __name__=='__main__':unittest.main()
