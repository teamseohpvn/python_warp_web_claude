import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional, AsyncGenerator
from app.config import TASK_LOG_DIR

class Task:
    def __init__(self, task_id: str, cmd: str, cwd: str):
        self.task_id = task_id
        self.cmd = cmd
        self.cwd = cwd
        self.status = "pending"  # pending, running, completed, failed, cancelled
        self.exit_code: Optional[int] = None
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.log_file = TASK_LOG_DIR / f"task_{self.started_at.strftime('%Y%m%d_%H%M%S')}_{task_id[:8]}.log"
        self.process: Optional[asyncio.subprocess.Process] = None
        self.subscribers = []
        self.output_buffer = []

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "cmd": self.cmd,
            "cwd": self.cwd,
            "status": self.status,
            "exit_code": self.exit_code,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
            "duration_seconds": round((self.completed_at - self.started_at).total_seconds(), 1) if self.completed_at else round((datetime.now() - self.started_at).total_seconds(), 1),
            "log_filename": self.log_file.name
        }

class TaskRunner:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    async def run_task(self, cmd: str, cwd: str = "/root") -> Task:
        task_id = str(uuid.uuid4())
        task = Task(task_id, cmd, cwd)
        self.tasks[task_id] = task

        # Start execution in background asyncio task
        asyncio.create_task(self._execute(task))
        return task

    async def _execute(self, task: Task):
        task.status = "running"
        with open(task.log_file, "w", encoding="utf-8", errors="replace") as f_log:
            header = (
                f"==========================================================\n"
                f"TASK ID     : {task.task_id}\n"
                f"COMMAND     : {task.cmd}\n"
                f"DIRECTORY   : {task.cwd}\n"
                f"STARTED AT  : {task.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"==========================================================\n\n"
            )
            f_log.write(header)
            f_log.flush()

            try:
                # Spawn subprocess with merged stdout and stderr
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["TERM"] = "xterm-256color"
                env["COLORTERM"] = "truecolor"

                task.process = await asyncio.create_subprocess_shell(
                    task.cmd,
                    cwd=task.cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    env=env
                )

                while True:
                    line = await task.process.stdout.readline()
                    if not line:
                        break
                    text = line.decode("utf-8", errors="replace")
                    
                    # Record in log
                    f_log.write(text)
                    f_log.flush()
                    
                    # Store in memory buffer (capped at 1000 lines)
                    if len(task.output_buffer) > 1000:
                        task.output_buffer.pop(0)
                    task.output_buffer.append(text)

                    # Notify subscribers
                    for queue in list(task.subscribers):
                        try:
                            await queue.put(text)
                        except Exception:
                            pass

                await task.process.wait()
                task.exit_code = task.process.returncode
                task.status = "completed" if task.exit_code == 0 else "failed"

            except asyncio.CancelledError:
                task.status = "cancelled"
                f_log.write("\n[TASK CANCELLED BY USER]\n")
                if task.process and task.process.returncode is None:
                    try:
                        task.process.terminate()
                    except Exception:
                        pass
            except Exception as e:
                task.status = "failed"
                err_msg = f"\n[ERROR EXECUTING COMMAND]: {str(e)}\n"
                f_log.write(err_msg)
                task.output_buffer.append(err_msg)
            finally:
                task.completed_at = datetime.now()
                footer = (
                    f"\n\n==========================================================\n"
                    f"FINISHED AT : {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"EXIT CODE   : {task.exit_code}\n"
                    f"STATUS      : {task.status.upper()}\n"
                    f"==========================================================\n"
                )
                f_log.write(footer)
                f_log.flush()

                # Notify finish to subscribers
                for queue in list(task.subscribers):
                    try:
                        await queue.put(None)  # None indicates EOF
                    except Exception:
                        pass

    async def stream_task_output(self, task_id: str) -> AsyncGenerator[str, None]:
        task = self.tasks.get(task_id)
        if not task:
            yield f"data: [Error: Task {task_id} not found]\n\n"
            return

        # First yield past buffered output
        for text in task.output_buffer:
            yield f"data: {text.rstrip()}\n\n"

        if task.status in ["completed", "failed", "cancelled"]:
            yield f"data: [Task already finished: {task.status}]\n\n"
            return

        # Subscribe to live queue
        queue = asyncio.Queue()
        task.subscribers.append(queue)

        try:
            while True:
                line = await queue.get()
                if line is None:
                    break
                yield f"data: {line.rstrip()}\n\n"
        finally:
            if queue in task.subscribers:
                task.subscribers.remove(queue)

    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == "running" and task.process:
            try:
                task.process.terminate()
                task.status = "cancelled"
                return True
            except Exception:
                return False
        return False

    def get_task(self, task_id: str) -> Optional[Dict]:
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_all_tasks(self):
        return [t.to_dict() for t in sorted(self.tasks.values(), key=lambda x: x.started_at, reverse=True)]

task_runner = TaskRunner()
