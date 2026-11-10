"""仅在 CI 临时目录验证 Docker 与 Compose；模型接口为明确的协议夹具。"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import uuid

import httpx

if os.environ.get("CI") != "true":
    raise SystemExit("本脚本只用于隔离 CI；学员按章节操作自己的 Docker 服务。")
course = Path(__file__).resolve().parents[1]


class ModelFixture(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, value):
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.send({"object": "list", "data": [{"id": "protocol-fixture", "object": "model", "created": 0, "owned_by": "ci"}]})

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        evidence = json.loads(request["messages"][-1]["content"])["evidence"]
        content = json.dumps({"answer": "这是容器网络协议夹具，不是真实模型回答。",
                              "citations": [evidence[0]["id"]], "insufficient": False}, ensure_ascii=False)
        self.send({"id": "ci-fixture", "object": "chat.completion", "created": 0, "model": "protocol-fixture",
                   "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                   "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})


server = ThreadingHTTPServer(("0.0.0.0", 11434), ModelFixture)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory) / "examples"
        shutil.copytree(course / "examples", work, ignore=shutil.ignore_patterns("data", ".env*", ".venv*", "__pycache__"))
        shutil.copytree(course / "examples/data/input", work / "data/input")
        (work / "data/live").mkdir()
        (work / "data/output").mkdir()
        (work / ".env").write_text("\n".join(["LLM_MODE=local", "LLM_MODEL=protocol-fixture",
            "LLM_BASE_URL=http://host.docker.internal:11434/v1", "RETRIEVAL=keyword",
            f"APP_UID={os.getuid()}", f"APP_GID={os.getgid()}", "RELEASE_TAG=review-ci"]) + "\n")
        def run(command):
            return subprocess.run(command, cwd=work, check=True)
        project = "classics-ci-" + uuid.uuid4().hex[:8]
        compose = ["docker", "compose", "--env-file", ".env", "--project-name", project, "-f", "deploy/compose.yaml"]
        try:
            # env_file 给容器传值，--env-file 则参与 Compose 的 UID/镜像变量替换；两层都要核对。
            resolved = json.loads(subprocess.check_output(compose + ["config", "--format", "json"], cwd=work))
            assert resolved["services"]["app"]["user"] == f"{os.getuid()}:{os.getgid()}"
            # 前三章：真正构建读取镜像、挂载输入，检查容器写出的 JSON。
            run(["docker", "build", "-t", "classics-reader:review-ci", "."])
            first = sorted((work / "data/input").glob("06*.docx"))[0]
            run(["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
                 "-v", f"{work / 'data'}:/data", "classics-reader:review-ci",
                 f"/data/input/{first.name}", "/data/output/first.json"])
            result = json.loads((work / "data/output/first.json").read_text())
            assert result["paragraph_count"] == 1 and result["character_count"] == 1302
            run(compose + ["build"])
            run(compose + ["run", "--rm", "app", "python", "-m", "companion", "ingest"])
            run(compose + ["run", "--rm", "app", "python", "-c",
                 "from companion.state import initialize; from companion.auth import create_user; initialize(); create_user('demo','ci-reader','synthetic-ci-password')"])
            run(compose + ["up", "-d"])
            with httpx.Client(base_url="http://127.0.0.1:8000", trust_env=False, timeout=10) as api:
                ready = False
                for attempt in range(60):
                    try:
                        ready = api.get("/readyz").status_code == 200
                        if ready:
                            break
                    except httpx.TransportError:
                        pass
                    time.sleep(1)
                assert ready, "容器未通过就绪检查。"
                assert api.get("/api/sessions").status_code == 401
                response = api.post("/api/login", json={"tenant": "demo", "username": "ci-reader", "password": "synthetic-ci-password"})
                response.raise_for_status()
                api.headers["Authorization"] = "Bearer " + response.json()["access_token"]
                response = api.post("/api/sessions", json={"book": "狂人日记"})
                response.raise_for_status()
                identity = response.json()["id"]
                response = api.post("/api/ask", json={"session_id": identity, "question": "文言文序言与白话日记有什么关系", "request_id": uuid.uuid4().hex})
                response.raise_for_status()
                assert response.json()["citations"]
            # 真正访问 Compose 内的 Qdrant 服务；固定向量只验证服务与 SDK 协议。
            run(compose + ["exec", "-T", "app", "python", "-c",
                "from qdrant_client import QdrantClient,models; c=QdrantClient(url='http://qdrant:6333'); c.create_collection('ci_protocol',vectors_config=models.VectorParams(size=2,distance=models.Distance.COSINE)); c.upsert('ci_protocol',points=[models.PointStruct(id=1,vector=[1.0,0.0],payload={'tenant':'demo'})],wait=True); assert c.query_points('ci_protocol',query=[1.0,0.0]).points[0].id==1; c.close()"])
            print(json.dumps({"docx_container": "passed", "compose_authenticated_api": "passed", "qdrant_service": "passed",
                              "model": "protocol_fixture_only", "scope": "Docker 构建、挂载、身份和服务连通；不评价生成质量"}, ensure_ascii=False))
        finally:
            subprocess.run(compose + ["logs", "--tail", "30"], cwd=work)
            # 只清理本脚本随机命名的 CI 项目及其临时卷。
            subprocess.run(compose + ["down", "-v"], cwd=work)
finally:
    server.shutdown()
    server.server_close()
