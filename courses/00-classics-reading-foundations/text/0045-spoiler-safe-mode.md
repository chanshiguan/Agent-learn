# 把进度限制贯穿检索和回答

本单元预计 **55—70 分钟**。用时包括阅读、输入代码、运行与一次排错；下载、模型等待及公司评审另计。

接着上一单元[《先核对片段属于哪个阅读范围》](0044-reviewed-ranges.html)继续。使用同一个 `classics-reader/` 项目，保留此前文件与输入资料。

## 为什么不只加一句“别剧透”

生成模型本身可能知道结尾，即使只喂前文，也可能从预训练记忆补出后文。为了给初学项目一个可检查的边界，本课受限模式只展示人工审核范围内的片段，不调用生成模型自由解释。它依赖人工审核质量，仍不能保证绝对无剧透。


## 现在动手写

先读每步的目的，再输入代码。代码块里的缩进属于程序；若同一处拆成多个连续块，写完这些块再检查。不要用课后完整参考文件覆盖自己的进度。

### 第 1 步：在排序前排除未核对或越界片段

讲次不等于剧情进度。只有人工核对且范围不超过当前进度的块才能进入候选。

**写在哪里：**项目根目录下的 `companion/corpus.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    return [c for c in chunks if c["tenant"] == tenant and c["book"] == book]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    # 先限制可见范围再排序，避免先检索出其他租户资料，再让模型自己过滤。
    result = [c for c in chunks if c["tenant"] == tenant and c["book"] == book]
    if progress is not None:
        result = [c for c in result if c.get("range_reviewed") is True
                  and type(c.get("range_end")) is int and 0 <= c["range_end"] <= progress]
    return result
```

**写完后应当怎样：**布尔值不能伪装成数字进度，未知片段被排除。

### 第 2 步：给向量路线加同样的范围规则

先让数据库过滤，再与当前语料允许集合相交，避免不同后端的类型比较语义造成越界。

**写在哪里：**项目根目录下的 `companion/vectors.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
                models.FieldCondition(key="book", match=models.MatchValue(value=book))]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
                models.FieldCondition(key="book", match=models.MatchValue(value=book))]
    if progress is not None:
        required += [models.FieldCondition(key="range_reviewed", match=models.MatchValue(value=True)),
                     models.FieldCondition(key="range_end", range=models.Range(lte=progress))]
```

**写完后应当怎样：**关键词和向量两条路线遵守同一阅读范围。

### 第 3 步：受限阅读只展示已核对证据

即使检索范围正确，生成模型仍可能凭训练知识补后文。受限模式直接返回片段。

**写在哪里：**项目根目录下的 `companion/rag.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
                "citations": [], "insufficient": True, "sources": [], "usage": None}
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
                "citations": [], "insufficient": True, "sources": [], "usage": None}
    if strict:
        # 防剧透模式只展示人工核对范围内的资料，不让生成模型凭已有知识补出后文。
        return {"answer": "已开启受限阅读：本次仅展示下方已核对范围的讲稿片段，请结合片段讨论。",
                "citations": [c["id"] for c in selected], "insufficient": False,
                "sources": selected, "usage": None, "mode": "reviewed-excerpts"}
```

**写完后应当怎样：**strict=True 不调用生成模型，明确说明展示的是受限资料。

### 第 4 步：让来源回查使用同一范围规则

不能只限制搜索列表，却允许读者拿任意来源 ID 直接读正文。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
```

</details>

**先理解：**`from ... import ...` 只引入本步骤要用的名字。以点开头的路径指向 companion 包里的文件；先确认那个文件已在前面的步骤创建。

```python
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
from .corpus import visible
from .files import load
```

**写完后应当怎样：**来源接口与问答接口共享当前会话范围。

### 第 5 步：把会话范围传入检索

范围从已验证归属的会话读取，不接受模型临时改写。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    hits=retrieve(question,actor.tenant,session["book"],method)
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    hits=retrieve(question,actor.tenant,session["book"],method,session["progress"] if session["strict"] else None)
```

**写完后应当怎样：**打开受限模式后，只选允许范围的资料。

### 第 6 步：受限模式丢弃旧上下文

旧聊天可能包含后文，不能仅过滤新检索结果。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    result=answer(question,hits,session["history"])
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    result=answer(question,hits,[] if session["strict"] else session["history"],strict=bool(session["strict"]))
```

**写完后应当怎样：**受限请求不会把过去的普通对话送给模型。

### 第 7 步：不把受限展示混进普通对话

明确保存什么、清除什么，后续恢复也能遵守相同规则。

**写在哪里：**项目根目录下的 `companion/service.py`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```python
    history=(session["history"]+[{"role":"user","content":question},{"role":"assistant","content":result["answer"]}])[-4:]
```

</details>

**先理解：**对照旧段和新段，看本次增加了哪个条件或配置值。它应当只改变上面说明的行为；其余输入与输出继续沿用。

```python
    history=[] if session["strict"] else (session["history"]+[{"role":"user","content":question},{"role":"assistant","content":result["answer"]}])[-4:]
```

**写完后应当怎样：**受限阅读历史为空，切换范围不残留旧答案。

### 第 8 步：写来源回查函数

读取 ID 仍需带本人会话和当前进度，不能把引用链接当成访问凭证。

**写在哪里：**项目根目录下的 `companion/service.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**函数定义先保存一项能力，不会立刻执行函数体。沿着参数、判断、返回值读一遍，再用本单元的调用观察它。

```python
# 目的：读取 ID 仍需带本人会话和当前进度，不能把引用链接当成访问凭证。
# 预期：已失去可见范围的旧引用会被拒绝。
def source(actor, session_id, source_id):
    session = get_session(actor, session_id)
    corpus = load("corpus.json", {"chunks": []})
    allowed = visible(corpus["chunks"], actor.tenant, session["book"], session["progress"] if session["strict"] else None)
    hit = next((c for c in allowed if c["id"] == source_id), None)
    if hit is None:
        raise PermissionError("当前阅读范围内没有此来源。")
    return hit
```

**写完后应当怎样：**已失去可见范围的旧引用会被拒绝。

### 第 9 步：给来源回查加 API

接口复用 service.source，不再写一套可能遗漏条件的 SQL 或检索。

**写在哪里：**项目根目录下的 `companion/app.py`。 在文件末尾另起一行，接着写下面这一段；已有内容保留。

**先理解：**`@app` 装饰器把函数登记为接口。路径决定请求去哪，函数参数决定请求怎样验证；只定义函数不会向模型发请求。

```python
# 目的：接口复用 service.source，不再写一套可能遗漏条件的 SQL 或检索。
# 预期：越界返回403，允许的来源返回正文。
@app.get("/api/sources/{source_id}")
def source(source_id: str, session_id: str, who=Depends(actor)):
    return service.source(who, session_id, source_id)
```

**写完后应当怎样：**越界返回403，允许的来源返回正文。

### 第 10 步：更新页面对受限模式的说明

过滤与回答限制已在本节接通，页面可以准确说明实际行为。

**写在哪里：**项目根目录下的 `companion/web/index.html`。 找到下面这段原文，把它完整替换成新内容。上下文行也包含在替换范围内，不要重复留下。

<details><summary>定位：本步骤要替换的原文</summary>

```html
      <label><input id="strict" type="checkbox" />只看核对范围（下一章接入过滤）</label>
```

</details>

**先理解：**标签确定页面结构，id 让后面的 JavaScript 找到同一个控件。label 关联输入框；hidden 只是隐藏显示，不负责服务端权限。

```html
      <label><input id="strict" type="checkbox" />只看已核对范围的片段</label>
```

**写完后应当怎样：**选中后只展示受限证据。

## 运行并观察

```bash
# 保存本单元代码并停止上一服务，再用同一命令重启；预期页面出现进度和受限阅读选项。
python -m uvicorn companion.app:app --host 127.0.0.1 --port 8000
```

先在普通模式问一个涉及后文的问题，然后把进度设为 1 并开启受限阅读。保存范围时旧 history 清空，页面旧结果消失。再次问后文，应该只看到允许片段或不足提示，而不是重复上一轮答案。

## 做四个边界检查

- 进度 0：没有任何已核对且 range_end≤0 的片段时，返回不足。
- 进度 1：只出现你确实标为允许的片段。
- 未标注来源：即使拿到 ID，也不能通过来源 API 读取。
- 退回较早进度：旧历史和旧展示不继续带入；以后缓存也必须考虑范围。

检查 `mode=reviewed-excerpts` 与 `usage=null`，确认本次没有调用生成。不是把“模型答得保守”误认为过滤已生效。

## 产品取舍写清楚

受限模式暂时牺牲自然对话能力，换来更容易核验的行为。后续若恢复生成，需要独立的剧情标注、泄露题集和人工审核；本课程不把一句 Prompt 当成可靠保证。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. 为什么限制证据仍可能被模型剧透？
2. 本课怎样降低这项风险？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**为什么限制证据仍可能被模型剧透？**

模型可能从预训练知识补出后文，不完全依赖检索片段。

**本课怎样降低这项风险？**

受限模式只展示人工审核过且范围允许的原片段，不走自由生成；未知范围被排除，范围变化清空旧上下文。

**通过证据：**四项边界结果与本次无生成调用的记录，明确人工标注仍是风险来源。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter9)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。

## 用小检查核对自己的实现

下面的 Python 在当前项目中检查已经写过的行为。终端中的 `python -` 从随后的文本读取临时检查代码，结束标记 `PY` 要单独顶格写。它不会替你创建项目。涉及资料输出或虚构会话的检查只在本课程练习库执行。

```bash
# 验证本单元已经实现的行为；assert 不成立会报错，不把检查通过当成真实模型质量评分。
python - <<'PY'
from companion.corpus import visible
from companion.rag import answer
base={"id":"x","tenant":"demo","book":"狂人日记","text":"已核对的一小段","range_reviewed":True}
assert visible([{**base,"range_end":True}],"demo","狂人日记",1)==[]
hits=visible([{**base,"range_end":1}],"demo","狂人日记",1)
assert answer("继续",hits,strict=True)["mode"]=="reviewed-excerpts"
print("范围类型与受限展示通过，没有生成调用")
PY
```

**预期：**true 不作为1，合法范围片段可展示。


遇到问题时，可以带着本单元名称、写到的文件、预期和实际结果继续问我。不要附密钥；也不用为了继续往后走而跳过失败。
