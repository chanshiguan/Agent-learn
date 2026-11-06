---
name: meeting-actions
description: 从编号的会议资料生成可核对行动表草稿，缺失责任人或日期时标待确认。
disable-model-invocation: true
---

只读取用户指定的会议资料，不读取其他文件或访问外部服务。
输出 JSON 对象，字段为 actions 数组和 needs_confirmation 字符串数组。
actions 每项包含 task、owner、due、source 四个字符串字段。
保留条件与否定；缺失信息用“待确认”，不猜具体日期。
source 使用原句编号。不发送消息，不创建实际日程，不发布。
没有资料时停止并列出缺失输入。
