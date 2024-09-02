# 使用官方 Python 3.9 运行时作为父镜像
FROM python:3.9-slim

# 更新包列表并安装系统依赖
RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc git zip unzip wget curl htop libgl1 libglib2.0-0 libpython3-dev \
    gnupg g++ libusb-1.0-0 libsm6 \
    && rm -rf /var/lib/apt/lists/*



# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY requirements.txt /app/

# 安装项目的依赖（不使用缓存）
RUN pip install --no-cache-dir -r requirements.txt

# 复制其他项目文件
COPY main.py /app/
COPY best.pt /app/

# 公开容器的5000端口
EXPOSE 5000

# 运行 Flask 应用
CMD ["python", "main.py"]
