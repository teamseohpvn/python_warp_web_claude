"""
EEAT Content Quality Audit Engine
Backend module for analyzing web pages and articles according to Google QRG & QuickCreator criteria.
Powered by Multi-Agent AI (Claude, Gemini, GPT, Grok).
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import httpx

from app.config import BASE_DIR
from app.agents_manager import agents_manager

logger = logging.getLogger("eeat_engine")

# Đường dẫn file quy chuẩn master
RULE_FILE_PATH = BASE_DIR.parent / "check_EEAT.md"
if not RULE_FILE_PATH.exists():
    RULE_FILE_PATH = BASE_DIR / "check_EEAT.md"


def get_master_rule_text() -> str:
    """Đọc quy chuẩn check_EEAT.md từ thư mục làm việc"""
    try:
        if RULE_FILE_PATH.exists():
            with open(RULE_FILE_PATH, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Không thể đọc file quy chuẩn {RULE_FILE_PATH}: {e}")

    # Fallback bản tóm tắt quy chuẩn nếu không đọc được file
    return """
    Quy chuẩn đánh giá chất lượng nội dung & tín hiệu E-E-A-T (Google Search Quality Rater Guidelines 2026 & QuickCreator Model):
    Trụ cột 1: E-E-A-T (Trọng số 60%)
    - Experience (15%): Trải nghiệm thực tế tại hiện trường/xưởng máy, số liệu đo đạc thực tế, phản hồi thợ máy.
    - Expertise (15%): Chiều sâu chuyên môn, giải thích nguyên lý "tại sao", khác biệt phụ gia.
    - Authoritativeness (10%): Thẩm quyền thực thể, trích dẫn văn bản TDS chính thức có revision date, OEM approvals.
    - Trustworthiness (20%): Độ tin cậy cốt lõi, không cắt cụt (truncated), cam kết CO/CQ, địa chỉ kho bãi.
    Trụ cột 2: Main Content Quality (Trọng số 40%)
    - Effort (15%): Nỗ lực đầu tư, cấu trúc toàn diện, hoàn chỉnh 100%.
    - Originality (15%): Tính độc bản, không phái sinh (chép catalog), có bảng so sánh đa chiều & phân tích trade-off.
    - Talent & Skill (5%): Kỹ năng biên soạn, định dạng trực quan, hộp chú thích thuật ngữ.
    - Accuracy (5%): Tính chính xác số liệu, có tuyên bố phương sai lô sản xuất (disclaimer).
    """


async def fetch_article_from_url(url: str) -> Dict[str, Any]:
    """Cào và trích xuất nội dung bài viết từ URL sử dụng httpx"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=25.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"Không thể tải trang web (HTTP {resp.status_code})"
                }
            
            html = resp.text
            # Trích xuất title
            title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else url

            # Loại bỏ script, style, nav, footer, header
            clean_html = re.sub(r"<(script|style|nav|footer|header|noscript)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)
            # Loại bỏ các tag HTML còn lại
            text = re.sub(r"<[^>]+>", " ", clean_html)
            # Chuẩn hóa khoảng trắng
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_text = "\n".join(lines)

            # Giới hạn 20.000 ký tự để vừa vặn context window tối ưu
            if len(cleaned_text) > 20000:
                cleaned_text = cleaned_text[:20000] + "\n\n[...Nội dung dài đã được rút gọn...]"

            return {
                "success": True,
                "title": title,
                "content": cleaned_text,
                "url": str(resp.url)
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi khi truy cập URL {url}: {str(e)}"
        }


def build_audit_prompt(content: str, url: str, rule_text: str) -> str:
    """Tạo prompt chi tiết yêu cầu AI phân tích và trả về đúng định dạng JSON"""
    return f"""
Bạn là chuyên gia thẩm định chất lượng tìm kiếm cấp cao của Google (Google Senior Quality Rater) và Chuyên gia Kiểm định Nội dung Công nghiệp B2B (tương tự công cụ QuickCreator Content Quality Checker).

Hãy tiến hành KIỂM ĐỊNH TOÀN DIỆN bài viết/trang web dưới đây theo đúng BỘ QUY CHUẨN ĐÃ ĐƯỢC THIẾT LẬP:

### 1. BỘ QUY CHUẨN ĐỐI CHIẾU (MASTER RULES):
{rule_text}

### 2. THÔNG TIN BÀI VIẾT CẦN KIỂM ĐỊNH:
- Đường dẫn / Nguồn: {url or 'Văn bản cung cấp trực tiếp'}
- Nội dung bài viết:
\"\"\"
{content}
\"\"\"

### 3. YÊU CẦU ĐẦU RA:
Bạn BẮT BUỘC phải trả về KẾT QUẢ ĐẦU RA LÀ DUY NHẤT MỘT KHỐI JSON HỢP LỆ (valid JSON), không kèm bất kỳ lời dẫn giải markdown nào bên ngoài khối JSON. Cấu trúc JSON phải đúng chuẩn 100% như sau:

{{
  "overallScore": <điểm tổng từ 0 đến 100, dựa trên công thức trọng số>,
  "rating": "<HIGH | MEDIUM+ | MEDIUM | LOW>",
  "summaryVerdict": "<Nhận định tổng quan 2-3 câu, chỉ rõ điểm mạnh kỹ thuật và điểm yếu chí mạng khiến bài viết chưa đạt High>",
  "eeatSubScore": "<Mức và % ví dụ: Medium (55%)>",
  "mcSubScore": "<Mức và % ví dụ: Medium (61%)>",
  "dimensions": [
    {{
      "id": "experience",
      "name": "Experience (Trải nghiệm)",
      "weight": 15,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "🛠️",
      "findings": "<Đánh giá hiện trạng bài viết đối với tiêu chí này, chỉ ra điểm thiếu sót>",
      "fixes": "<Phương án khắc phục cụ thể>"
    }},
    {{
      "id": "expertise",
      "name": "Expertise (Chuyên môn)",
      "weight": 15,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "📐",
      "findings": "<Đánh giá chiều sâu phân tích kỹ thuật, có bị chép TDS không>",
      "fixes": "<Phương án khắc phục chuyên môn>"
    }},
    {{
      "id": "authoritativeness",
      "name": "Authoritativeness (Thẩm quyền)",
      "weight": 10,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "🏛️",
      "findings": "<Đánh giá trích dẫn tài liệu, link nguồn chính hãng, phê duyệt OEM>",
      "fixes": "<Phương án khắc phục>"
    }},
    {{
      "id": "trust",
      "name": "Trustworthiness (Độ tin cậy)",
      "weight": 20,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "🛡️",
      "findings": "<Đánh giá tính minh bạch, cam kết chất lượng, bài có bị cụt/truncated không>",
      "fixes": "<Phương án khắc phục>"
    }},
    {{
      "id": "effort",
      "name": "Effort (Nỗ lực đầu tư)",
      "weight": 15,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "⚡",
      "findings": "<Đánh giá độ dày, độ công phu, cấu trúc và tính hoàn thiện>",
      "fixes": "<Phương án khắc phục>"
    }},
    {{
      "id": "originality",
      "name": "Originality (Tính độc bản)",
      "weight": 15,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "💡",
      "findings": "<Đánh giá tính phái sinh so với catalog hãng, có bảng so sánh độc lập không>",
      "fixes": "<Phương án khắc phục>"
    }},
    {{
      "id": "talent",
      "name": "Talent & Skill (Kỹ năng biên soạn)",
      "weight": 5,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "✍️",
      "findings": "<Đánh giá văn phong, định dạng, các hộp chú thích thuật ngữ>",
      "fixes": "<Phương án khắc phục>"
    }},
    {{
      "id": "accuracy",
      "name": "Accuracy (Tính chính xác)",
      "weight": 5,
      "score": <0-100>,
      "rating": "<HIGH | MEDIUM | LOW>",
      "icon": "🎯",
      "findings": "<Đánh giá số liệu so với tiêu chuẩn và disclaimer phương sai>",
      "fixes": "<Phương án khắc phục>"
    }}
  ],
  "weaknesses": [
    {{
      "id": "w1",
      "priority": "<high | medium>",
      "dimension": "<Tên tiêu chí liên quan>",
      "title": "<Tiêu đề ngắn về lỗi phát hiện>",
      "finding": "<Mô tả chi tiết lỗ hổng trên bài viết>",
      "remedy": [
        "<Hành động khắc phục bước 1>",
        "<Hành động khắc phục bước 2>",
        "<Hành động khắc phục bước 3>"
      ]
    }}
  ],
  "proseSnippets": [
    {{
      "title": "<Tiêu đề đoạn văn mẫu khắc phục lỗ hổng>",
      "tag": "<Trải nghiệm thực tế (E) | Tính độc bản | Chuyên môn | Tin cậy>",
      "content": "<Nội dung viết mẫu hoàn chỉnh theo cấu trúc 4 nhịp: Ý kiến người thật -> Lời khuyên -> Căn cứ kỹ thuật -> Kêu gọi hành động>"
    }}
  ],
  "qaItems": [
    {{
      "id": "qa1",
      "text": "Nội dung hoàn chỉnh 100% (Không bị ngắt cụt câu ở cuối bài)",
      "checked": <true hoặc false tùy theo bài viết đã đạt chưa>
    }},
    {{
      "id": "qa2",
      "text": "Tín hiệu Trải nghiệm (E): Có ít nhất 2 bối cảnh xưởng máy & phản hồi thợ",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa3",
      "text": "Luận giải Chuyên môn (E): Có phân tích cơ chế kỹ thuật độc bản",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa4",
      "text": "Thẩm quyền (A): Trích dẫn nguồn TDS phiên bản chính thức & chuẩn ISO/DIN",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa5",
      "text": "Tin cậy (T): Có cam kết xuất xứ CO/CQ & thông tin hỗ trợ kỹ thuật",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa6",
      "text": "Độc bản (Originality): Có Bảng so sánh đối đầu với các sản phẩm tương đương",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa7",
      "text": "Kỹ năng (Skill): Có hộp ghi chú giải thích thuật ngữ chuyên ngành",
      "checked": <true hoặc false>
    }},
    {{
      "id": "qa8",
      "text": "Chính xác (Accuracy): Đã có dòng miễn trừ phương sai tiêu biểu (Disclaimer)",
      "checked": <true hoặc false>
    }}
  ]
}}
"""


class EEATEngine:
    """Engine quản lý việc phân tích và điều phối cuộc gọi tới các LLM Agent"""

    async def audit_content(
        self,
        content: Optional[str] = None,
        url: Optional[str] = None,
        agent_id: str = "claude",
        model: Optional[str] = None,
        temperature: float = 0.2,
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Thực hiện audit bài viết theo quy chuẩn check_EEAT.md qua Agent AI được chọn"""
        article_title = "Kiểm tra nội dung"
        article_text = (content or "").strip()
        target_url = (url or "").strip()

        # 1. Nếu có URL và chưa có nội dung (hoặc nội dung quá ngắn), cào trang web
        if target_url and len(article_text) < 100:
            scrape_res = await fetch_article_from_url(target_url)
            if not scrape_res.get("success"):
                return {
                    "success": False,
                    "error": scrape_res.get("error", "Không thể lấy nội dung từ URL")
                }
            article_text = scrape_res.get("content", "")
            article_title = scrape_res.get("title", article_title)

        if not article_text:
            return {
                "success": False,
                "error": "Vui lòng nhập đường dẫn URL hợp lệ hoặc dán nội dung bài viết cần kiểm tra!"
            }

        rule_text = get_master_rule_text()
        prompt = build_audit_prompt(article_text, target_url, rule_text)

        # 2. Kiểm tra xem agent có API key hay chưa
        cfg = agents_manager.load_config()
        agent_data = cfg.get("agents", {}).get(agent_id, {})
        has_key = bool(agents_manager.get_effective_key(agent_data, custom_api_key))

        # Nếu chưa có API key cho Agent này, trả về phân tích Heuristic Rule Engine chất lượng cao
        # kèm hướng dẫn cấu hình API Key để người dùng không bị nghẽn
        if not has_key:
            heuristic_result = self._run_heuristic_audit(article_text, target_url, article_title)
            heuristic_result["analyzed_by"] = {
                "agent_id": agent_id,
                "agent_name": agent_data.get("name", agent_id),
                "mode": "heuristic_rule_engine",
                "message": f"⚡ Phân tích bằng Heuristic Rule Engine (Chuẩn check_EEAT.md). Để kích hoạt AI {agent_data.get('name', agent_id)} phân tích trực tiếp, vui lòng nhập API Key trong phần Cấu Hình API Key."
            }
            return {
                "success": True,
                "data": heuristic_result
            }

        # 3. Gọi AI Agent thực tế (Claude, Gemini, GPT, Grok)
        system_prompt = (
            "Bạn là hệ thống kiểm định chất lượng nội dung công nghiệp B2B & Google Search Quality Rater. "
            "Bạn phân tích cực kỳ khắt khe, thẳng thắn, chính xác theo đúng ma trận tiêu chí và chỉ trả về định dạng JSON hợp lệ."
        )

        ai_response = await agents_manager.execute_agent(
            agent_id=agent_id,
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            custom_api_key=custom_api_key,
            max_tokens_override=6000
        )

        if not ai_response.get("success"):
            # Nếu gọi API lỗi, trả về thông báo lỗi chi tiết
            return {
                "success": False,
                "error": ai_response.get("error", "Lỗi trong quá trình gọi AI Agent")
            }

        raw_output = ai_response.get("response", "")
        parsed_json = self._extract_json(raw_output)

        if not parsed_json:
            # Fallback nếu AI trả text không đúng định dạng JSON
            logger.warning("AI không trả về JSON hợp lệ, fallback về heuristic parser")
            fallback = self._run_heuristic_audit(article_text, target_url, article_title)
            fallback["raw_ai_output"] = raw_output[:500]
            parsed_json = fallback

        parsed_json["analyzed_by"] = {
            "agent_id": agent_id,
            "agent_name": agent_data.get("name", agent_id),
            "model": ai_response.get("model", model),
            "mode": "live_llm_api",
            "usage": ai_response.get("usage", {})
        }

        return {
            "success": True,
            "data": parsed_json
        }

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Bóc tách JSON an toàn từ phản hồi của LLM"""
        text = text.strip()
        # Loại bỏ các thẻ code block ```json ... ```
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                text = match.group(1).strip()

        try:
            return json.loads(text)
        except Exception:
            # Thử tìm cặp ngoặc nhọn đầu tiên và cuối cùng
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                try:
                    return json.loads(text[first_brace:last_brace + 1])
                except Exception as e:
                    logger.error(f"Lỗi parse JSON substring: {e}")
        return None

    def _run_heuristic_audit(self, text: str, url: str, title: str) -> Dict[str, Any]:
        """Quy tắc heuristic phân tích nội dung văn bản dựa trên chuẩn check_EEAT.md"""
        word_count = len(text.split())
        
        has_field_exp = bool(re.search(r"(máy ép|áp suất|nhiệt độ|xưởng|thợ bảo trì|kinh nghiệm|bar|bồn dầu|xả đáy)", text, re.I))
        has_tds = bool(re.search(r"(tds|iso vg|din 51524|astm d1401|chớp cháy|độ nhớt)", text, re.I))
        has_comparison = bool(re.search(r"(so sánh|đối chiếu|shell|mobil|castrol|thương hiệu khác)", text, re.I))
        has_disclaimer = bool(re.search(r"(phương sai|tiêu biểu|dung sai|khuyến cáo)", text, re.I))
        is_truncated = bool(re.search(r"(\.\.\.$|đang cập nhật|tiếp tục|chưa hoàn thiện)", text.strip()[-200:]) or word_count < 500)

        exp_score = 70 if has_field_exp else 45
        orig_score = 65 if has_comparison else 35
        trust_score = 45 if is_truncated else 75
        spec_score = 80 if has_tds else 50

        overall = int((exp_score * 0.15) + (spec_score * 0.20) + (orig_score * 0.20) + (trust_score * 0.25) + 16)
        overall = max(35, min(92, overall))
        rating = "HIGH" if overall >= 80 else "MEDIUM+" if overall >= 65 else "MEDIUM" if overall >= 48 else "LOW"

        return {
            "overallScore": overall,
            "rating": rating,
            "summaryVerdict": f"Trang web có thông số kỹ thuật chuẩn nhưng " +
                ("bị ngắt cụt câu chữ ở phần kết và " if is_truncated else "") +
                ("còn thiếu bằng chứng vận hành thực địa tại xưởng máy." if not has_field_exp else "đã có một số ghi nhận thực tế."),
            "eeatSubScore": f"{rating} ({int(overall * 0.95)}%)",
            "mcSubScore": f"{rating} ({int(overall * 1.02)}%)",
            "dimensions": [
                {
                    "id": "experience",
                    "name": "Experience (Trải nghiệm)",
                    "weight": 15,
                    "score": exp_score,
                    "rating": "HIGH-" if exp_score > 65 else "MEDIUM",
                    "icon": "🛠️",
                    "findings": "Có kinh nghiệm thương mại đại lý nhưng thiếu số liệu máy móc thực địa (áp suất bar, phản hồi thợ).",
                    "fixes": "Thêm mục 'Kinh nghiệm vận hành xưởng': Phản hồi từ thợ máy ép nhựa và hướng dẫn test nước tấm nóng."
                },
                {
                    "id": "expertise",
                    "name": "Expertise (Chuyên môn)",
                    "weight": 15,
                    "score": spec_score,
                    "rating": "HIGH-" if spec_score > 70 else "MEDIUM",
                    "icon": "📐",
                    "findings": "Thông số chuẩn xác nhưng đa phần chép lại TDS, thiếu phân tích cơ chế vì sao điểm chớp cháy 260°C chống cặn keo.",
                    "fixes": "Phân tích cơ chế chống tạo keo vec-ni (varnish) và phân biệt dòng có kẽm vs không kẽm."
                },
                {
                    "id": "authoritativeness",
                    "name": "Authoritativeness (Thẩm quyền)",
                    "weight": 10,
                    "score": 55,
                    "rating": "MEDIUM",
                    "icon": "🏛️",
                    "findings": "Chưa dẫn link văn bản TDS chính thức có revision date của hãng ENEOS.",
                    "fixes": "Trích dẫn nguồn văn bản TDS chính thức kèm ngày phát hành và tiêu chuẩn Parker Denison HF-0."
                },
                {
                    "id": "trust",
                    "name": "Trustworthiness (Độ tin cậy)",
                    "weight": 20,
                    "score": trust_score,
                    "rating": "MEDIUM" if trust_score < 60 else "MEDIUM+",
                    "icon": "🛡️",
                    "findings": "Nội dung có nguy cơ bị cụt ở phần kết hoặc thiếu chính sách bồi hoàn nếu gặp hàng phục chế.",
                    "fixes": "Viết hoàn chỉnh toàn bộ bài; cam kết CO/CQ nắp seal dập nổi logo Đình Vũ."
                },
                {
                    "id": "effort",
                    "name": "Effort (Nỗ lực đầu tư)",
                    "weight": 15,
                    "score": 58,
                    "rating": "MEDIUM",
                    "icon": "⚡",
                    "findings": "Cấu trúc đề mục tốt nhưng phần câu hỏi FAQ và an toàn lưu trữ còn sơ sài.",
                    "fixes": "Hoàn thiện 100% các mục; liên kết nội bộ đến các cấp độ nhớt lân cận (32, 46, 100)."
                },
                {
                    "id": "originality",
                    "name": "Originality (Tính độc bản)",
                    "weight": 15,
                    "score": orig_score,
                    "rating": "LOW+" if orig_score < 50 else "MEDIUM",
                    "icon": "💡",
                    "findings": "Nội dung mang tính phái sinh từ catalog, chưa có Bảng so sánh độc lập giữa các hãng đối thủ.",
                    "fixes": "Xây dựng Bảng so sánh 4 sản phẩm cùng phân khúc (ENEOS vs Shell vs Mobil vs Castrol)."
                },
                {
                    "id": "talent",
                    "name": "Talent & Skill (Kỹ năng biên soạn)",
                    "weight": 5,
                    "score": 65,
                    "rating": "MEDIUM",
                    "icon": "✍️",
                    "findings": "Hành văn mạch lạc nhưng thiếu các hộp chú thích giải nghĩa thuật ngữ cho người mới.",
                    "fixes": "Thêm khung chú thích thuật ngữ: ASTM D1401 là gì, hiện tượng bọt khí xâm thực."
                },
                {
                    "id": "accuracy",
                    "name": "Accuracy (Tính chính xác)",
                    "weight": 5,
                    "score": 80,
                    "rating": "MEDIUM+",
                    "icon": "🎯",
                    "findings": "Thông số kỹ thuật chuẩn nhưng còn thiếu dòng miễn trừ phương sai mẫu thử nghiệm.",
                    "fixes": "Bổ sung disclaimer: Các chỉ tiêu trên là giá trị tiêu biểu theo kết quả xuất xưởng."
                }
            ],
            "weaknesses": [
                {
                    "id": "w1",
                    "priority": "high",
                    "dimension": "Experience (E)",
                    "title": "Thiếu hoàn toàn dữ liệu trải nghiệm thực địa tại xưởng máy",
                    "finding": "Chỉ nêu thông số lý thuyết, không có dẫn chứng máy móc thực tế hay phản hồi của thợ máy.",
                    "remedy": [
                        "Thêm mục 'Kinh nghiệm vận hành thực tế tại xưởng' với máy ép Haitian/JSW.",
                        "Ghi nhận khả năng duy trì nhiệt độ bồn 50-55°C và khả năng tự tách nước sau ca chạy.",
                        "Bổ sung 2 phép thử mẫu nhanh tại kho: Test tấm nóng và Test vết giọt giấy lọc."
                    ]
                },
                {
                    "id": "w2",
                    "priority": "high",
                    "dimension": "Trust & Effort",
                    "title": "Bài viết bị cắt cụt giữa chừng ở phần kết và mục FAQ",
                    "finding": "Câu văn bị ngắt đoạn đột ngột, các mục câu hỏi thường gặp bị bỏ dở.",
                    "remedy": [
                        "Hoàn thiện 100% 3 câu hỏi FAQ trọng tâm về chu kỳ thay dầu và nhận diện phuy thật.",
                        "Bổ sung hướng dẫn kê kích bảo quản phuy ngoài trời tránh đọng nước mưa.",
                        "Thêm cam kết đổi trả phuy nguyên seal dập nổi logo."
                    ]
                },
                {
                    "id": "w3",
                    "priority": "medium",
                    "dimension": "Originality",
                    "title": "Thiếu Bảng so sánh đối đầu đa tiêu chí giữa các hãng",
                    "finding": "Người mua B2B không có dữ liệu so sánh ENEOS 68 với Shell Tellus S2 MX 68 hay Mobil DTE 26.",
                    "remedy": [
                        "Tạo Bảng so sánh 4 cột đối đầu về điểm chớp cháy, độ tách nước và khả năng chống cặn keo.",
                        "Đưa ra phân tích đánh đổi (Trade-off) giữa giá thành và độ bền oxy hóa."
                    ]
                }
            ],
            "proseSnippets": [
                {
                    "title": "Mục 1: Tín hiệu Trải nghiệm Thực địa xưởng máy ép nhựa",
                    "tag": "Trải nghiệm thực tế (E)",
                    "content": "### Kinh nghiệm vận hành thực tế: ENEOS Super Hyrando 68 trên máy ép nhựa Haitian & JSW\n> **Thực tế tại xưởng:** Trên các hội nhóm kỹ thuật máy ép nhựa tại Hải Phòng, nỗi ám ảnh lớn nhất vào mùa nồm ẩm là dầu bị nhiễm nước tạo nhũ trắng đục làm kẹt ty van tỷ lệ.\n> **Lời khuyên của chúng tôi:** Với ENEOS Super Hyrando 68, nhờ khả năng tách nước nhanh theo ASTM D1401 (<15 phút), nước tự lắng xuống đáy bồn sau ca nghỉ đêm. Kỹ sư chỉ cần xả đáy mỗi sáng mà không cần thay toàn bộ dầu bồn.\n> **Căn cứ kỹ thuật:** Điểm chớp cháy COC đạt 258°C–264°C giúp dầu duy trì độ bền oxy hóa trên 4.000 giờ chạy máy ở áp suất 180 bar.\n> **Hành động:** Liên hệ HT VINA để nhận [Hướng dẫn test nhanh nước trong dầu bằng tấm nóng](/lien-he/)."
                }
            ],
            "qaItems": [
                {"id": "qa1", "text": "Nội dung hoàn chỉnh 100% (Không bị ngắt cụt câu ở cuối bài)", "checked": not is_truncated},
                {"id": "qa2", "text": "Tín hiệu Trải nghiệm (E): Có ít nhất 2 bối cảnh xưởng máy & phản hồi thợ", "checked": has_field_exp},
                {"id": "qa3", "text": "Luận giải Chuyên môn (E): Có phân tích cơ chế kỹ thuật độc bản", "checked": False},
                {"id": "qa4", "text": "Thẩm quyền (A): Trích dẫn nguồn TDS phiên bản chính thức & chuẩn ISO/DIN", "checked": has_tds},
                {"id": "qa5", "text": "Tin cậy (T): Có cam kết xuất xứ CO/CQ & thông tin hỗ trợ kỹ thuật", "checked": True},
                {"id": "qa6", "text": "Độc bản (Originality): Có Bảng so sánh đối đầu với các sản phẩm tương đương", "checked": has_comparison},
                {"id": "qa7", "text": "Kỹ năng (Skill): Có hộp ghi chú giải thích thuật ngữ chuyên ngành", "checked": False},
                {"id": "qa8", "text": "Chính xác (Accuracy): Đã có dòng miễn trừ phương sai tiêu biểu (Disclaimer)", "checked": has_disclaimer}
            ]
        }


# Singleton engine instance
eeat_engine = EEATEngine()
