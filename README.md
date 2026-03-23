# Mini-OpenClaw - 方便了解OpenClaw的底层运行原理

一个基于 LangChain 和 Flask 的智能 AI 代理系统，支持动态技能加载、多轮对话、命令执行和 Web UI 交互。

## 🌟 主要功能

### 核心功能
- **多轮对话交互** - 保持上下文的连续对话
- **智能命令执行** - AI 自动识别并执行系统命令
- **动态技能加载** - 自动发现并加载 `skills/` 目录下的所有技能
- **Web UI 界面** - 一个简单的web客户端页面
- **会话管理** - 为每个用户维护独立的对话会话
- **角色定义** - 通过 SYSTEM.md、User.md 等文件定义系统和用户角色

### 智能特性
- **YAML Frontmatter 支持** - 标准化的技能元数据提取
- **自适应降级处理** - 多层级的元数据提取策略
- **环境配置管理** - 安全的 .env 配置文件支持
- **实时技能发现** - 启动时自动扫描并加载所有可用技能

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                   Web 前端 (index.html)                   │
│              美观的对话UI + 实时消息展示                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            Flask Web 服务器 (main.py)                     │
│  - 路由处理: /chat, /reset, /clear-session               │
│  - 会话管理: 用户ID + Agent 实例存储                      │
│  - 环境配置: 从 .env 加载配置                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Agent 核心 (agent.py)                            │
│  - 初始化 LangChain ChatOpenAI 客户端                     │
│  - 构建动态系统提示词（SYSTEM + User + Skills）          │
│  - 维护消息历史                                          │
│  - 执行多轮对话循环                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│        动态提示词构建 (load_prompt.py)                     │
│  - 加载 SYSTEM.md (系统角色)                             │
│  - 加载 User.md (用户信息)                               │
│  - 扫描 skills/ 目录                                     │
│  - 提取 YAML frontmatter 元数据                          │
│  - 生成完整系统提示词                                    │
└──────────────────────┬──────────────────────────────────
```

### 文件结构

```
src/
├── main.py                 # Flask Web 服务器
├── agent.py               # AI 代理核心逻辑
├── load_prompt.py         # 动态提示词加载和构建
├── index.html             # Web UI 前端
├── .env                   # 环境配置（API_KEY、MODEL_NAME 等）
│
├── SYSTEM.md              # 系统角色定义
├── User.md                # 用户角色信息
├── Agent.md               # Agent 系统提示
├── SKILL.md               # 技能定义模板
│
├── skills/                # 技能库目录
│   └── weather/
│       ├── SKILL.md       # 天气技能定义
│       └── ...
│
├── requirements.txt       # 项目依赖
└── README.md             # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆或进入项目目录**
   ```bash
   cd /src
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置 .env 文件**
   ```bash
   cat .env
   ```
   
   确保以下配置已设置：
   ```
   API_KEY=your_api_key
   MODEL_NAME=your_model_name
   BASE_URL=your_model_base_url
   SECRET_KEY=your_secret_key
   ```

4. **启动应用**
   ```bash
   python main.py
   ```

5. **访问 Web 界面**
   - 打开浏览器访问: `http://localhost:5001`
   - 即可使用对话界面与 AI 交互

## 💬 使用指南

### 基本使用

1. **发送消息**
   - 在输入框输入你的问题或命令
   - 按 Enter 或点击"发送"按钮

2. **AI 执行流程**
   - AI 理解你的请求
   - 选择合适的技能
   - 执行相应的命令或操作
   - 返回执行结果

3. **会话管理**
   - **新建对话** - 清空当前对话历史
   - **清除历史** - 清除所有会话数据
   - 每个用户拥有独立的会话

### 技能系统

#### 查看可用技能
系统启动时自动加载 `skills/` 目录下所有技能：

```
<available_skills>
<skill>
  <name>weather</name>
  <description>Get current weather and forecasts...</description>
  <location>skills/weather/SKILL.md</location>
</skill>
</available_skills>
```

#### 添加新技能

1. **创建技能目录**
   ```bash
   mkdir skills/my_skill
   ```

2. **编写 SKILL.md**
   ```yaml
   ---
   name: my_skill
   description: "My custom skill description"
   path: skills/my_skill
   ---
   
   # My Skill
   
   Skill content and instructions...
   ```

3. **重启应用**
   - 系统将自动发现并加载新技能


## 🎯 技术栈

- **后端**: Flask
- **AI 框架**: LangChain
- **大模型**: LLM (OpenAI API 兼容)
- **前端**: HTML + CSS + JavaScript (ES6+)
- **配置**: YAML + dotenv


### 常见问题

1. **导入错误: 无法找到 langchain**
   ```bash
   pip install -r requirements.txt
   ```

2. **.env 配置未生效**
   - 确认 .env 在项目根目录
   - 重启应用
   - 检查 API_KEY 是否正确

3. **技能未加载**
   - 检查 skills/ 目录是否存在
   - 验证 SKILL.md 文件格式
   - 查看启动日志中的加载信息

4. **Web UI 不显示**
   - 验证 index.html 在根目录
   - 检查浏览器控制台是否有错误
   - 尝试清除浏览器缓存


## 📄 许可证

项目文档（本 README 和相关配置文件）使用 MIT 许可证。
