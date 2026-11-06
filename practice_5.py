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

examples = """范例：
输入：信用卡又扣了一次
输出：billing

输入：提交表单后没有反应
输出：bug

输入：可以更改联系邮箱吗
输出：other"""

cases = [
    ("我被扣款两次", "billing"),
    ("发票上的金额不对", "billing"),
    ("按下登录后画面全白", "bug"),
    ("更新后一直闪退", "bug"),
    ("你们周末上班吗", "other"),
    ("谢谢你帮我处理", "other"),
]

valid_labels = {"billing", "bug", "other"}
score = 0
all_formats_valid = True

for index, (message, expected) in enumerate(cases, start=1):
    prompt = f"""目标：将客服留言分到 billing、bug 或 other。
资料：<input_data>{message}</input_data>
规则：只根据资料分类；不知道时选 other。
{examples}
输出：只返回一个小写标签。"""

    response = client.chat.completions.create(
        model="gemma4:e4b",
        max_tokens=20,
        reasoning_effort="none",
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )

    choice = response.choices[0]
    answer = (choice.message.content or "").strip()
    format_valid = answer in valid_labels
    correct = answer == expected

    score += int(correct)
    all_formats_valid = all_formats_valid and format_valid

    print(f"{index}. {message}")
    print(f"   模型输出：{answer or '[空响应]'}")
    print(f"   正确标签：{expected}")
    print(f"   结果：{'✓' if correct else '✗'}")

    if choice.finish_reason != "stop":
        print(f"   警告：输出未正常完成（finish_reason={choice.finish_reason}）")

print(f"\nFew-Shot 得分：{score} / {len(cases)}")
print(f"标签格式是否全部一致：{'是' if all_formats_valid else '否'}")
