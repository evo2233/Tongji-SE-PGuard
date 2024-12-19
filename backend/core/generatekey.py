import secrets
SECRET_KEY = secrets.token_urlsafe(32)  # 生成一个长度为 32 的随机字符串
print(SECRET_KEY)

# 仅用于生成 SECRET_KEY 开发环境中写进.env里，生产环境中要写进服务器环境变量
