# Local Agent Platform

一个本地优先的 Agent 执行平台原型，基于 LangGraph、LangChain、FastAPI、MCP 和 SQLite 设计。当前阶段已完成端到端 MVP：任务提交、Agent 编排、工具调用、高风险审批、恢复执行、任务存储、执行日志查询和前端工作台。

## 项目定位

这个项目的目标是构建一个可本地部署的个人 Agent 工作台。用户提交自然语言任务后，系统通过 LangGraph 编排执行流程，由大模型完成计划生成和工具选择，再通过统一工具层调用本地工具或未来的 MCP 工具。

长期目标包括：

- 本地任务执行与文件操作
- 高风险操作审批
- 执行过程日志和回放
- 多模型适配
- MCP 工具扩展
- FastAPI 接口和前端工作台

## 当前能力

当前已经完成的 Agent MVP 流程：

```text
用户任务
  -> plan_task 生成短计划
  -> select_tool 选择工具和参数
  -> check_approval 判断是否需要审批
  -> execute_tool 执行工具
  -> finalize_task 生成最终回复
```

已支持：

- LangGraph 线性流程和条件路由
- Kimi / DeepSeek 风格的 OpenAI 兼容模型配置
- 工具注册表和工具元信息
- 本地工具：`mock_tool`、`list_files`、`read_file`、`write_file`
- 高风险工具审批中断
- LangGraph 原生 `interrupt` / `Command(resume=...)` 恢复执行
- `step_logs` 执行日志累积
- SQLAlchemy + SQLite 任务和日志存储层
- FastAPI 任务提交、查询、日志、审批接口
- CORS 配置，方便后续前端联调
- 基础错误保护：模型调用失败、工具 JSON 解析失败、未知工具调用
- React 前端工作台：任务输入、任务列表、任务详情、审批操作和日志翻页

## 技术栈

- LangGraph：Agent 状态流转和节点编排
- LangChain：模型调用抽象
- FastAPI：API 服务层
- MCP：后续标准化工具扩展
- SQLite：本地任务和日志存储
- SQLAlchemy：ORM 数据访问层
- React + Vite：本地前端工作台

## 目录结构

```text
app/
  main.py            # FastAPI 应用入口
  api/
    routes.py        # 任务接口
  schemas/
    tasks.py         # 请求和响应模型
  agent/
    state.py          # AgentState 定义
    node.py           # LangGraph 节点和路由函数
    graph.py          # 图结构组装
    test_graph.py     # 本地测试入口
  tools/
    builtin.py        # 本地工具实现
    registry.py       # 工具注册表和工具元信息
  storage/
    database.py       # SQLAlchemy ORM 模型和数据库初始化
    task_repository.py # 任务和日志存储函数
  services/
    agent_service.py  # 串联 graph 和 storage
scripts/
  test_agent_service.py # service 层测试脚本
frontend/
  src/
    App.tsx       # 前端主界面
    api.ts        # 后端 API 调用
    types.ts      # 前端类型定义
    styles.css    # macOS 风格界面样式
data/
  agent.db            # 本地 SQLite 数据库，默认不提交
```

## 快速开始

创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境变量模板：

```bash
cp .env.example .env
```

填写 `.env` 中的大模型 API Key：

```env
LLM_PROVIDER=kimi
KIMI_API_KEY=your_kimi_api_key_here
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=kimi-k2.5
```

初始化数据库：

```bash
python -c "from app.storage.database import init_db; init_db()"
```

运行本地 Agent 测试：

```bash
python -m app.agent.test_graph
```

运行 service 层测试：

```bash
python -m scripts.test_agent_service
```

启动 FastAPI 后端：

```bash
uvicorn app.main:app --reload
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

启动前端工作台：

```bash
cd frontend
npm install
npm run dev
```

打开前端页面：

```text
http://127.0.0.1:5173/
```

如果 `5173` 被占用，Vite 会自动切换到下一个端口，例如 `5174`。

前端构建检查：

```bash
cd frontend
npm run build
```

## API Endpoints

```text
POST /tasks
提交任务，返回 task_id、thread_id 和执行结果。如果触发高风险操作，会返回 pending_approval。

GET /tasks
查询最近任务列表。

GET /tasks/{task_id}
查询单个任务详情。

GET /tasks/{task_id}/logs
查询任务执行日志，用于执行回放。

POST /tasks/{task_id}/approve
审批高风险任务，使用 LangGraph Command(resume=...) 恢复执行。
```

示例请求：

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"task": "读取 requirements.txt"}'
```

高风险任务审批示例：

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"task": "帮我写入 api_demo.txt，内容是 hello"}'
```

如果返回 `status=pending_approval`，再调用：

```bash
curl -X POST http://127.0.0.1:8000/tasks/{task_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```

## 当前测试场景

`app/agent/test_graph.py` 和 `scripts/test_agent_service.py` 当前包含两个场景：

- 低风险任务：读取 `requirements.txt`
- 高风险任务：写入 `demo.txt`，触发审批中断后通过 `Command(resume={"approved": True})` 恢复执行

## 前端演示流程

1. 启动 FastAPI 后端：`uvicorn app.main:app --reload`
2. 启动前端：`cd frontend && npm run dev`
3. 在前端输入：`读取 requirements.txt`
4. 查看任务详情、最终回复和执行日志
5. 再输入：`帮我写入 demo.txt，内容是 hello`
6. 任务进入 `pending_approval`
7. 点击批准，Agent 从中断点恢复并完成写入

## 后续计划

近期计划：

- 增加更实用的本地工具，例如 `run_shell` 和 `http_request`
- 增强工具权限控制和安全策略
- 优化前端任务详情、日志回放和错误提示体验

中期计划：

- 接入 MCP Client
- 支持 MCP 工具发现和调用
- 增加工具权限和风险等级配置
- 增加执行回放接口

长期计划：

- 构建本地 Web UI
- 支持模型配置管理
- 支持桌面 App 打包
- 支持 PostgreSQL 扩展

## 简历描述参考

基于 LangGraph、LangChain、FastAPI、React 和 MCP 设计本地 Agent 执行平台，支持任务规划、工具调用、高风险操作审批中断、恢复执行、执行日志记录和前端回放展示。通过 SQLAlchemy 抽象本地 SQLite 存储层，预留 PostgreSQL 和 MCP 工具生态扩展能力。
