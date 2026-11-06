# 领域文档

工程技能在探索代码库时，应按以下规则使用本仓库的领域文档。

## 探索前读取

- 读取仓库根目录的 **`CONTEXT.md`**；或者
- 如果根目录存在 **`CONTEXT-MAP.md`**，按其指引读取与当前主题相关的各个上下文 `CONTEXT.md`
- 读取 **`docs/adr/`** 中与即将处理区域有关的 ADR；在多上下文仓库中，还应检查 `src/<context>/docs/adr/` 中限定于该上下文的决策

如果这些文件不存在，**静默继续**，不要提示缺失，也不要主动建议创建。`/domain-modeling` 技能（可由 `/grill-with-docs` 和 `/improve-codebase-architecture` 调用）会在术语或决策真正明确后按需创建这些文件。

## 文件结构

单上下文仓库（大多数仓库）：

```text
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md`）：

```text
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 上下文专属决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表中的词汇

当输出中出现领域概念名称时，例如工单标题、重构建议、假设或测试名称，应使用 `CONTEXT.md` 定义的术语，不要改用术语表明确避免的同义词。

如果术语表中没有所需概念，应将其视为一个信号：要么正在创造项目并未使用的语言，需要重新考虑；要么确实存在领域文档缺口，应将其记录下来，交由 `/domain-modeling` 处理。

## 标明与 ADR 的冲突

如果输出与现有 ADR 冲突，应明确指出，而不是静默覆盖：

> _与 ADR-0007（事件溯源订单）冲突——但值得重新讨论，因为……_
