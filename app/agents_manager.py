import os
import re
import json
import time
import shutil
import asyncio
import subprocess
import tempfile
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import BASE_DIR

CONFIG_FILE_PATH = BASE_DIR / "config" / "agents_config.json"

# Danh sách model được lấy trực tiếp từ API mỗi lần load app.
# Cache ngắn chỉ để tránh gọi trùng khi nhiều tab/endpoint load cùng lúc.
MODELS_CACHE_TTL = 60
MODELS_FETCH_TIMEOUT = 10

# Model không dùng được để chat/viết bài (embedding, ảnh, âm thanh...)
NON_CHAT_KEYWORDS = (
    "embedding", "tts", "whisper", "dall-e", "moderation", "davinci", "babbage",
    "audio", "realtime", "transcribe", "image", "imagen", "imagine", "search",
    "aqa", "sora", "computer-use", "veo", "instruct", "-live"
)

# Claude Code CLI đã đăng nhập sẵn (claude.ai) → agent Claude chạy qua `claude -p`, không cần API key.
# Alias luôn trỏ tới bản mới nhất của từng họ model (vd opus → claude-opus-5-5).
CLAUDE_CODE_MODELS = {
    "opus": "Opus – bản mới nhất (Claude Code)",
    "sonnet": "Sonnet – bản mới nhất (Claude Code)",
    "haiku": "Haiku – bản mới nhất (Claude Code)",
}
CLAUDE_CODE_STATUS_TTL = 300
CLAUDE_CODE_TIMEOUT = 900

# Antigravity CLI (`agy`) đã đăng nhập sẵn (tài khoản Google) → agent Gemini chạy qua `agy`, không cần API key.
# Chạy ở chế độ plan + sandbox trong thư mục tạm rỗng để agent không sửa được file nào của server.
ANTIGRAVITY_DEFAULT_MODEL = "gemini-4-argon-medium"
ANTIGRAVITY_TIMEOUT = 900

# Model đã bị nhà cung cấp ngừng hỗ trợ → loại khỏi config đã lưu
RETIRED_MODEL_PREFIXES = ("claude-3",)

# Họ model ưu tiên làm mặc định khi model mặc định cũ không còn trong danh sách
PREFERRED_DEFAULT_FAMILY = {
    "claude": "opus",
    "gemini": "pro",
    "gpt_code": "gpt-",
    "grok": "grok",
}

DEFAULT_AGENTS_CONFIG = {
    "active_agent": "claude",
    "agents": {
        "claude": {
            "id": "claude",
            "name": "Claude Agent",
            "provider": "anthropic",
            "badge": "Anthropic AI",
            "color": "#E06D53",
            "icon": "🟣",
            "description": "Chuyên gia phân tích sâu sắc, viết bài SEO E-E-A-T, audit cấu trúc và code phức tạp.",
            "cli_command": "claude",
            "api_key_env": "ANTHROPIC_API_KEY",
            "api_key": "",
            "base_url": "https://api.anthropic.com/v1",
            "default_model": "claude-opus-5-5",
            "models": [
                "claude-fable-5-1",
                "claude-opus-5-5",
                "claude-sonnet-5-5",
                "claude-haiku-5-5"
            ],
            "max_tokens": 8192,
            "temperature": 0.7,
            "system_prompt": "Bạn là chuyên gia SEO & Kỹ sư phần mềm cao cấp, chuyên sâu về E-E-A-T và tối ưu hóa nội dung B2B."
        },
        "gemini": {
            "id": "gemini",
            "name": "Gemini Agent",
            "provider": "google",
            "badge": "Google DeepMind",
            "color": "#3B82F6",
            "icon": "🔵",
            "description": "Tốc độ phản hồi cực nhanh, ngữ cảnh siêu lớn (1M+ tokens), tra cứu và tổng hợp thông tin sắc bén.",
            "cli_command": "gemini",
            "api_key_env": "GEMINI_API_KEY",
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "default_model": "gemini-3.8-flash",
            "models": [
                "gemini-3.8-flash",
                "gemini-3.5-flash",
                "gemini-3.1-pro-preview",
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-pro"
            ],
            "max_tokens": 8192,
            "temperature": 0.7,
            "system_prompt": "Bạn là chuyên gia phân tích chất lượng tìm kiếm Google, am hiểu thuật toán xếp hạng và quy chuẩn đánh giá E-E-A-T."
        },
        "gpt_code": {
            "id": "gpt_code",
            "name": "GPT Code Agent",
            "provider": "openai",
            "badge": "OpenAI",
            "color": "#10B981",
            "icon": "🟢",
            "description": "Suy luận logic, viết mã nguồn chuẩn xác, tối ưu hóa Technical SEO, regex và schema structured data.",
            "cli_command": "openai",
            "api_key_env": "OPENAI_API_KEY",
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "default_model": "gpt-4o",
            "models": [
                "o3",
                "o3-mini",
                "o1",
                "gpt-4.5-preview",
                "gpt-4o",
                "chatgpt-4o-latest",
                "gpt-4o-mini",
                "o1-mini"
            ],
            "max_tokens": 8192,
            "temperature": 0.7,
            "system_prompt": "Bạn là chuyên gia lập trình và Technical SEO, chuyên xử lý mã nguồn, cấu trúc dữ liệu schema và thuật toán tìm kiếm."
        },
        "grok": {
            "id": "grok",
            "name": "Grok Agent",
            "provider": "xai",
            "badge": "xAI Grok",
            "color": "#F3F4F6",
            "icon": "⚫",
            "description": "Suy luận sắc bén, nắm bắt dữ liệu thực tế và xu hướng mới nhất, tư duy phản biện thẳng thắn về chất lượng bài viết.",
            "cli_command": "grok",
            "api_key_env": "XAI_API_KEY",
            "api_key": "",
            "base_url": "https://api.x.ai/v1",
            "default_model": "grok-4",
            "models": [
                "grok-4",
                "grok-3",
                "grok-3-mini",
                "grok-2-latest",
                "grok-2-1212",
                "grok-beta"
            ],
            "max_tokens": 8192,
            "temperature": 0.7,
            "system_prompt": "Bạn là chuyên gia phân tích chất lượng nội dung và E-E-A-T theo tiêu chuẩn Google QRG, đánh giá sắc sảo và thẳng thắn về điểm yếu bài viết."
        }
    }
}


def _parse_created(value: Any) -> int:
    """Chuẩn hóa thời điểm phát hành model về epoch (giây)"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value:
        try:
            return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
        except ValueError:
            return 0
    return 0


def _version_key(model_id: str) -> tuple:
    """Tách số phiên bản từ tên model, bỏ hậu tố ngày (vd claude-3-7-sonnet-20250219 → (3, 7))"""
    stripped = re.sub(r"\d{4}-\d{2}-\d{2}|\d{8}", "", model_id)
    return tuple(float(n) for n in re.findall(r"\d+(?:\.\d+)?", stripped))


def _sort_models(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sắp xếp model mới nhất lên đầu: theo ngày phát hành, rồi theo số phiên bản"""
    return sorted(
        models,
        key=lambda m: (m.get("created", 0), _version_key(m["id"]), m["id"]),
        reverse=True
    )


def _is_chat_model(model_id: str) -> bool:
    lowered = model_id.lower()
    return not any(k in lowered for k in NON_CHAT_KEYWORDS)


def _http_get_json(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=MODELS_FETCH_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


class AgentsManager:
    def __init__(self):
        self.config_path = CONFIG_FILE_PATH
        self._models_status: Dict[str, Dict[str, Any]] = {}
        self._models_fetched_at: Dict[str, float] = {}
        self._models_lock = asyncio.Lock()
        self._claude_code_status: Dict[str, Any] = {"checked_at": 0, "logged_in": False, "auth_method": ""}
        self._antigravity_status: Dict[str, Any] = {"checked_at": 0, "logged_in": False, "quota": ""}
        self._ensure_config()

    def claude_code_logged_in(self) -> bool:
        """Kiểm tra Claude Code CLI có sẵn và đã đăng nhập (cache 5 phút)"""
        st = self._claude_code_status
        if time.time() - st["checked_at"] < CLAUDE_CODE_STATUS_TTL:
            return st["logged_in"]
        logged_in, auth_method = False, ""
        if shutil.which("claude"):
            try:
                out = subprocess.run(
                    ["claude", "auth", "status"], capture_output=True, text=True, timeout=20
                ).stdout
                data = json.loads(out)
                logged_in = bool(data.get("loggedIn"))
                auth_method = data.get("authMethod", "")
            except Exception as e:
                print(f"[AgentsManager] Không kiểm tra được Claude Code: {e}")
        self._claude_code_status = {"checked_at": time.time(), "logged_in": logged_in, "auth_method": auth_method}
        return logged_in

    def uses_claude_code(self, agent_id: str, agent_data: Dict[str, Any], custom_key: Optional[str] = None) -> bool:
        """Agent Claude ưu tiên Claude Code đã đăng nhập; chỉ dùng API key khi được truyền key riêng
        hoặc Claude Code chưa đăng nhập"""
        if agent_data.get("provider", agent_id) != "anthropic":
            return False
        if custom_key and custom_key.strip():
            return False
        return self.claude_code_logged_in()

    def antigravity_logged_in(self) -> bool:
        """Kiểm tra Antigravity CLI có sẵn và đã đăng nhập (cache 5 phút).
        `agy -p=/quota` không tốn hạn mức và không tạo hội thoại mới."""
        st = self._antigravity_status
        if time.time() - st["checked_at"] < CLAUDE_CODE_STATUS_TTL:
            return st["logged_in"]
        logged_in, quota = False, ""
        if shutil.which("agy"):
            try:
                proc = subprocess.run(
                    ["agy", "-p=/quota"], capture_output=True, text=True, timeout=30,
                    cwd=tempfile.gettempdir()
                )
                if proc.returncode == 0 and "Limit" in proc.stdout:
                    logged_in = True
                    for line in proc.stdout.splitlines():
                        cols = line.split("\t")
                        if len(cols) >= 3 and cols[0] == "Gemini Models" and "Five Hour" in cols[1]:
                            quota = f"còn {cols[2]} hạn mức Gemini 5 giờ"
            except Exception as e:
                print(f"[AgentsManager] Không kiểm tra được Antigravity CLI: {e}")
        self._antigravity_status = {"checked_at": time.time(), "logged_in": logged_in, "quota": quota}
        return logged_in

    def uses_antigravity(self, agent_id: str, agent_data: Dict[str, Any], custom_key: Optional[str] = None) -> bool:
        """Agent Gemini ưu tiên Antigravity CLI đã đăng nhập; chỉ dùng API key khi được truyền key riêng
        hoặc Antigravity chưa đăng nhập"""
        if agent_data.get("provider", agent_id) != "google":
            return False
        if custom_key and custom_key.strip():
            return False
        return self.antigravity_logged_in()

    def has_credentials(self, agent_id: str, agent_data: Dict[str, Any], custom_key: Optional[str] = None) -> bool:
        return (
            bool(self.get_effective_key(agent_data, custom_key))
            or self.uses_claude_code(agent_id, agent_data, custom_key)
            or self.uses_antigravity(agent_id, agent_data, custom_key)
        )

    def _ensure_config(self):
        """Đảm bảo file cấu hình tồn tại và đồng bộ các model mới nhất"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_AGENTS_CONFIG, f, indent=2, ensure_ascii=False)
        else:
            try:
                cfg = self.load_config()
                agents = cfg.get("agents", {})
                updated = False
                for def_id, def_data in DEFAULT_AGENTS_CONFIG["agents"].items():
                    if def_id not in agents:
                        agents[def_id] = def_data
                        updated = True
                    else:
                        existing_agent = agents[def_id]
                        cur_models = existing_agent.get("models", [])
                        new_models = def_data.get("models", [])
                        # Đồng bộ danh sách models mới mà không làm mất model tùy chỉnh của user
                        merged_models = []
                        for m in new_models:
                            if m not in merged_models:
                                merged_models.append(m)
                        for m in cur_models:
                            if m not in merged_models and not m.startswith(RETIRED_MODEL_PREFIXES):
                                merged_models.append(m)
                        if merged_models != cur_models:
                            existing_agent["models"] = merged_models
                            updated = True
                        if def_data.get("default_model") and existing_agent.get("default_model") not in merged_models:
                            existing_agent["default_model"] = def_data["default_model"]
                            updated = True
                if updated:
                    cfg["agents"] = agents
                    self.save_config(cfg)
            except Exception as e:
                print(f"[AgentsManager] Lỗi kiểm tra agent mặc định: {e}")

    def load_config(self) -> Dict[str, Any]:
        """Tải file cấu hình JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[AgentsManager] Lỗi đọc config: {e}")
        return DEFAULT_AGENTS_CONFIG.copy()

    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Lưu file cấu hình JSON"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[AgentsManager] Lỗi lưu config: {e}")
            return False

    def get_effective_key(self, agent_data: Dict[str, Any], custom_key: Optional[str] = None) -> str:
        """Lấy API key từ custom_key, config hoặc biến môi trường"""
        if custom_key and custom_key.strip():
            return custom_key.strip()
        
        key = (agent_data.get("api_key") or "").strip()
        if not key:
            env_var = agent_data.get("api_key_env", "")
            if env_var:
                key = (os.environ.get(env_var) or "").strip()
            # Fallback cho Grok
            if not key and agent_data.get("id") == "grok":
                key = (os.environ.get("GROK_API_KEY") or "").strip()
        return key

    def get_public_agents_info(self) -> Dict[str, Any]:
        """Trả về thông tin agents an toàn (đã ẩn key) cho Frontend"""
        cfg = self.load_config()
        active_id = cfg.get("active_agent", "claude")
        agents_dict = cfg.get("agents", {})

        public_agents = []
        for a_id, a_data in agents_dict.items():
            key = self.get_effective_key(a_data)
            claude_code = self.uses_claude_code(a_id, a_data)
            antigravity = self.uses_antigravity(a_id, a_data)
            has_key = bool(key) or claude_code or antigravity
            masked_key = ""
            if claude_code:
                masked_key = f"Claude Code đã đăng nhập ({self._claude_code_status['auth_method'] or 'claude.ai'})"
            elif antigravity:
                quota = self._antigravity_status["quota"]
                masked_key = "Antigravity CLI đã đăng nhập" + (f" ({quota})" if quota else "")
            elif has_key:
                if len(key) > 8:
                    masked_key = key[:4] + "..." + key[-4:]
                else:
                    masked_key = "********"

            public_agents.append({
                "id": a_id,
                "name": a_data.get("name", a_id),
                "provider": a_data.get("provider", ""),
                "badge": a_data.get("badge", ""),
                "color": a_data.get("color", "#6366F1"),
                "icon": a_data.get("icon", "🤖"),
                "description": a_data.get("description", ""),
                "cli_command": a_data.get("cli_command", ""),
                "api_key_env": a_data.get("api_key_env", ""),
                "has_key": has_key,
                "masked_key": masked_key,
                "auth_mode": "claude_code" if claude_code else "antigravity" if antigravity else "api_key",
                "base_url": a_data.get("base_url", ""),
                "default_model": a_data.get("default_model", ""),
                "models": a_data.get("models", []),
                "model_labels": a_data.get("model_labels", {}),
                "models_source": a_data.get("models_source", "default"),
                "models_updated_at": a_data.get("models_updated_at", ""),
                "models_status": self._models_status.get(a_id, {}),
                "max_tokens": a_data.get("max_tokens", 4096),
                "temperature": a_data.get("temperature", 0.7),
                "system_prompt": a_data.get("system_prompt", ""),
                "is_active": (a_id == active_id)
            })

        return {
            "active_agent": active_id,
            "agents": public_agents
        }

    def set_active_agent(self, agent_id: str) -> bool:
        """Đặt agent mặc định hoạt động"""
        cfg = self.load_config()
        if agent_id in cfg.get("agents", {}):
            cfg["active_agent"] = agent_id
            return self.save_config(cfg)
        return False

    def update_agent_config(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Cập nhật thiết lập cho một agent"""
        cfg = self.load_config()
        if agent_id not in cfg.get("agents", {}):
            return False

        agent_data = cfg["agents"][agent_id]
        allowed_fields = [
            "api_key", "default_model", "temperature",
            "max_tokens", "system_prompt", "base_url"
        ]
        for field in allowed_fields:
            if field in updates:
                agent_data[field] = updates[field]

        # Đổi key/base_url → lần load sau phải lấy lại danh sách model
        if "api_key" in updates or "base_url" in updates:
            self._models_fetched_at.pop(agent_id, None)

        return self.save_config(cfg)

    def _fetch_models(self, agent_id: str, agent: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
        """Gọi API của nhà cung cấp để lấy danh sách model mà API key được phép dùng"""
        provider = agent.get("provider", agent_id)
        base_url = (agent.get("base_url") or "").rstrip("/")
        models: List[Dict[str, Any]] = []

        if provider == "anthropic":
            base_url = base_url or "https://api.anthropic.com/v1"
            headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
            after_id = None
            while True:
                params = {"limit": 1000}
                if after_id:
                    params["after_id"] = after_id
                data = _http_get_json(f"{base_url}/models?{urllib.parse.urlencode(params)}", headers)
                for m in data.get("data", []):
                    models.append({
                        "id": m["id"],
                        "label": m.get("display_name") or m["id"],
                        "created": _parse_created(m.get("created_at")),
                    })
                if not data.get("has_more") or not data.get("last_id"):
                    break
                after_id = data["last_id"]

        elif provider == "google":
            base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
            page_token = None
            while True:
                params = {"key": key, "pageSize": 1000}
                if page_token:
                    params["pageToken"] = page_token
                data = _http_get_json(f"{base_url}/models?{urllib.parse.urlencode(params)}")
                for m in data.get("models", []):
                    model_id = m.get("name", "").replace("models/", "")
                    if not model_id.startswith("gemini"):
                        continue
                    if "generateContent" not in m.get("supportedGenerationMethods", []):
                        continue
                    if not _is_chat_model(model_id):
                        continue
                    models.append({"id": model_id, "label": m.get("displayName") or model_id, "created": 0})
                page_token = data.get("nextPageToken")
                if not page_token:
                    break

        elif provider in ("openai", "xai"):
            default_base = "https://api.openai.com/v1" if provider == "openai" else "https://api.x.ai/v1"
            base_url = base_url or default_base
            data = _http_get_json(f"{base_url}/models", {"Authorization": f"Bearer {key}"})
            id_pattern = r"^(gpt-|chatgpt-|o\d)" if provider == "openai" else r"^grok"
            for m in data.get("data", []):
                model_id = m.get("id", "")
                if not re.match(id_pattern, model_id) or not _is_chat_model(model_id):
                    continue
                models.append({"id": model_id, "label": model_id, "created": _parse_created(m.get("created"))})

        else:
            raise ValueError(f"Nhà cung cấp '{provider}' chưa hỗ trợ lấy danh sách model")

        return _sort_models(models)

    def _fetch_antigravity_models(self) -> List[Dict[str, Any]]:
        """Lấy danh sách model Gemini mà tài khoản Antigravity được dùng (`agy models`, giữ thứ tự của CLI)"""
        proc = subprocess.run(
            ["agy", "models"], capture_output=True, text=True, timeout=60, cwd=tempfile.gettempdir()
        )
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "").strip()[:300] or f"agy models exit {proc.returncode}")
        models = []
        for line in proc.stdout.splitlines():
            cols = line.strip().split("\t")
            if len(cols) >= 2 and cols[0].startswith("gemini-"):
                models.append({"id": cols[0], "label": f"{cols[1]} – Antigravity CLI"})
        return models

    async def refresh_models(self, force: bool = False) -> Dict[str, Dict[str, Any]]:
        """Lấy danh sách model mới nhất của mọi agent có API key (chạy song song) và lưu vào config.
        Lỗi mạng/key sai → giữ nguyên danh sách đã lưu lần trước."""
        async with self._models_lock:
            cfg = self.load_config()
            agents = cfg.get("agents", {})
            now = time.time()
            loop = asyncio.get_event_loop()

            jobs = {}
            antigravity_ids = set()
            changed = False
            for a_id, a_data in agents.items():
                if self.uses_claude_code(a_id, a_data):
                    # Claude Code: alias opus/sonnet/haiku luôn là bản mới nhất, không cần gọi API
                    ids = list(CLAUDE_CODE_MODELS)
                    if a_data.get("models") != ids or a_data.get("models_source") != "claude_code":
                        a_data["models"] = ids
                        a_data["model_labels"] = dict(CLAUDE_CODE_MODELS)
                        a_data["models_source"] = "claude_code"
                        a_data["models_updated_at"] = datetime.now().isoformat(timespec="seconds")
                        changed = True
                    if a_data.get("default_model") not in ids:
                        a_data["default_model"] = "opus"
                        changed = True
                    self._models_status[a_id] = {"ok": True, "count": len(ids), "mode": "claude_code"}
                    continue
                if self.uses_antigravity(a_id, a_data):
                    if not force and now - self._models_fetched_at.get(a_id, 0) < MODELS_CACHE_TTL:
                        continue
                    antigravity_ids.add(a_id)
                    jobs[a_id] = loop.run_in_executor(None, self._fetch_antigravity_models)
                    continue
                key = self.get_effective_key(a_data)
                if not key:
                    self._models_status[a_id] = {"ok": False, "error": "Chưa có API key – dùng danh sách mặc định"}
                    continue
                if not force and now - self._models_fetched_at.get(a_id, 0) < MODELS_CACHE_TTL:
                    continue
                jobs[a_id] = loop.run_in_executor(None, self._fetch_models, a_id, a_data, key)

            results = await asyncio.gather(*jobs.values(), return_exceptions=True) if jobs else []
            for a_id, result in zip(jobs.keys(), results):
                self._models_fetched_at[a_id] = now
                if isinstance(result, Exception):
                    if isinstance(result, urllib.error.HTTPError):
                        err = f"HTTP {result.code}" + (" – API key không hợp lệ" if result.code in (401, 403) else "")
                    else:
                        err = str(result) or result.__class__.__name__
                    self._models_status[a_id] = {"ok": False, "error": f"Không lấy được danh sách model: {err}"}
                    continue
                if not result:
                    self._models_status[a_id] = {"ok": False, "error": "API không trả về model chat nào"}
                    continue

                agent = agents[a_id]
                ids = [m["id"] for m in result]
                agent["models"] = ids
                agent["model_labels"] = {m["id"]: m["label"] for m in result}
                agent["models_updated_at"] = datetime.now().isoformat(timespec="seconds")
                if a_id in antigravity_ids:
                    agent["models_source"] = "antigravity"
                    if agent.get("default_model") not in ids:
                        agent["default_model"] = ANTIGRAVITY_DEFAULT_MODEL if ANTIGRAVITY_DEFAULT_MODEL in ids else ids[0]
                    self._models_status[a_id] = {"ok": True, "count": len(ids), "mode": "antigravity"}
                    changed = True
                    continue
                agent["models_source"] = "live"
                if agent.get("default_model") not in ids:
                    family = PREFERRED_DEFAULT_FAMILY.get(a_id, "")
                    agent["default_model"] = next((i for i in ids if family and family in i), ids[0])
                self._models_status[a_id] = {"ok": True, "count": len(ids)}
                changed = True

            if changed:
                self.save_config(cfg)
            return self._models_status

    async def execute_agent(
        self,
        agent_id: str,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        custom_api_key: Optional[str] = None,
        max_tokens_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """Chạy truy vấn tới Agent thông qua API trực tiếp"""
        cfg = self.load_config()
        agents = cfg.get("agents", {})
        if agent_id not in agents:
            return {"success": False, "error": f"Agent '{agent_id}' không tồn tại trong cấu hình"}

        agent = agents[agent_id]
        key = self.get_effective_key(agent, custom_api_key)
        provider = agent.get("provider", agent_id)
        active_model = model or agent.get("default_model")
        active_sys_prompt = system_prompt or agent.get("system_prompt", "")
        active_temp = temperature if temperature is not None else agent.get("temperature", 0.7)
        max_tokens = max_tokens_override or agent.get("max_tokens", 4096)

        loop = asyncio.get_event_loop()
        try:
            if self.uses_claude_code(agent_id, agent, custom_api_key):
                res = await loop.run_in_executor(
                    None, self._call_claude_code, active_model, prompt, active_sys_prompt
                )
            elif self.uses_antigravity(agent_id, agent, custom_api_key):
                res = await loop.run_in_executor(
                    None, self._call_antigravity, active_model, prompt, active_sys_prompt
                )
            elif provider == "anthropic" or agent_id == "claude":
                res = await loop.run_in_executor(
                    None, self._call_anthropic, key, active_model, prompt, active_sys_prompt, active_temp, max_tokens
                )
            elif provider == "google" or agent_id == "gemini":
                res = await loop.run_in_executor(
                    None, self._call_gemini, key, active_model, prompt, active_sys_prompt, active_temp, max_tokens
                )
            elif provider == "openai" or agent_id == "gpt_code" or agent_id == "gpt":
                res = await loop.run_in_executor(
                    None, self._call_openai, key, active_model, prompt, active_sys_prompt, active_temp, max_tokens
                )
            elif provider == "xai" or agent_id == "grok":
                res = await loop.run_in_executor(
                    None, self._call_grok, key, active_model, prompt, active_sys_prompt, active_temp, max_tokens
                )
            else:
                return {"success": False, "error": f"Nhà cung cấp '{provider}' chưa được hỗ trợ"}
            return res
        except Exception as e:
            return {"success": False, "error": f"Lỗi khi thực thi {agent_id}: {str(e)}"}

    def _call_claude_code(self, model: str, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Gọi Claude qua Claude Code CLI đã đăng nhập (`claude -p`), không dùng API key"""
        cmd = [
            "claude", "-p", "--output-format", "json",
            "--tools", "",
            "--no-session-persistence", "--disable-slash-commands", "--strict-mcp-config",
        ]
        if model:
            cmd += ["--model", model]
        if system_prompt:
            cmd += ["--system-prompt", system_prompt]

        # Bỏ API key khỏi env để CLI dùng phiên đăng nhập claude.ai thay vì key
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("ANTHROPIC_AUTH_TOKEN", None)

        try:
            proc = subprocess.run(
                cmd, input=prompt, capture_output=True, text=True,
                timeout=CLAUDE_CODE_TIMEOUT, cwd=tempfile.gettempdir(), env=env
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Claude Code quá {CLAUDE_CODE_TIMEOUT} giây không phản hồi"}
        except Exception as e:
            return {"success": False, "error": f"Claude Code Error: {str(e)}"}

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            detail = (proc.stderr or proc.stdout or "").strip()[:500]
            return {"success": False, "error": f"Claude Code lỗi (exit {proc.returncode}): {detail}"}

        if data.get("is_error"):
            return {"success": False, "error": f"Claude Code: {data.get('result') or data.get('subtype')}"}

        resolved = list((data.get("modelUsage") or {}).keys())
        return {
            "success": True,
            "agent": "claude",
            "model": resolved[0] if resolved else model,
            "mode": "claude_code",
            "response": data.get("result", ""),
            "usage": data.get("usage", {})
        }

    def _call_antigravity(self, model: str, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """Gọi Gemini qua Antigravity CLI đã đăng nhập (`agy`), không dùng API key.
        Nội dung gửi qua stdin (stream-json) để bài dài không vượt giới hạn tham số dòng lệnh."""
        # agy không có cờ system prompt → ghép vào đầu tin nhắn
        content = (
            "Trả lời trực tiếp trong tin nhắn này. Không dùng công cụ, không tạo file, không lập kế hoạch.\n\n"
            + (f"{system_prompt}\n\n---\n\n" if system_prompt else "")
            + prompt
        )
        message = json.dumps({"event": "user", "message": {"content": content}}, ensure_ascii=False)
        cmd = [
            "agy", "--print=", "--input-format", "stream-json", "--output-format", "stream-json",
            "--mode", "plan", "--sandbox", "--disable-slash-commands",
        ]
        if model:
            cmd += ["--model", model]

        # Bỏ API key khỏi env để CLI dùng phiên đăng nhập Google thay vì key
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)

        workdir = tempfile.mkdtemp(prefix="eeat-agy-")
        try:
            proc = subprocess.run(
                cmd, input=message + "\n", capture_output=True, text=True,
                timeout=ANTIGRAVITY_TIMEOUT, cwd=workdir, env=env
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Antigravity CLI quá {ANTIGRAVITY_TIMEOUT} giây không phản hồi"}
        except Exception as e:
            return {"success": False, "error": f"Antigravity CLI Error: {str(e)}"}
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

        result, active_model = None, model
        for line in proc.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event") == "init":
                active_model = (event.get("init") or {}).get("model") or active_model
            elif event.get("event") == "result":
                result = event.get("result") or {}

        if result is None:
            detail = (proc.stderr or proc.stdout or "").strip()[:500]
            return {"success": False, "error": f"Antigravity CLI lỗi (exit {proc.returncode}): {detail}"}
        if result.get("status") != "SUCCESS":
            return {"success": False, "error": f"Antigravity CLI: {result.get('error') or result.get('status')}"}

        return {
            "success": True,
            "agent": "gemini",
            "model": active_model,
            "mode": "antigravity",
            "response": (result.get("response") or "").strip(),
            "usage": result.get("usage", {})
        }

    def _call_anthropic(
        self,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Gọi Anthropic Claude Messages API"""
        if not api_key:
            return {
                "success": False,
                "error": "Thiếu ANTHROPIC_API_KEY. Vui lòng cấu hình API key trong mục Thiết Lập Agent hoặc biến môi trường."
            }

        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            # Không gửi temperature: từ 21/10/2026 Anthropic trả lỗi 400 nếu có tham số này
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        if system_prompt:
            payload["system"] = system_prompt

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                content_blocks = res_json.get("content", [])
                text_content = "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
                usage = res_json.get("usage", {})
                return {
                    "success": True,
                    "agent": "claude",
                    "model": model,
                    "response": text_content,
                    "usage": usage
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            return {"success": False, "error": f"Anthropic HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"success": False, "error": f"Anthropic Error: {str(e)}"}

    def _call_gemini(
        self,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Gọi Google Gemini generateContent API"""
        if not api_key:
            return {
                "success": False,
                "error": "Thiếu GEMINI_API_KEY. Vui lòng cấu hình API key trong mục Thiết Lập Agent hoặc biến môi trường."
            }

        clean_model = model.replace("models/", "").strip() if model else "gemini-3.8-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"
        contents = [{"parts": [{"text": prompt}]}]
        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                candidates = res_json.get("candidates", [])
                if not candidates:
                    prompt_feedback = res_json.get("promptFeedback", {})
                    block_reason = prompt_feedback.get("blockReason")
                    if block_reason:
                        return {"success": False, "error": f"Gemini bị chặn bởi bộ lọc an toàn: {block_reason}"}
                    return {"success": False, "error": "Gemini không trả về kết quả nào."}
                
                parts = candidates[0].get("content", {}).get("parts", [])
                text_content = "".join([p.get("text", "") for p in parts if "text" in p])
                usage = res_json.get("usageMetadata", {})
                return {
                    "success": True,
                    "agent": "gemini",
                    "model": model,
                    "response": text_content,
                    "usage": usage
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            return {"success": False, "error": f"Gemini HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"success": False, "error": f"Gemini Error: {str(e)}"}

    def _call_openai(
        self,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Gọi OpenAI GPT chat completions API"""
        if not api_key:
            return {
                "success": False,
                "error": "Thiếu OPENAI_API_KEY. Vui lòng cấu hình API key trong mục Thiết Lập Agent hoặc biến môi trường."
            }

        url = "https://api.openai.com/v1/chat/completions"
        is_reasoning_model = any(model.startswith(prefix) for prefix in ["o1", "o3", "o4"])
        role_name = "developer" if is_reasoning_model else "system"
        messages = []
        if system_prompt:
            messages.append({"role": role_name, "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages
        }
        if is_reasoning_model:
            payload["max_completion_tokens"] = max_tokens
        else:
            payload["temperature"] = temperature
            payload["max_tokens"] = max_tokens


        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                choices = res_json.get("choices", [])
                if not choices:
                    return {"success": False, "error": "OpenAI không trả về kết quả nào."}
                
                text_content = choices[0].get("message", {}).get("content", "")
                usage = res_json.get("usage", {})
                return {
                    "success": True,
                    "agent": "gpt_code",
                    "model": model,
                    "response": text_content,
                    "usage": usage
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            return {"success": False, "error": f"OpenAI HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"success": False, "error": f"OpenAI Error: {str(e)}"}

    def _call_grok(
        self,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Gọi xAI Grok API (OpenAI compatible)"""
        if not api_key:
            return {
                "success": False,
                "error": "Thiếu XAI_API_KEY / GROK_API_KEY. Vui lòng cấu hình API key trong mục Thiết Lập Agent hoặc biến môi trường."
            }

        url = "https://api.x.ai/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                choices = res_json.get("choices", [])
                if not choices:
                    return {"success": False, "error": "Grok không trả về kết quả nào."}

                text_content = choices[0].get("message", {}).get("content", "")
                usage = res_json.get("usage", {})
                return {
                    "success": True,
                    "agent": "grok",
                    "model": model,
                    "response": text_content,
                    "usage": usage
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            return {"success": False, "error": f"xAI Grok HTTP {e.code}: {err_msg}"}
        except Exception as e:
            return {"success": False, "error": f"xAI Grok Error: {str(e)}"}


# Khởi tạo singleton instance
agents_manager = AgentsManager()
