import os
import json
import asyncio
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import BASE_DIR

CONFIG_FILE_PATH = BASE_DIR / "config" / "agents_config.json"

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
            "default_model": "claude-3-7-sonnet-20250219",
            "models": [
                "claude-3-7-sonnet-20250219",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022"
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
            "default_model": "gemini-2.5-flash",
            "models": [
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
                "gpt-4o",
                "gpt-4o-mini",
                "o3-mini",
                "gpt-4-turbo"
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
            "default_model": "grok-2-latest",
            "models": [
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


class AgentsManager:
    def __init__(self):
        self.config_path = CONFIG_FILE_PATH
        self._ensure_config()

    def _ensure_config(self):
        """Đảm bảo file cấu hình tồn tại"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_AGENTS_CONFIG, f, indent=2, ensure_ascii=False)
        else:
            # Đảm bảo các agent mới như grok được thêm vào nếu file cũ chưa có
            try:
                cfg = self.load_config()
                agents = cfg.get("agents", {})
                updated = False
                for def_id, def_data in DEFAULT_AGENTS_CONFIG["agents"].items():
                    if def_id not in agents:
                        agents[def_id] = def_data
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
            has_key = bool(key)
            masked_key = ""
            if has_key:
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
                "base_url": a_data.get("base_url", ""),
                "default_model": a_data.get("default_model", ""),
                "models": a_data.get("models", []),
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

        return self.save_config(cfg)

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
            if provider == "anthropic" or agent_id == "claude":
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
            "temperature": temperature,
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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
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
                    return {"success": False, "error": "Gemini không trả về kết quả nào."}
                
                parts = candidates[0].get("content", {}).get("parts", [])
                text_content = "".join([p.get("text", "") for p in parts])
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
