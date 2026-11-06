# 需要：pip install openai      （用 OpenAI-compatible SDK 与 Ollama 通信）
# 运行前：ollama pull gemma4:e4b && ollama serve
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama 不检查这个占位值
)

prompt = """目标：将客服留言分到 billing、bug 或 other。
资料：<input_data>我被扣款两次，请帮我查。</input_data>
规则：只根据资料分类；不知道时选 other。
输出：只返回一个小写标签。"""

r = client.chat.completions.create(
    model="gemma4:e4b",
    max_tokens=100,
    temperature=0.0,
    messages=[{"role": "user", "content": prompt}],
)

# === 自我验证 ===
choice = r.choices[0]
text = choice.message.content or ""
print("响应：", text)
print("usage:", r.usage)

assert choice.finish_reason == "stop" and text.strip(), f"Expected complete non-empty response; got finish_reason={choice.finish_reason!r}"
assert r.usage.completion_tokens > 0, "output token 应大于 0"
print("✅ 练习 1 通过 — Ollama gemma4:e4b 已能在本地响应，每次 $0")