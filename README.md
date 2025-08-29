# 📁 Web 文件管理系统

一个基于 Flask 的专业文件上传、管理和下载系统，支持多种文件类型，提供友好的 Web 界面。

## ✨ 功能特性

### 核心功能
- 🎯 **多文件类型支持**：音视频、文档、图片、其他文件等
- 📤 **多种上传方式**：拖拽上传、文件选择、多文件批量上传
- 📋 **文件管理**：文件列表、分页浏览、搜索过滤
- 👁️ **实时预览**：支持图片、视频、音频的在线预览
- 📊 **统计信息**：总文件数、今日上传、存储大小统计
- 🗑️ **文件操作**：下载、删除、URL复制

### 技术特性
- 🔒 **安全文件名**：自动生成安全的唯一文件名
- 📱 **响应式设计**：移动端和桌面端友好
- ⚡ **实时进度**：文件上传进度实时显示
- 🎨 **现代UI**：渐变色彩、卡片布局、流畅动画
- 🐳 **Docker支持**：容器化部署

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

1. **构建镜像**：
```bash
docker build -t web-files-server:latest .
```

2. **运行容器**：
```bash
docker run -d --name web-files-server -p 8080:8080 -v ./Web_Server:/app web-files-server:latest
```

3. **访问系统**：
打开浏览器访问 `http://localhost:8080`

### 方式二：本地部署

1. **安装依赖**：
```bash
pip install flask requests werkzeug
```

2. **运行服务**：
```bash
cd Web_Server
python video_server.py
```

3. **访问系统**：
打开浏览器访问 `http://localhost:8080`

## 📚 API 接口

### 文件上传
- **POST** `/upload`
  - 上传文件，支持单个或多个文件
  - 最大文件大小：500MB
  - 返回文件信息和下载链接

### 文件管理
- **GET** `/api/files` - 获取文件列表
- **GET** `/api/stats` - 获取统计信息
- **DELETE** `/api/files/<filename>` - 删除指定文件

### 文件下载
- **GET** `/files/<filename>` - 下载文件
- **GET** `/videos/<filename>` - 兼容接口（重定向到文件下载）
- **GET** `/videos` - 获取文件列表（兼容接口）

## 📁 支持的文件类型

### 🎬 音视频文件
**扩展名**：mp4, avi, mov, mkv, flv, wmv, m4v, 3gp, webm, mp3, wav, flac, aac, ogg, m4a, wma

### 📄 文档文件  
**扩展名**：pdf, doc, docx, txt, rtf, odt, pages, xls, xlsx, csv, ods, ppt, pptx, odp, key

### 🖼️ 图片文件
**扩展名**：jpg, jpeg, png, gif, bmp, tiff, svg, webp

### 📦 其他文件
**扩展名**：zip, rar, 7z, tar, gz, bz2, js, py, html, css, json, xml, java, cpp, c

## 🛠️ 项目结构

```
web_files_download_server/
├── Dockerfile              # Docker 配置文件
├── README.txt              # 简单部署说明
├── README.md               # 详细项目文档（本文件）
└── Web_Server/
    ├── video_server.py     # 主程序文件
    └── files/              # 文件存储目录
        ├── *.mp4           # 示例视频文件
        └── ...             # 其他上传的文件
```

## ⚙️ 配置说明

### 主要配置项（在 video_server.py 中）

```python
# 文件存储目录
VIDEO_DIR = r'./files'

# 最大文件大小（500MB）
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# 服务端口
app.run(host='0.0.0.0', port=8080)

# 分页设置
filesPerPage = 10  # 每页显示文件数
```

### Docker 配置
- **基础镜像**：python:3.12-slim
- **工作目录**：/app
- **暴露端口**：8080
- **数据卷**：建议挂载 `/app/files` 目录

## 🎨 界面预览

### 主界面功能
1. **文件类型选择区域**：可选择特定文件类型进行过滤
2. **拖拽上传区域**：支持文件拖拽和点击选择
3. **实时统计卡片**：显示文件总数、今日上传、总大小
4. **文件列表表格**：分页显示所有文件，支持预览、下载、删除操作

### 响应式设计
- **桌面端**：多列布局，完整功能
- **移动端**：单列布局，卡片式文件信息展示

## 🔧 开发者信息

### 技术栈
- **后端**：Python 3.12 + Flask
- **前端**：原生 HTML/CSS/JavaScript
- **容器化**：Docker
- **文件处理**：Werkzeug

### 文件命名规则
上传的文件会自动重命名为：
```
YYYYMMDD_HHMMSS_UUID前8位_原文件名
```
例：`20250828_192159_ab03bcb0_video.mp4`

## 🚨 注意事项

1. **安全性**：
   - 自动生成安全文件名，防止路径遍历攻击
   - 文件类型验证，仅允许预定义的文件扩展名
   - 文件大小限制，防止恶意上传

2. **存储空间**：
   - 默认文件存储在 `./files` 目录
   - 建议定期清理不需要的文件
   - Docker 部署时建议挂载外部存储

3. **性能优化**：
   - 大文件上传时建议增加服务器超时时间
   - 大量文件时可能需要优化分页查询
   - 可考虑添加文件缓存机制

## 📝 更新日志

- **v1.0.0**：初始版本，基础文件上传下载功能
- **v2.0.0**：新增 Web 界面、多文件类型支持、预览功能
- **v2.1.0**：添加统计信息、分页浏览、响应式设计
- **v2.2.0**：完善 Docker 支持、API 接口优化

## 📞 技术支持

如有问题或建议，请检查：
1. 文件权限是否正确
2. 端口是否被占用
3. 存储空间是否充足
4. Docker 容器日志信息

---

*该文件管理系统适合个人、团队或小型组织使用，提供简单易用的文件管理解决方案。*