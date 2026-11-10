# 目的：测试描述业务结果：旧更新不能覆盖、重复确认不重复写、旧预览不能批准新内容。
# 预期：一旦以后改坏事务或版本检查，测试会失败。
import unittest
import uuid
from companion import actions,state


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        state.initialize()
        self.actor=state.Actor("demo","test-"+uuid.uuid4().hex)

    def test_old_progress_cannot_replace_new(self):
        session=state.create_session(self.actor)
        state.update_session(self.actor,session,progress=3)
        with self.assertRaises(ValueError):
            state.update_session(self.actor,session,progress=1)
        self.assertEqual(state.get_session(self.actor,session["id"])["progress"],3)

    def test_confirming_twice_writes_one_note(self):
        item=actions.draft(self.actor,"note","只保存一次",uuid.uuid4().hex)
        for _ in range(2):
            actions.approve(self.actor,item["id"],item["revision"],item["digest"],True)
        self.assertEqual(len(actions.notes(self.actor)),1)

    def test_changed_draft_rejects_old_confirmation(self):
        item=actions.draft(self.actor,"note","旧正文",uuid.uuid4().hex)
        actions.revise(self.actor,item["id"],"新正文")
        with self.assertRaises(ValueError):
            actions.approve(self.actor,item["id"],item["revision"],item["digest"],True)


if __name__=="__main__":
    unittest.main()
