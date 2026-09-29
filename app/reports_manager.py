import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from app.config import WORKSPACE_ROOT, PRESET_PROJECTS

class ReportsManager:
    @staticmethod
    def list_reports() -> List[Dict]:
        results = []
        scanned_dirs = [Path(p["path"]) for p in PRESET_PROJECTS if Path(p["path"]).exists()]
        
        # Also ensure /root is covered
        if WORKSPACE_ROOT not in scanned_dirs:
            scanned_dirs.append(WORKSPACE_ROOT)

        seen_paths = set()

        for directory in scanned_dirs:
            # Look for markdown files, html files, and text reports in root of directory
            for ext in ["*.md", "*.html", "*.txt"]:
                for file_path in directory.glob(ext):
                    if file_path.is_file() and not file_path.name.startswith("."):
                        abs_str = str(file_path.resolve())
                        if abs_str in seen_paths:
                            continue
                        seen_paths.add(abs_str)

                        # Filter out vendor or internal READMEs if they are in repo root and not custom reports
                        stat = file_path.stat()
                        results.append({
                            "name": file_path.name,
                            "path": abs_str,
                            "directory": str(file_path.parent),
                            "extension": file_path.suffix.lower(),
                            "size_bytes": stat.st_size,
                            "size_formatted": ReportsManager._format_size(stat.st_size),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "timestamp": stat.st_mtime
                        })

        # Sort newest modified first
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    @staticmethod
    def get_report_content(file_path_str: str) -> Optional[Dict]:
        try:
            target_path = Path(file_path_str).resolve()
            # Ensure path is within /root for security
            if not str(target_path).startswith("/root"):
                return {"error": "Truy cập ngoài thư mục /root bị từ chối"}

            if not target_path.exists() or not target_path.is_file():
                return {"error": "File không tồn tại"}

            stat = target_path.stat()
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            return {
                "name": target_path.name,
                "path": str(target_path),
                "extension": target_path.suffix.lower(),
                "size_formatted": ReportsManager._format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "content": content
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
