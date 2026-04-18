# KKRPA - 自动化流程图形化编程平台

<p align="center">
  <strong>支持内嵌 Python 的 RPA 可视化工作流桌面应用</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Electron-33-blue?logo=electron" alt="Electron" />
  <img src="https://img.shields.io/badge/React%20Flow-12-blue" alt="React Flow" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

---

## ✨ 特性

| 特性 | 社区版 | 企业版 |
|------|:------:|:------:|
| 🎨 可视化工作流编辑器 (拖拽式) | ✅ | ✅ |
| 🐍 内嵌 Python 代码节点 (Monaco Editor) | ✅ | ✅ |
| 🌐 HTTP 请求节点 | ✅ | ✅ |
| 🔀 条件分支 / 🔄 循环 / ⏰ 延时 | ✅ | ✅ |
| ▶️ 手动触发执行 | ✅ | ✅ |
| 📊 执行日志查看 | ✅ | ✅ |
| 📋 最多 5 个工作流 | ✅ | ❌ 无限制 |
| ⏱️ Cron 定时任务调度 | ❌ | ✅ |
| ⚡ 并行执行 | ❌ | ✅ |
| 🔒 高级沙盒隔离 | ❌ | ✅ |

## 🏗️ 架构

```
KKRPA.exe (Electron)
├── Electron 主进程 (窗口管理 + 子进程管理)
├── React 前端 (静态文件, React Flow 编辑器)
├── Python 后端 (FastAPI, PyInstaller 打包)
│   ├── SQLite 数据库 (零配置)
│   ├── APScheduler (内置定时调度)
│   └── 工作流执行引擎 (线程池)
└── License 激活系统 (本地验证)
```

**零外部依赖** — 无需安装 PostgreSQL、Redis 等服务，双击即用。

## 🛠️ 技术栈

- **桌面框架**: Electron + electron-builder
- **前端**: Next.js 15 (静态导出) + React Flow + Monaco Editor + TailwindCSS
- **后端**: FastAPI + SQLAlchemy (SQLite) + APScheduler
- **沙盒**: RestrictedPython
- **打包**: PyInstaller (Python) + electron-builder (.exe)

## 🚀 快速开始

### 用户使用

1. 下载 `KKRPA-Setup.exe`
2. 安装并运行
3. 输入激活码（企业版）或跳过（免费社区版）
4. 开始创建工作流！

### 构建 .exe (Windows)

**前置条件：**
- [Node.js 20+](https://nodejs.org/) (LTS)
- [Python 3.11+](https://www.python.org/) (勾选 "Add to PATH")
- Git (用于克隆代码)

```powershell
# 1. 克隆项目到本地
git clone <your-repo-url> KKRPA
cd KKRPA

# 2. 双击运行，或在 CMD 中执行：
build.bat
```

构建完成后会自动打开 `dist/` 目录，其中包含 `KKRPA Setup x.x.x.exe` 安装包。

> **提示：** 构建过程约需 5-10 分钟，首次运行会自动安装所有依赖。

### 开发者本地运行

#### 后端
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 18090
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

#### Electron (开发模式)
```bash
cd electron
npm install
npm start
```
输出：`dist/KKRPA Setup *.exe`

## 📁 项目结构

```
KKRPA/
├── build.sh                    # 一键构建脚本
├── .env.example                # 环境变量模板
├── electron/                   # Electron 桌面外壳
│   ├── main.js                 # 主进程 (启动后端+窗口管理)
│   ├── preload.js              # IPC 安全桥接
│   ├── activation.html         # 激活/License 验证页面
│   └── package.json            # electron-builder 配置
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置 (SQLite 模式)
│   │   ├── database.py         # 数据库连接
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # API 校验
│   │   ├── api/                # API 路由
│   │   │   ├── license.py      # 激活码验证 API
│   │   │   └── ...
│   │   ├── core/               # 认证/权限/版本/激活码
│   │   │   ├── license.py      # License 生成与验证
│   │   │   └── ...
│   │   ├── engine/             # 工作流执行引擎
│   │   │   ├── executor.py     # DAG 执行器
│   │   │   └── nodes/          # 节点实现
│   │   └── workers/            # 任务执行
│   │       ├── workflow_tasks.py  # 线程池执行器
│   │       └── scheduler.py      # APScheduler 定时
│   └── requirements.txt
└── frontend/                   # Next.js 前端
    ├── next.config.ts          # 静态导出配置
    └── src/
        ├── app/                # 页面路由
        ├── components/workflow/ # 编辑器组件
        ├── lib/                # API Client & Store
        └── types/              # TypeScript 类型
```

## 🔑 激活码说明

| 类型 | 格式 | 功能 |
|------|------|------|
| 社区版 | `KKRPA-CE-XXXXXXXX-XXXXXXXX` | 基础功能，5 个工作流限制 |
| 企业版 | `KKRPA-EE-XXXXXXXX-XXXXXXXX` | 全部功能，无限制 |

开发测试时，可通过 API 生成测试激活码：
```bash
curl -X POST http://{ServiceIP}:18090/api/license/generate \
  -H "Content-Type: application/json" \
  -d '{"edition": "enterprise"}'
```

## 📜 License

MIT
