# 同一 Python 大版本便于比较主机和容器；标签仍会更新，生产锁定留到发布阶段。
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 先复制依赖清单，使只修改业务代码时可以复用之前的安装结果。
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# 明确复制程序，不把讲稿、虚拟环境和个人配置带进镜像。
COPY read_docx.py ./
# 容器从命令行接收资料路径，下一次可以处理另一份讲稿而不重建镜像。
ENTRYPOINT ["python", "read_docx.py"]
