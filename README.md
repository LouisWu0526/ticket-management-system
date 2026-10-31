# 工单报修管理系统

一个简洁的工单/报修管理系统：用户提交问题 → 管理员处理 → 完结。前后端分离，支持 JWT 认证与基于角色的权限控制。

## 功能

- **用户注册 / 登录**：JWT 无状态认证，bcrypt 加密存储密码
- **提交工单**：标题、描述、图片上传（类型白名单 + 5MB 大小限制）
- **工单列表**：分页、按状态筛选、按标题搜索
- **工单处理**：管理员修改状态、回复沟通，详情页以时间线展示
- **权限区分**：普通用户仅能查看和处理自己的工单，管理员可查看全部工单
- **状态流转**：待处理 → 处理中 → 已完成，服务端强校验非法流转
- **操作日志**：创建、状态变更、回复全程留痕

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端 | FastAPI、SQLAlchemy 2.0、Pydantic、PyJWT、bcrypt |
| 前端 | Vue 3、Vite、Element Plus、Pinia、Vue Router、Axios |
| 数据库 | SQLite（开发）/ MySQL 8（部署） |
| 部署 | Docker Compose、Nginx |

## 项目结构

```
management_system/
├── backend/
│   ├── app/
│   │   ├── routers/        # 认证、工单、上传接口
│   │   ├── config.py       # 配置（支持环境变量覆盖）
│   │   ├── database.py     # 数据库连接
│   │   ├── deps.py         # 依赖注入与权限校验
│   │   ├── models.py       # ORM 模型
│   │   ├── schemas.py      # 请求/响应模型
│   │   ├── security.py     # JWT 与密码哈希
│   │   └── main.py         # 应用入口
│   ├── tests/test_api.py   # 端到端接口测试
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── views/          # 登录、注册、工单列表/详情/创建
│       ├── layout/         # 整体布局
│       ├── api/            # Axios 封装与接口
│       ├── router/         # 路由与登录守卫
│       └── stores/         # 用户状态
└── docker-compose.yml
```

## 快速开始

### 本地开发

**后端**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

首次启动会自动建表并初始化管理员账号。

**前端**

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 。

- 接口文档（Swagger）：http://localhost:8000/docs
- 默认管理员：`admin / admin123`
- 普通用户请通过注册页面创建

### Docker Compose 部署

```bash
docker compose up -d --build
```

编排包含三个容器：MySQL 8（带健康检查）+ FastAPI 后端 + Nginx 前端。访问 http://localhost:8080 。

## 数据库切换

默认使用 SQLite，无需任何配置。切换 MySQL 只需在 `backend/.env` 中设置连接串：

```ini
DATABASE_URL=mysql+pymysql://ticket:ticket123456@localhost:3306/ticket_system?charset=utf8mb4
```

首次启动会自动建表并初始化管理员，无需手动执行 SQL。

## 测试

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/test_api.py -v
```

覆盖注册登录、鉴权、越权访问、状态机流转、分页筛选、图片上传等场景。

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 登录获取 Token |
| GET | `/api/auth/me` | 当前用户信息 |
| POST | `/api/tickets` | 提交工单 |
| GET | `/api/tickets` | 工单列表（分页、状态筛选） |
| GET | `/api/tickets/{id}` | 工单详情 |
| PATCH | `/api/tickets/{id}/status` | 修改状态（管理员） |
| POST | `/api/tickets/{id}/replies` | 回复工单 |
| GET | `/api/tickets/{id}/logs` | 操作日志 |
| POST | `/api/uploads` | 上传图片 |
| GET | `/api/health` | 健康检查 |
