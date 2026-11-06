# 固定 Python 运行环境；网络、输入输出挂载与资源限制由讲义中的 docker run 参数控制。
# 选择示例所用的基础 Python 镜像。
FROM python:3.11-slim
# 设置后续命令在容器内的工作目录。
WORKDIR /app
# 将明确列出的文件复制到容器指定位置。
COPY plot_csv.py /app/plot_csv.py
# 以非 root 用户执行；输出目录需对该 UID 可写，不能因此开放其他宿主目录。
# 后续以这个普通用户身份运行，避免默认使用 root。
USER 65534:65534
# 设置启动容器时的默认命令及参数。
CMD ["python", "/app/plot_csv.py"]
