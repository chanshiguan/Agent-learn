# 与前三章相同，先固定解释器系列；发布时还需记录实际镜像摘要。
FROM python:3.12-slim
WORKDIR /app
COPY requirements*.txt ./
# 本课程在容器内用 CPU 编码，先装 CPU 版，避免 Linux 自动下载不使用的 CUDA 运行库。
RUN python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-model.txt -r requirements-web.txt -r requirements-rag.txt -r requirements-graph.txt
COPY companion ./companion
COPY eval ./eval
RUN useradd --uid 1000 --create-home reader && mkdir -p data && chown reader:reader data
USER reader
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
# 单 worker 与本课程进程内请求额度一致；扩副本前必须改成共享限流与会话存储。
CMD ["python", "-m", "uvicorn", "companion.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "16", "--no-access-log"]
