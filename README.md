# 植保精灵 PGuard

## 开发人员

2250753 宋宇然；2251875 陈晓坤；2251948 许经宝

**联系方式：**

电话：+86 13614356534

邮箱：3759790650@qq.com

**项目贡献：**

宋宇然：后端 33.33%

陈晓坤：前端 33.33%

许经宝：模型 33.33%

## 项目简介

本项目旨在通过基于图像识别的病害检测功能，帮助用户管理种植地块并提供植物保护建议。用户可以上传植物图片，系统将自动识别病害并提供相应的建议，并会统计用户地块信息，给出来年种植建议。

## 功能特性

- **用户管理**：用户注册、登录及权限验证。
- **地块管理**：用户可以添加、删除和查看自己的种植地块。
- **病害检测**：基于YOLOv8模型的图像识别，检测上传图片中的植物病害。
- **日志记录**：记录每次检测的结果和建议，供用户查看历史记录。

## 目录结构

- `backend/`：后端服务代码
  - `service/`：业务逻辑实现
  - `controller/`：API路由
  - `models/` 
    * `model.py`：数据库模型定义
  - `core/`：核心依赖配置
  - `database/`：数据库配置
    * `settings.py`：PostgreSQL
    * `redis_config.py`：Redis
- `yolov8/`：YOLOv8模型相关文件
  * `ultralytics-main` 
    * `Grape_defect.py`：葡萄病害检测脚本
    * `Potato_defect.py`：马铃薯病害检测脚本

## 后端部署

1. 请确保你的环境已安装以下依赖：

- Python 3.8，其他依赖请参考`backend\requirements.txt`。
- yolov8 模型与后端是运行于不同的环境中的微服务，依赖请参考 `yolov8\说明文档.md`。
- 数据存储(本项目部署在WindowsServer2019上，Linux服务器选择匹配的版本即可)：
  * PostgreSQL-16.6-1-windows-x64
  * Redis-x64-3.0.504

2. 开启PostgreSQL服务、Redis服务

3. 在`backend`目录创建`.env`文件

   ```.env
   DB_HOST=
   DB_PWD=
   SECRET_KEY= # 随机生成一个长度为 32 的随机字符串
   ALGORITHM = "HS256"
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ```

4. 运行后端项目：在命令行中，切换到`main.py`所在的目录，然后运行`uvicorn main:app --reload`。

