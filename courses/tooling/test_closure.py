"""第二次补齐：课程对应、框架接线、三组实验及失败收据。"""
import asyncio
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PYTHON=ROOT/'.venv-verification/bin/python'


def load(name,path):
    path=ROOT/path
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


rag=load('abc_lab','06-memory-rag/examples/rerank_experiment.py')
sdk=load('sdk_job_lab','05-claude-code-ecosystem/examples/sdk_job.py')


class ClosureTests(unittest.TestCase):
    def test_three_groups_same_questions_and_candidates(self):
        result=rag.experiment()
        self.assertEqual(len(result['rows']),60)
        for index in range(0,60,3):
            a,b,c=result['rows'][index:index+3]
            self.assertEqual(a['question'],c['question'])
            self.assertEqual(b['candidates'],c['candidates'])
            self.assertTrue(set(c['selected'])<=set(c['candidates']))
            self.assertEqual(a['gold'],c['gold'])

    def test_reranker_cannot_invent_evidence(self):
        docs=[{'id':'wrong','text':'这里没有报名规则'}]
        self.assertEqual([row['id'] for row in rag.rerank('报名截止时间',docs)],['wrong'])
        self.assertEqual(rag.rerank('报名截止时间',[]),[])

    def test_private_data_filtered_before_each_variant(self):
        rows=rag.experiment()['rows']
        private=[row for row in rows if row['question']=='Bob私人预约编号']
        self.assertEqual(len(private),3)
        self.assertTrue(all(not row['candidates'] and row['answer']['review']=='REFUSED' for row in private))

    def test_invalid_experiment_sizes(self):
        with self.assertRaises(ValueError):rag.experiment(candidate_k=1,answer_k=5)

    def test_sdk_terminal_states_and_no_fake_session(self):
        with tempfile.TemporaryDirectory() as directory:
            for scenario,status in [('success','NEEDS_REVIEW'),('limit','FAILED'),('timeout','TIMEOUT')]:
                result=asyncio.run(sdk.run(Path(directory)/scenario,scenario=scenario))
                self.assertEqual(result['status'],status)
                self.assertIsNone(result['session_id'])
                if status!='NEEDS_REVIEW':self.assertIsNone(result['answer'])
            with self.assertRaises(ValueError):asyncio.run(sdk.run(Path(directory)/'success'))
            with self.assertRaises(ValueError):asyncio.run(sdk.run(Path(directory)/'success',resume=True))

    def test_graph_dynamic_fanout_and_all_results(self):
        program=ROOT/'04-agent-frameworks/examples/dynamic_workers.py'
        for flags,status in [([], 'FAIL'),(['--fixed'],'PASS')]:
            result=json.loads(subprocess.check_output([str(PYTHON),str(program),*flags],text=True))
            self.assertEqual(result['status'],status)
            self.assertEqual([item['id'] for item in result['checks']],['a','b'])

    def test_real_agents_sdk_control_transfer(self):
        result=json.loads(subprocess.check_output([str(PYTHON),str(ROOT/'04-agent-frameworks/examples/sdk_orchestration.py')],text=True))
        manager,handoff=result['rows']
        self.assertEqual(manager['final_agent'],'manager')
        self.assertEqual(handoff['final_agent'],'specialist')
        self.assertIn('tool_call_output_item',[item['type'] for item in manager['events']])
        self.assertIn('handoff_output_item',[item['type'] for item in handoff['events']])

    def test_workflow_null_is_not_success(self):
        program=ROOT/'05-claude-code-ecosystem/examples/workflow_contract.mjs'
        normal=json.loads(subprocess.check_output(['node',str(program)],text=True))
        failed=json.loads(subprocess.check_output(['node',str(program),'cancel'],text=True))
        self.assertEqual(normal['reports'][1]['result']['missing'],['运行示例'])
        self.assertEqual(failed['status'],'INCOMPLETE')
        self.assertEqual(len(failed['reports']),2)
        self.assertIsNone(failed['reports'][1]['result'])

    def test_every_direct_required_link_has_explicit_entry(self):
        from catalog import COURSES
        actual=json.loads((ROOT/'reference/required-readings.json').read_text())
        for slug,_,_,source,*_ in COURSES:
            text=(ROOT/'_sources/upstream'/source).read_text()
            sections=[s for s in re.split(r'(?=^## )',text,flags=re.M) if re.match(r'##[^\n]*(必读|必修阅读|必讀)',s)]
            if not sections:continue
            section=sections[0].split('<details')[0] if slug=='07-multi-agent-production' else sections[0]
            lines='\n'.join(line for line in section.splitlines() if re.match(r'^\s*(?:\d+\.|-)\s+',line))
            urls=set(re.findall(r'\]\((https?://[^\s)]+)\)',lines))
            self.assertEqual(urls,{row['source'] for row in actual if row['course']==slug and row['source_document']==source},slug)

    def test_direct_branch_readings_have_explicit_entries(self):
        rows=json.loads((ROOT/'reference/required-readings.json').read_text())
        for source in ['resources/advanced-rag.zh-Hans.md','resources/agent-memory.zh-Hans.md']:
            raw=(ROOT/'_sources/upstream'/source).read_text()
            section=next(s for s in re.split(r'(?=^## )',raw,flags=re.M) if re.match(r'##[^\n]*必读',s))
            lines='\n'.join(line for line in section.splitlines() if re.match(r'^\s*\d+\.\s+',line))
            urls=set(re.findall(r'\]\((https?://[^\s)]+)\)',lines))
            self.assertEqual(urls,{row['source'] for row in rows if row['source_document']==source})

    def test_sdk_real_options_and_resume_marker(self):
        script = """import sys,tempfile,json
from pathlib import Path
sys.path.insert(0,'courses/05-claude-code-ecosystem/examples')
from sdk_job import make_options
with tempfile.TemporaryDirectory() as directory:
 p=Path(directory);o=make_options(p)
 assert o.tools==[] and o.strict_mcp_config and o.max_turns==2
 (p/'session.json').write_text(json.dumps({'session_id':'00000000-0000-4000-8000-000000000001'}))
 assert make_options(p,True).resume=='00000000-0000-4000-8000-000000000001'
"""
        subprocess.run([str(PYTHON),'-c',script],cwd=ROOT.parent,check=True)

    def test_source_mapping_does_not_guess_from_domain(self):
        from source_topics import destination
        self.assertIsNone(destination('https://code.claude.com/docs/en/nonexistent-topic'))
        self.assertIn('00-first-session',destination('https://code.claude.com/docs/en/quickstart')[0])


if __name__=='__main__':unittest.main()
