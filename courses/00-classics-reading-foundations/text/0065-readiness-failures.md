# 活着不等于已经能接待读者

本单元预计 **35—50 分钟**。本章总用时见课程地图；首次安装、模型下载和等待他人审核另计。

## 两个检查回答不同问题

`/healthz` 只表示进程能响应；`/readyz` 检查资料、状态库、所选向量索引与模型列表。模型断了时，进程仍可能活着，因此不能只凭健康状态放行流量。某些供应商不支持 models.list，需要按真实接口调整 readiness，并补最小生成检查，不能伪造模型已就绪。

```bash
# 检查进程存活；预期返回 alive。
curl --fail http://127.0.0.1:8000/healthz
# 检查依赖就绪；缺资料、索引或模型时应非成功状态。
curl --fail http://127.0.0.1:8000/readyz
# 查看有限的服务日志定位启动问题；不要把含凭据的配置完整贴给他人。
docker compose -f deploy/compose.yaml logs --tail 40 app
```

关闭模型服务，重复两个检查，再从页面提问；预期是 alive 仍可能成功、ready 失败、用户得到可理解错误。恢复模型后再验证可用。使用 hybrid 时，也试一次停止 Qdrant 后的行为。

## 真正对外访问前补哪条连接

公司受控访问通常由 HTTPS 反向代理接到本机 8000。`deploy/Caddyfile.example` 展示这层关系，实际域名、DNS、证书、访问范围和运维账号由部署负责人配置；`.env` 的 ALLOWED_HOSTS 加入真实域名。仅准备配置文件不算完成 HTTPS 验证。

先在受保护测试域名验证登录、来源、反馈与错误，再允许试用。应用端口、数据库端口、模型端口不直接暴露公网。本课单 worker 配置与进程内限流一致，多副本扩容前需要共享状态、限流和取消机制。

## 本单元完成条件

先遮住答案，回答下面的问题，再核对自己的运行记录。

1. healthz 成功、readyz 失败合理吗？
2. 有 Caddyfile 就算 HTTPS 上线了吗？

<details class="answer-key"><summary>查看参考答案与通过标准</summary>

**healthz 成功、readyz 失败合理吗？**

合理。进程活着但依赖未就绪，应停止接纳需要这些依赖的业务流量。

**有 Caddyfile 就算 HTTPS 上线了吗？**

没有。必须完成实际域名、证书、网络与访问验证，并按公司要求审核。

**通过证据：**模型故障前后的双检查与用户界面记录；对外访问项注明实际完成或待办。

</details>

## 下次开始前

隔一天，先不看命令，解释本单元解决了什么问题，以及哪种情况仍会失败。再用你自己的一个阅读问题重跑关键步骤。若卡住，带上单元名称、预期结果和去掉凭据的错误信息继续讨论。

## 资料依据与选读

主线概念依据 [awesome-agentic-ai-zh 对应章节](https://github.com/WenyuChiou/awesome-agentic-ai-zh/blob/main/stages/07-multi-agent-production.zh-Hans.md) 和 [Hello-Agents 对应章节](https://github.com/datawhalechina/hello-agents/tree/main/docs/chapter13)。名著例子、练习顺序和本页程序是本课程的场景化编排，不是上游仓库的逐字转载。下方拓展可随时跳过。
