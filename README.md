# 电力设备智能运维分析与决策支持系统

基于「感-知-决」三层架构的电力设备智能运维系统，融合大语言模型、知识图谱与多 Agent 协作技术，实现设备状态感知、故障智能诊断与检修决策辅助。

## 技术栈

**后端**：Python 3.10+ / FastAPI / Pydantic v2 / WebSocket / Uvicorn

**前端**：Vue 3 / TypeScript / Vite / Pinia / Element Plus / ECharts / Axios

## 项目结构

```
power-equipment-intelligent-om/
├── backend/                          # Python FastAPI 后端
│   ├── run.py                        # 启动脚本
│   ├── requirements.txt              # Python 依赖
│   └── app/
│       ├── main.py                   # FastAPI 应用、中间件、路由注册
│       ├── config.py                 # 配置管理（Pydantic Settings）
│       ├── models/                   # Pydantic 数据模型（7 个模块）
│       ├── routers/                  # API 路由层（6 个模块）
│       ├── services/                 # 业务逻辑层（6 个模块）
│       └── mock_data/                # Mock 数据层（12 台设备、6 个故障案例、13 份知识文档）
├── frontend/                         # Vue 3 + TypeScript 前端
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── views/                    # 4 个业务页面
│       │   ├── dashboard/            #   可视化大屏
│       │   ├── chat/                 #   智能问答
│       │   ├── diagnosis/            #   故障诊断
│       │   └── maintenance/          #   检修决策
│       ├── components/               # 5 个通用/布局组件
│       ├── stores/                   # 4 个 Pinia Store
│       ├── services/api.ts           # Axios API 客户端
│       ├── types/index.ts            # TypeScript 类型定义（23 个接口）
│       └── assets/styles/            # 清华紫 SCSS 主题
└── 前后端代码技术设计文档.md            # 详细技术设计文档
```

## 功能模块

| 模块 | 说明 |
|---|---|
| **可视化大屏** | 设备统计、健康度分布、告警趋势、知识检索 |
| **智能问答** | ChatGPT 风格对话、RAG 知识检索、置信度评分、知识引用 |
| **故障诊断** | 传感器数据展示、5 Agent 流水线可视化、根因分析、FMEA 评估 |
| **检修决策** | 健康度仪表盘、设备列表、工单管理、维护计划生成 |

## 快速开始

### 环境要求

- Python >= 3.10
- Node.js >= 18

### 启动后端

```bash
cd backend
pip3 install -r requirements.txt
python3 run.py
```

后端服务启动在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务启动在 `http://localhost:5173`，已配置 `/api` 请求代理到后端。

### 构建生产版本

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/` 目录。

## API 概览

共 14 个端点（13 HTTP + 1 WebSocket），统一返回 `ApiResponse` 格式：

```json
{ "code": 0, "message": "success", "data": { ... } }
```

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/chat` | 智能问答 |
| POST | `/api/v1/diagnosis/trigger` | 触发故障诊断 |
| GET | `/api/v1/diagnosis/{id}` | 获取诊断报告 |
| WS | `/ws/diagnosis/{id}` | 诊断进度实时推送 |
| POST | `/api/v1/batch/assess` | 批次风险评估 |
| POST | `/api/v1/maintenance/plan` | 生成检修计划 |
| POST | `/api/v1/knowledge/upload` | 上传知识文档 |
| GET | `/api/v1/knowledge/search` | 知识语义检索 |
| GET | `/api/v1/equipment` | 设备列表（分页、筛选） |
| GET | `/api/v1/equipment/stats` | 设备统计概览 |
| GET | `/api/v1/equipment/{id}/health` | 设备健康度评分 |
| GET | `/api/v1/equipment/{id}` | 设备详情 |

完整 API 文档：[前后端代码技术设计文档](./前后端代码技术设计文档.md)

## 架构设计

```
┌─────────────────────────────────────────────────────┐
│                  浏览器 (Vue SPA)                     │
│     Vue 3 + TypeScript + Element Plus + ECharts      │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP / WebSocket
                        ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI (Python 后端)                    │
│           Router → Service → Mock Data               │
└─────────────────────────────────────────────────────┘
```

系统采用前后端分离架构。后端遵循 Router → Service → Mock Data 三层设计，前端通过 Pinia Store 管理状态，API 服务层已预置对接接口，待接入真实模型与数据库后可无缝切换。

## Mock 数据

当前版本为原型验证阶段，内置完整模拟数据：

- **12 台设备**：变压器 5 台、断路器 4 台、GIS 3 组，分布在 4 个变电站
- **6 个故障案例**：涵盖过热、气体泄漏、绝缘缺陷、机械故障等典型故障
- **13 份知识文档**：覆盖标准规程、诊断知识、维护策略、应急预案
- **传感器模拟器**：支持油温、DGA、局放等传感器数据的时序生成

## 许可证

MIT License
