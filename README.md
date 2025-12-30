# 企业知识助手

这是一个基于 RAG（Retrieval-Augmented Generation）的企业知识助手，支持 React 前端界面和 Flask API 后端。

## ✨ 功能特点

- 📄 文档分块与向量化存储
- 🔍 基于相似度的文档检索
- 🤖 使用 Ollama 生成智能回答
- ⚛️ 现代化的 React 前端界面
- 📱 响应式设计，支持移动端
- 🎨 美观的 UI 设计和加载动画
- 📊 显示检索结果和相似度评分

## 🚀 快速开始

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 确保 Ollama 运行

确保 Ollama 服务正在运行，并且已下载 `qwen2:0.5b` 模型：

```bash
ollama serve
ollama pull qwen2:0.5b
```

### 4. 启动服务

**终端 1：启动 Flask API 后端**
```bash
python app.py
```

**终端 2：启动 React 前端**
```bash
cd frontend
npm start
```

### 5. 访问应用

打开浏览器访问：http://localhost:3000/

## 📁 项目结构

```
knowledge_table/
├── app.py                 # Flask API 后端服务
├── rag_demo.py           # 原始 RAG 演示脚本
├── company_handbook.txt  # 公司手册文档
├── requirements.txt      # Python 依赖
├── chroma_rag_db/        # ChromaDB 向量数据库
└── frontend/             # React 前端应用
    ├── src/
    │   ├── App.tsx       # 主应用组件
    │   ├── App.css       # 样式文件
    │   └── index.tsx     # 应用入口
    ├── public/
    └── package.json
```

## 🛠️ 技术栈

- **后端**: Flask, Python, ChromaDB, Ollama
- **前端**: React, TypeScript, CSS3
- **AI**: Ollama (qwen2:0.5b)
- **向量数据库**: ChromaDB

## 📝 API 接口

### POST /query
查询知识库并获取回答

**请求体**:
```json
{
  "query": "您的问题"
}
```

**响应**:
```json
{
  "answer": "AI 生成的回答",
  "retrieved_docs": [
    {
      "content": "参考文档内容",
      "similarity": 0.85,
      "distance": 0.15
    }
  ]
}
```

## ⚠️ 注意事项

- 首次运行时会自动创建向量库，可能需要一些时间
- 确保 Ollama 服务正在运行
- 文档分块大小和重叠可以根据需要调整
- **如果遇到数据库错误**：删除 `chroma_rag_db/` 目录后重新运行应用
- React 开发服务器运行在 http://localhost:3000
- Flask API 服务器运行在 http://localhost:5000

## 🔧 开发模式

- 前端热重载：修改 `frontend/src/` 中的文件会自动刷新
- 后端调试模式：Flask 以调试模式运行，支持热重载
- CORS 已配置：前端可以安全地调用后端 API

## 📦 生产部署

1. 构建 React 生产版本：
```bash
cd frontend
npm run build
```

2. 使用生产 WSGI 服务器运行 Flask：
```bash
pip install gunicorn
gunicorn -w 4 app:app
```

3. 配置反向代理（如 Nginx）来服务静态文件和 API
