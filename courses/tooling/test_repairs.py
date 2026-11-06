"""回归测试：评分漏洞、任务对应、持久化与错误路径。"""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def module(name, relative):
    path=ROOT/relative
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


evalmod=module('repaired_eval','capstone-b/examples/evaluate.py')
cap_a=module('repaired_cap_a','capstone-a/examples/validate.py')
rag6=module('repaired_rag6','06-memory-rag/examples/grounded_rag.py')
review=module('repaired_review','A2-cli-workflow/examples/review.py')
production=module('repaired_production','07-multi-agent-production/examples/production_case.py')


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.case=json.loads((ROOT/'capstone-b/examples/eval_cases.json').read_text())['development'][0]
        self.good=evalmod.run(self.case['question'])

    def test_exact_evidence_passes(self):
        self.assertEqual(evalmod.grade(self.case,self.good)['status'],'PASS')

    def test_negation_never_auto_passes(self):
        self.good['answer']='以下说法都是错误的：09:00；18:00'
        self.assertEqual(evalmod.grade(self.case,self.good)['status'],'NEEDS_REVIEW')

    def test_extra_false_fact_never_auto_passes(self):
        self.good['answer']+='月亮是奶酪。'
        self.assertEqual(evalmod.grade(self.case,self.good)['status'],'NEEDS_REVIEW')

    def test_fake_trace_fails(self):
        self.good['trace'][0]['result'][0]['text']='伪造文本'
        self.assertEqual(evalmod.grade(self.case,self.good)['status'],'FAIL')

    def test_missing_trace_fails(self):
        self.good['trace']=[]
        self.assertEqual(evalmod.grade(self.case,self.good)['status'],'FAIL')

    def test_wrong_owner_fails(self):
        data=json.loads((ROOT/'capstone-a/examples/reference-draft.json').read_text())
        data['actions'][0]['owner']='小王'
        with self.assertRaises(ValueError):cap_a.validate(data)

    def test_teacher_incomplete_work_fails(self):
        checker=module('teacher_work','branch-teacher/examples/check_work.py')
        self.assertEqual(checker.check({'draft':'没有教案','claims':[]})['status'],'FAIL')

    def test_teacher_reference_waits_for_human(self):
        checker=module('teacher_work','branch-teacher/examples/check_work.py')
        data=json.loads((ROOT/'branch-teacher/examples/reference-work.json').read_text())
        self.assertEqual(checker.check(data)['status'],'NEEDS_REVIEW')
        del data['original_activity']['exit_ticket']
        self.assertEqual(checker.check(data)['status'],'FAIL')

    def test_complete_document_passes(self):
        self.assertEqual(review.review(ROOT/'A2-cli-workflow/examples/sample.md')['status'],'PASS')

    def test_empty_section_fails(self):
        self.assertEqual(review.review(ROOT/'A2-cli-workflow/examples/empty.md')['status'],'FAIL')

    def test_readme_complete_still_requires_content_review(self):
        checker=module('readme_checker','05-claude-code-ecosystem/examples/check_readme.py')
        result=checker.check(ROOT/'05-claude-code-ecosystem/examples/demo-data/README.md')
        self.assertEqual(result['status'],'NEEDS_REVIEW')
        self.assertEqual(result['missing'],[])

    def test_readme_empty_or_missing_fails(self):
        checker=module('readme_checker','05-claude-code-ecosystem/examples/check_readme.py')
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'README.md'
            self.assertEqual(checker.check(path)['status'],'FAIL')
            path.write_text(''.join('## '+name+'\n\n' for name in checker.REQUIRED))
            self.assertEqual(checker.check(path)['missing'],list(checker.REQUIRED))


class WorkflowTests(unittest.TestCase):
    def test_rag_refs_and_private_data(self):
        docs=rag6.retrieve('主办方取消课程退款','alice')
        self.assertTrue({'refund','exception'}.issubset({d['id'] for d in docs}))
        self.assertEqual(rag6.retrieve('Bob私人预约编号','alice'),[])
        self.assertEqual(rag6.retrieve('火星天气','alice'),[])
        self.assertEqual(rag6.retrieve('火星天气','alice',True),[])
        answer=rag6.generate(docs,'退款')
        self.assertTrue(all(c['source_id'] in {d['id'] for d in docs} for c in answer['claims']))

    def test_memory_preference_changes_display_and_deletion(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'memory.db'
            store=rag6.MemoryStore(db)
            store.put('alice','answer_style','分步解释',consent=True,expected_version=0,source='虚构选择')
            store.close()
            result=rag6.run('报名截止时间','alice',db)
            self.assertTrue(result['display_answer'].startswith('1. '))
            store=rag6.MemoryStore(db);store.delete('alice','answer_style');store.close()
            result=rag6.run('报名截止时间','alice',db)
            self.assertIsNone(result['preference'])
            self.assertEqual(result['display_answer'],result['answer'])

    def test_source_updated_after_approval_requires_new_review(self):
        with tempfile.TemporaryDirectory() as d:
            production.prepare(d,'原始资料')
            (Path(d)/'draft.json').write_text('{}')
            with self.assertRaises(ValueError):production.resume(d,'approve')

    def test_repeated_resume_has_one_effect(self):
        with tempfile.TemporaryDirectory() as d:
            production.prepare(d,'原始资料')
            production.resume(d,'approve');production.resume(d,'approve')
            self.assertEqual(len(json.loads((Path(d)/'ledger.json').read_text())['executed']),1)

    def test_rejection_has_no_effect(self):
        with tempfile.TemporaryDirectory() as d:
            production.prepare(d,'原始资料');production.resume(d,'reject')
            path=Path(d)/'ledger.json'
            self.assertTrue(not path.exists() or json.loads(path.read_text())['executed']==[])

    def test_graph_cross_process_and_reject(self):
        python=ROOT/'.venv-verification/bin/python'
        if not python.exists():self.skipTest('缺专用验证环境')
        with tempfile.TemporaryDirectory() as d:
            command=[str(python),str(ROOT/'04-agent-frameworks/examples/summary_workflow.py'),'--db',str(Path(d)/'graph.db'),'--thread','test']
            first=json.loads(subprocess.check_output(command,text=True))
            second=json.loads(subprocess.check_output(command+['--decision','reject'],text=True))
            self.assertEqual(first['state']['status'],'awaiting_review')
            self.assertEqual(second['state']['status'],'rejected')
            self.assertFalse(second['state']['published'])
            repeated=subprocess.run(command+['--decision','accept'],capture_output=True)
            self.assertNotEqual(repeated.returncode,0)


class ContentTests(unittest.TestCase):
    def test_original_branch_tasks_preserved(self):
        teacher=json.loads((ROOT/'branch-teacher/examples/reference-work.json').read_text())
        self.assertEqual(len(teacher['original_activity']['exit_ticket']),2)
        self.assertEqual(len(teacher['original_activity']['facts']),3)
        self.assertEqual(len(teacher['original_student_groups']),3)
        for slug,field in [('branch-researcher','original_three_questions'),('branch-knowledge-worker','original_meeting'),('branch-everyday-users','original_message')]:
            self.assertIn(field,json.loads((ROOT/slug/'examples/reference-work.json').read_text()))

    def test_second_lesson_and_shared_assets_unchanged(self):
        import hashlib
        manifest=ROOT.parent/'.scratch/remaining-courses/repair/protected.json'
        observed=json.loads(manifest.with_name('concurrent-changes.json').read_text())
        for relative,digest in json.loads(manifest.read_text()).items():
            if relative.startswith('courses/03-tool-use-and-hello-agent/'):
                continue  # 用户本轮已授权润色第三课；保留原审查快照，不改历史证据。
            if Path(relative).name == '.DS_Store':
                continue  # Finder 元数据不属于教材内容，浏览目录会自动改变。
            expected=observed.get(relative,{}).get('observed',digest)
            self.assertEqual(hashlib.sha256((ROOT.parent/relative).read_bytes()).hexdigest(),expected,relative)


if __name__=='__main__':unittest.main()
