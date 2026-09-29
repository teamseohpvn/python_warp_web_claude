import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, Query, HTTPException, Request, Response, Depends, status
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import (
    BASE_DIR, PRESET_PROJECTS, PRESETS, LOG_DIR,
    TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR,
    AUTH_ENABLED, AUTH_PASSWORD, AUTH_COOKIE_NAME
)
from app.auth import (
    rate_limiter, get_client_ip, create_session,
    delete_session, verify_token, require_auth,
    SESSION_DURATION_SECONDS
)
from app.task_runner import task_runner
from app.pty_manager import handle_pty_websocket
from app.log_manager import LogManager
from app.reports_manager import ReportsManager

app = FastAPI(title="Claude SEO & Blog Web Console", version="1.0.0")

# Mount static files
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class LoginRequest(BaseModel):
    password: str

class RunTaskRequest(BaseModel):
    cmd: str
    cwd: str = "/root"

# --- Authentication Endpoints ---

@app.post("/api/auth/login")
async def login(req: LoginRequest, request: Request, response: Response):
    if not AUTH_ENABLED:
        return {"success": True, "token": "auth_disabled"}

    ip = get_client_ip(request)
    is_allowed, val = rate_limiter.check_limit(ip)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Đã vượt quá 10 lần nhập sai trong 1 phút! Vui lòng chờ {val} giây trước khi thử lại."
        )

    if req.password == AUTH_PASSWORD:
        rate_limiter.reset(ip)
        token = create_session()
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            httponly=True,
            max_age=SESSION_DURATION_SECONDS,
            samesite="lax",
            path="/"
        )
        return {"success": True, "token": token}
    else:
        rate_limiter.record_failure(ip)
        is_still_allowed, val = rate_limiter.check_limit(ip)
        if not is_still_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Đã vượt quá 10 lần nhập sai trong 1 phút! Vui lòng chờ {val} giây trước khi thử lại."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Mật khẩu không chính xác! Bạn còn {val} lần thử trong 1 phút này."
        )

@app.get("/api/auth/status")
async def auth_status(request: Request):
    if not AUTH_ENABLED:
        return {"authenticated": True, "auth_required": False}

    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
    if not token:
        token = request.query_params.get("token")

    return {
        "authenticated": verify_token(token),
        "auth_required": True
    }

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(AUTH_COOKIE_NAME)
    delete_session(token)
    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    return {"success": True}

# --- Web UI ---

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = BASE_DIR / "templates" / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index template not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# --- Protected API Endpoints ---

@app.get("/api/config", dependencies=[Depends(require_auth)])
async def get_config():
    projects = []
    for proj in PRESET_PROJECTS:
        p_path = Path(proj["path"])
        projects.append({
            "name": proj["name"],
            "path": proj["path"],
            "badge": proj["badge"],
            "exists": p_path.exists()
        })
    return {
        "projects": projects,
        "presets": PRESETS
    }

@app.post("/api/tasks/run", dependencies=[Depends(require_auth)])
async def run_task(req: RunTaskRequest):
    if not req.cmd.strip():
        raise HTTPException(status_code=400, detail="Lệnh không được để trống")
    
    cwd_path = Path(req.cwd)
    if not cwd_path.exists():
        req.cwd = "/root"

    task = await task_runner.run_task(req.cmd.strip(), req.cwd)
    return {"success": True, "task": task.to_dict()}

@app.get("/api/tasks/{task_id}/stream", dependencies=[Depends(require_auth)])
async def stream_task(task_id: str):
    return StreamingResponse(
        task_runner.stream_task_output(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/tasks/{task_id}/cancel", dependencies=[Depends(require_auth)])
async def cancel_task(task_id: str):
    success = task_runner.cancel_task(task_id)
    return {"success": success}

@app.get("/api/tasks", dependencies=[Depends(require_auth)])
async def list_tasks():
    return {"tasks": task_runner.get_all_tasks()}

@app.websocket("/ws/terminal")
async def terminal_endpoint(websocket: WebSocket, cwd: str = Query("/root"), token: str = Query(None)):
    # Verify authentication for WebSocket
    cookie_token = websocket.cookies.get(AUTH_COOKIE_NAME)
    auth_token = token or cookie_token
    if AUTH_ENABLED and not verify_token(auth_token):
        await websocket.close(code=4001, reason="Unauthorized")
        return
    await handle_pty_websocket(websocket, cwd)

@app.get("/api/logs", dependencies=[Depends(require_auth)])
async def list_logs():
    return {"logs": LogManager.get_logs()}

@app.get("/api/logs/{filename}", dependencies=[Depends(require_auth)])
async def view_log(filename: str):
    data = LogManager.get_log_content(filename)
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy file log")
    return data

@app.get("/api/logs/{filename}/download", dependencies=[Depends(require_auth)])
async def download_log(filename: str):
    for dir_path in [TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR]:
        candidate = dir_path / filename
        if candidate.exists() and candidate.is_file():
            return FileResponse(
                path=str(candidate),
                filename=filename,
                media_type="text/plain"
            )
    raise HTTPException(status_code=404, detail="File không tồn tại")

@app.delete("/api/logs/{filename}", dependencies=[Depends(require_auth)])
async def delete_log(filename: str):
    success = LogManager.delete_log(filename)
    return {"success": success}

@app.get("/api/reports", dependencies=[Depends(require_auth)])
async def list_reports():
    return {"reports": ReportsManager.list_reports()}

@app.get("/api/reports/content", dependencies=[Depends(require_auth)])
async def get_report_content(path: str = Query(...)):
    res = ReportsManager.get_report_content(path)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res
