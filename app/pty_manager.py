import os
import pty
import fcntl
import termios
import struct
import asyncio
import uuid
from datetime import datetime
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.config import SESSION_LOG_DIR, AUDIT_LOG_DIR

class PtySession:
    def __init__(self, session_id: str, cwd: str = "/root"):
        self.session_id = session_id
        self.cwd = cwd
        self.started_at = datetime.now()
        timestamp_str = self.started_at.strftime("%Y%m%d_%H%M%S")
        self.log_file_path = SESSION_LOG_DIR / f"session_{timestamp_str}_{session_id[:8]}.log"
        self.audit_log_path = AUDIT_LOG_DIR / f"audit_{timestamp_str}_{session_id[:8]}.log"
        self.master_fd: Optional[int] = None
        self.pid: Optional[int] = None
        self.log_file = None
        self.audit_file = None

    def start(self, rows: int = 24, cols: int = 80):
        self.master_fd, slave_fd = pty.openpty()
        self.resize(rows, cols)

        self.log_file = open(self.log_file_path, "ab")
        self.audit_file = open(self.audit_log_path, "a", encoding="utf-8", errors="replace")
        
        self.audit_file.write(
            f"=== SESSION {self.session_id} STARTED AT {self.started_at.strftime('%Y-%m-%d %H:%M:%S')} CWD: {self.cwd} ===\n"
        )
        self.audit_file.flush()

        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["COLORTERM"] = "truecolor"
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"
        env["HOME"] = "/root"
        env["PWD"] = self.cwd

        # Fork process
        self.pid = os.fork()
        if self.pid == 0:
            # Child process
            os.close(self.master_fd)
            os.setsid()
            fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            if slave_fd > 2:
                os.close(slave_fd)

            try:
                os.chdir(self.cwd)
            except Exception:
                os.chdir("/root")

            # Execute bash login shell
            os.execvpe("/bin/bash", ["/bin/bash", "--login"], env)
        else:
            # Parent process
            os.close(slave_fd)

    def resize(self, rows: int, cols: int):
        if self.master_fd:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            except Exception:
                pass

    def write_input(self, data: bytes):
        if self.master_fd:
            try:
                os.write(self.master_fd, data)
                # Record printable input into audit log
                if self.audit_file:
                    try:
                        decoded = data.decode("utf-8", errors="ignore")
                        if decoded in ["\r", "\n"]:
                            self.audit_file.write("\n")
                        elif len(decoded) > 0 and ord(decoded[0]) >= 32:
                            self.audit_file.write(decoded)
                        self.audit_file.flush()
                    except Exception:
                        pass
            except Exception:
                pass

    def read_output(self, size: int = 4096) -> Optional[bytes]:
        if self.master_fd:
            try:
                data = os.read(self.master_fd, size)
                if data and self.log_file:
                    self.log_file.write(data)
                    self.log_file.flush()
                return data
            except Exception:
                return None
        return None

    def close(self):
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except Exception:
                pass
            self.master_fd = None

        if self.pid:
            try:
                os.kill(self.pid, 9)
                os.waitpid(self.pid, 0)
            except Exception:
                pass
            self.pid = None

        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None

        if self.audit_file:
            try:
                self.audit_file.write(
                    f"\n=== SESSION CLOSED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
                )
                self.audit_file.close()
            except Exception:
                pass
            self.audit_file = None


async def handle_pty_websocket(websocket: WebSocket, cwd: str = "/root"):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session = PtySession(session_id, cwd)
    session.start()

    loop = asyncio.get_event_loop()

    # Async reader task
    async def read_from_pty():
        while True:
            await asyncio.sleep(0.01)
            data = await loop.run_in_executor(None, session.read_output)
            if not data:
                break
            try:
                await websocket.send_bytes(data)
            except Exception:
                break

    read_task = asyncio.create_task(read_from_pty())

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                session.write_input(message["bytes"])
            elif "text" in message:
                text = message["text"]
                # Handle control commands like JSON resize
                if text.startswith('{"type":"resize"'):
                    import json
                    try:
                        data = json.loads(text)
                        session.resize(data.get("rows", 24), data.get("cols", 80))
                    except Exception:
                        pass
                else:
                    session.write_input(text.encode("utf-8"))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        read_task.cancel()
        session.close()
