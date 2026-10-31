"""端到端接口冒烟测试：覆盖注册登录(JWT)、RBAC、工单流转、回复、日志、图片上传。

运行：cd backend && pytest -v
"""
import io
import os

# 在导入应用前指定独立的测试数据库
TEST_DB = os.path.join(os.path.dirname(__file__), "test_ticket.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    from app.database import engine

    with TestClient(app) as c:
        yield c
    # 测试结束释放连接并清理临时数据库（Windows 需先 dispose）
    engine.dispose()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(client, username, password):
    resp = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# 1x1 像素 PNG
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae"
    "426082"
)


def test_01_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_02_register_and_duplicate(client):
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "123456"})
    assert resp.status_code == 201, resp.text
    assert resp.json()["user"]["role"] == "user"
    assert resp.json()["access_token"]

    # 重复用户名
    resp = client.post("/api/auth/register", json={"username": "alice", "password": "123456"})
    assert resp.status_code == 400


def test_03_login_invalid(client):
    resp = client.post("/api/auth/login", data={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_04_create_ticket(client):
    token = login(client, "alice", "123456")
    resp = client.post(
        "/api/tickets",
        json={"title": "空调不制冷", "description": "3楼会议室空调故障", "image_url": None},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "pending"
    assert resp.json()["author_name"] == "alice"


def test_05_list_permission_isolation(client):
    # 第二个用户 bob，看不到 alice 的工单
    client.post("/api/auth/register", json={"username": "bob", "password": "123456"})
    bob = login(client, "bob", "123456")
    resp = client.get("/api/tickets", headers=auth_headers(bob))
    assert resp.status_code == 200
    assert resp.json()["total"] == 0

    # 管理员能看到全部
    admin = login(client, "admin", "admin123")
    resp = client.get("/api/tickets", headers=auth_headers(admin))
    assert resp.json()["total"] == 1

    # bob 越权访问 alice 的工单 → 403
    resp = client.get("/api/tickets/1", headers=auth_headers(bob))
    assert resp.status_code == 403

    # 未登录 → 401
    assert client.get("/api/tickets").status_code == 401


def test_06_status_filter_and_pagination(client):
    alice = login(client, "alice", "123456")
    resp = client.get("/api/tickets?status=pending&page=1&page_size=10", headers=auth_headers(alice))
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["title"] == "空调不制冷"


def test_07_user_cannot_change_status(client):
    alice = login(client, "alice", "123456")
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "completed"}, headers=auth_headers(alice)
    )
    assert resp.status_code == 403


def test_08_status_flow_and_reply(client):
    admin = login(client, "admin", "admin123")

    # pending → processing
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "processing"}, headers=auth_headers(admin)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "processing"

    # 重复设置同一状态 → 400
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "processing"}, headers=auth_headers(admin)
    )
    assert resp.status_code == 400

    # 非法状态 → 400
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "pending"}, headers=auth_headers(admin)
    )
    assert resp.status_code == 400

    # 管理员回复
    resp = client.post(
        "/api/tickets/1/replies",
        json={"content": "已安排维修师傅，预计今天下午上门"},
        headers=auth_headers(admin),
    )
    assert resp.status_code == 201
    assert resp.json()["author_role"] == "admin"

    # processing → completed
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "completed"}, headers=auth_headers(admin)
    )
    assert resp.status_code == 200

    # 已完成不可再变更
    resp = client.patch(
        "/api/tickets/1/status", json={"status": "processing"}, headers=auth_headers(admin)
    )
    assert resp.status_code == 400


def test_09_detail_replies_and_logs(client):
    alice = login(client, "alice", "123456")
    resp = client.get("/api/tickets/1", headers=auth_headers(alice))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert len(data["replies"]) == 1
    # create / status_change x2 / reply 共 4 条日志
    actions = [log["action"] for log in data["logs"]]
    assert actions == ["create", "status_change", "reply", "status_change"]


def test_10_image_upload(client):
    alice = login(client, "alice", "123456")
    resp = client.post(
        "/api/uploads",
        files={"file": ("fault.png", io.BytesIO(PNG_BYTES), "image/png")},
        headers=auth_headers(alice),
    )
    assert resp.status_code == 200, resp.text
    url = resp.json()["url"]
    assert url.startswith("/uploads/")

    # 文件可访问
    assert client.get(url).status_code == 200

    # 非图片类型拒绝
    resp = client.post(
        "/api/uploads",
        files={"file": ("virus.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
        headers=auth_headers(alice),
    )
    assert resp.status_code == 400
