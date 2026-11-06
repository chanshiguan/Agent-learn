"""Stage 6 练习 5 自我验证 — MemoryStore + maybe_remember_fact 逻辑。
"""

# 本组测试围绕以下行为检查正反例：保存事实后按问题检索，再放入模型上下文；持久化、授权与删除是不同能力。

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

# 不同终端对标准输出对象的实现不同，先确认支持重设编码，再开启中文输出，避免测试替身上报属性错误。
if hasattr(sys.stdout, "reconfigure"):
    # 统一终端的中文编码；无法编码的字符只替换显示，不能让日志打印失败掩盖实际业务结果。
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from starter import MemoryStore, chat, maybe_remember_fact


class FakeCollection:
    def __init__(self):
        self.rows: dict[str, str] = {}

    def count(self):
        return len(self.rows)

    def add(self, ids, documents):
        self.rows.update(dict(zip(ids, documents)))

    def get(self):
        return {"ids": list(self.rows), "documents": list(self.rows.values())}

    def query(self, query_texts, n_results):
        words = set(re.findall(r"[a-z]+", query_texts[0].lower()))
        # 给离线替身补充少量固定关联，让测试能构造相关与不相关结果；它不是通用语义理解。
        aliases = {"language": "python", "programming": "python", "recommend": "prefer"}
        words |= {aliases[word] for word in words if word in aliases}
        ranked = sorted(
            self.rows.values(),
            key=lambda text: len(words & set(re.findall(r"[a-z]+", text.lower()))),
            reverse=True,
        )[:n_results]
        return {"documents": [ranked]}


class FakeClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def get_or_create_collection(self, name, embedding_function=None):
        return self.collections.setdefault(name, FakeCollection())


FAKE_CLIENT = FakeClient()


class TinyEmbeddingFunction:
    """用固定规则生成向量，只验证真实数据库的保存与重启读取，不验证语义检索质量。"""

    def __call__(self, input):
        vectors = []
        for text in input:
            lowered = text.lower()
            vectors.append([
                float("python" in lowered),
                float("taipei" in lowered),
                float("language" in lowered or "prefer" in lowered),
                1.0,
            ])
        return vectors

    @staticmethod
    def name():
        return "stage06-tiny-test"

    def get_config(self):
        return {}

    @staticmethod
    def build_from_config(config):
        return TinyEmbeddingFunction()


def fresh_memory():
    """每个 test 用独立 collection，不下载 embedding model。"""
    name = f"test_{len(FAKE_CLIENT.collections)}"
    return MemoryStore(
        collection_name=name,
        client=FAKE_CLIENT,
        # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
        embedding_function=lambda rows: rows,
    )


def make_mock_llm(answer: str = "ok"):
    llm = MagicMock()
    msg = SimpleNamespace(content=answer)
    llm.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=msg)]
    )
    return llm


def test_memory_remember_and_recall():
    mem = fresh_memory()
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    mem.remember("用户更喜欢 Python，而不是 JavaScript。")
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    mem.remember("用户住在台北。")
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    mem.remember("香蕉是黄色的。")  # 无关问题用于检查记忆是否意外改变当前任务

    # 先按当前问题取回相关记忆，再提供给模型；把所有历史无差别塞入提示会增加噪声与泄露范围。
    recalled = mem.recall("用户喜欢什么编程语言", top_k=2)
    assert any("Python" in m for m in recalled), f"预期 recall Python、得到 {recalled}"
    print("✅ test_memory_remember_and_recall")


def test_memory_empty_recall():
    mem = fresh_memory()
    # 先按当前问题取回相关记忆，再提供给模型；把所有历史无差别塞入提示会增加噪声与泄露范围。
    assert mem.recall("anything") == []
    print("✅ test_memory_empty_recall")


def test_reopening_same_store_keeps_memory():
    client = FakeClient()
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    first = MemoryStore(client=client, embedding_function=lambda rows: rows)
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    first.remember("用户住在台北。")
    # embedding_function：统一负责把文档与查询转换成向量；换它之后需要重新建立索引，旧向量不能直接复用。
    reopened = MemoryStore(client=client, embedding_function=lambda rows: rows)
    assert "用户住在台北。" in reopened.all()
    print("✅ test_reopening_same_store_keeps_memory")


def test_persistent_store_survives_new_process():
    with tempfile.TemporaryDirectory(prefix="stage06-memory-") as temp_dir:
        child_code = textwrap.dedent(
            """
            import sys
            from starter import MemoryStore

            class TinyEmbeddingFunction:
                def __call__(self, input):
                    return [[float('python' in text.lower()), 0.0, 1.0, 1.0] for text in input]
                @staticmethod
                def name():
                    return 'stage06-tiny-test'
                def get_config(self):
                    return {}
                @staticmethod
                def build_from_config(config):
                    return TinyEmbeddingFunction()

            memory = MemoryStore(path=sys.argv[1], embedding_function=TinyEmbeddingFunction())
            if sys.argv[2] == 'write':
                memory.remember('用户喜欢 Python。')
            else:
                assert '用户喜欢 Python。' in memory.all()
            """
        )
        for action in ("write", "read"):
            result = subprocess.run(
                [sys.executable, "-c", child_code, temp_dir, action],
                # cwd：限定命令的工作目录，防止相对路径落到用户的其他项目或错误位置。
                cwd=Path(__file__).parent,
                # capture_output：保存子进程的真实输出，后续报告才能引用实际结果而不是声称“已运行”。
                capture_output=True,
                # text：按文本而不是字节接收子进程输出，便于检查断言和生成可读报告。
                text=True,
                # timeout：限制当前等待操作的时长，避免它一直阻塞；这个局部超时不等于整个 Agent 的总时限。
                timeout=30,
            )
            assert result.returncode == 0, result.stderr
    print("✅ test_persistent_store_survives_new_process")


def test_remember_deduplicates_exact_fact():
    mem = fresh_memory()
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    first_id = mem.remember("用户喜欢 Python。")
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    second_id = mem.remember("用户喜欢 Python。")
    assert first_id == second_id
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert mem.collection.count() == 1
    print("✅ test_remember_deduplicates_exact_fact")


def test_maybe_remember_fact_triggers_on_self_statements():
    mem = fresh_memory()
    fid = maybe_remember_fact("我住在台北", mem)
    assert fid is not None
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert mem.collection.count() == 1
    print("✅ test_maybe_remember_fact_triggers_on_self_statements")


def test_maybe_remember_fact_skips_non_self_statements():
    mem = fresh_memory()
    fid = maybe_remember_fact("天气怎么样？", mem)
    assert fid is None
    # 先确认集合中有多少记录，用于处理空库和限制返回数量，避免对空索引盲目查询。
    assert mem.collection.count() == 0
    print("✅ test_maybe_remember_fact_skips_non_self_statements")


def test_chat_uses_memory_in_prompt():
    """chat 应该把 recalled memory 塞进 system prompt。"""
    mem = fresh_memory()
    # 把经本例规则允许的事实写入记忆；是否能保存这类信息仍要在入口确定，不能见到文本就永久保存。
    mem.remember("用户更喜欢 Python，而不是 JavaScript。")

    llm = make_mock_llm("我推荐 Python。")
    result = chat("请推荐一种编程语言。", mem, llm=llm)

    # mock 看 create() 收到的 messages
    call_args = llm.chat.completions.create.call_args
    system_msg = call_args.kwargs["messages"][0]["content"]
    assert "用户更喜欢 Python，而不是 JavaScript。" in system_msg, "system prompt 应含 memory"
    assert "Python" in result["recalled"][0]
    print("✅ test_chat_uses_memory_in_prompt")


if __name__ == "__main__":
    test_memory_remember_and_recall()
    test_memory_empty_recall()
    test_reopening_same_store_keeps_memory()
    test_persistent_store_survives_new_process()
    test_remember_deduplicates_exact_fact()
    test_maybe_remember_fact_triggers_on_self_statements()
    test_maybe_remember_fact_skips_non_self_statements()
    test_chat_uses_memory_in_prompt()
    print("\n🎉 全部通过 — long-term memory 逻辑正确")
