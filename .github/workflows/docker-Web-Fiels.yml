# 基础镜像，选择带 Python 的官方镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制代码到容器
COPY ./Web_Server /app

# 安装依赖（可以是 requirements.txt，也可以直接列）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask requests werkzeug

# 暴露端口（假设你的服务监听 7178）
EXPOSE 7187

# 设置容器启动命令
CMD ["python", "video_server.py"]
