# 使用 cimg/python:3.8 作为基础镜像
FROM cimg/python:3.8

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码到镜像
COPY . .

# 暴露 FastAPI 的默认端口
EXPOSE 8000

# 启动应用程序
CMD ["uvicorn", "main:app_api", "--host", "0.0.0.0", "--port", "8000"]
