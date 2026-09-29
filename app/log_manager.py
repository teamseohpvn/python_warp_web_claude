import os
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from app.config import TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR

class LogManager:
    @staticmethod
    def get_logs() -> List[Dict]:
        logs = []
        
        # Collect task logs
        for path in sorted(TASK_LOG_DIR.glob("*.log"), key=os.path.getmtime, reverse=True):
            stat = path.stat()
            logs.append({
                "id": path.stem,
                "filename": path.name,
                "type": "task",
                "path": str(path),
                "size_bytes": stat.st_size,
                "size_formatted": LogManager._format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": stat.st_mtime
            })
            
        # Collect session logs (PTY)
        for path in sorted(SESSION_LOG_DIR.glob("*.log"), key=os.path.getmtime, reverse=True):
            stat = path.stat()
            logs.append({
                "id": path.stem,
                "filename": path.name,
                "type": "terminal_session",
                "path": str(path),
                "size_bytes": stat.st_size,
                "size_formatted": LogManager._format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": stat.st_mtime
            })
            
        # Sort combined logs by modified timestamp descending
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs

    @staticmethod
    def get_log_content(filename: str, max_lines: int = 2000) -> Optional[Dict]:
        # Search in task, session, and audit directories
        target_path = None
        for dir_path in [TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR]:
            candidate = dir_path / filename
            if candidate.exists() and candidate.is_file():
                target_path = candidate
                break
                
        if not target_path:
            return None
            
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                total_lines = len(lines)
                if total_lines > max_lines:
                    content = "".join(lines[-max_lines:])
                    truncated = True
                else:
                    content = "".join(lines)
                    truncated = False
                    
            stat = target_path.stat()
            return {
                "filename": filename,
                "path": str(target_path),
                "total_lines": total_lines,
                "truncated": truncated,
                "size": LogManager._format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "content": content
            }
        except Exception as e:
            return {"error": str(e), "filename": filename, "content": f"Lỗi đọc file log: {str(e)}"}

    @staticmethod
    def delete_log(filename: str) -> bool:
        for dir_path in [TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR]:
            candidate = dir_path / filename
            if candidate.exists() and candidate.is_file():
                candidate.unlink()
                return True
        return False

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
