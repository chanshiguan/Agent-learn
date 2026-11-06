# 工单系统：本地 Markdown

本仓库的工单和规格文档（也称 PRD）存放在 `.scratch/` 目录中。

## 约定

- 每项功能使用一个目录：`.scratch/<feature-slug>/`
- 规格文档为 `.scratch/<feature-slug>/spec.md`
- 每个实施工单单独保存为 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 开始编号；不得合并为单个工单文件
- Triage 状态记录在每个工单文件顶部附近的 `Status:` 行中，角色字符串参见 `triage-labels.md`
- 评论和对话历史追加在文件底部的 `## Comments` 标题下

## 当技能要求“发布到工单系统”时

在 `.scratch/<feature-slug>/` 下创建新文件；目录不存在时一并创建。

## 当技能要求“获取相关工单”时

读取引用路径对应的文件。用户通常会直接提供文件路径或工单编号。

## Wayfinding 操作

供 `/wayfinder` 使用。**地图**文件对应多个**子工单**文件，每个工单一个文件。

- **地图**：`.scratch/<effort>/map.md`，包含 Notes、Decisions-so-far 和 Fog 正文
- **子工单**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号，正文记录待解决的问题；`Type:` 行记录工单类型（`research`、`prototype`、`grilling` 或 `task`），`Status:` 行记录 `claimed` 或 `resolved`
- **阻塞关系**：在文件顶部附近使用 `Blocked by: NN, NN`；列出的所有工单均为 `resolved` 后，该工单才解除阻塞
- **前沿工单**：扫描 `.scratch/<effort>/issues/`，寻找状态为开放、未阻塞且未认领的文件；编号最小者优先
- **认领**：开始工作前，将 `Status:` 设置为 `claimed` 并保存
- **解决**：在 `## Answer` 标题下追加答案，将 `Status:` 设置为 `resolved`，然后在 `map.md` 的 Decisions-so-far 中追加上下文指针（摘要和链接）
