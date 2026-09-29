import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
TASK_LOG_DIR = LOG_DIR / "tasks"
SESSION_LOG_DIR = LOG_DIR / "sessions"
AUDIT_LOG_DIR = LOG_DIR / "audit"

for directory in [LOG_DIR, TASK_LOG_DIR, SESSION_LOG_DIR, AUDIT_LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Authentication & Rate Limiting Settings
AUTH_ENABLED = True
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "claude2026")
AUTH_COOKIE_NAME = "claude_hub_token"
RATE_LIMIT_MAX_ATTEMPTS = 10   # Tối đa 10 lần nhập trong 1 phút
RATE_LIMIT_WINDOW_SECONDS = 60 # Cửa sổ thời gian 60 giây

# Default and known working directories
WORKSPACE_ROOT = Path("/root")
PRESET_PROJECTS = [
    {"name": "Site Dầu Công Nghiệp", "path": "/root/site-dau-cong-nghiep", "badge": "SEO Target"},
    {"name": "Bê Tông - Đăng Ký Lên", "path": "/root/betong/danky_len", "badge": "SEO Target"},
    {"name": "Bê Tông - Mr Cường", "path": "/root/betong/mrcuong_betong", "badge": "Target"},
    {"name": "Đăng Ký Lên (Root)", "path": "/root/danky_len", "badge": "Target"},
    {"name": "Claude SEO Engine", "path": "/root/claude-seo", "badge": "Core Tool"},
    {"name": "Claude Blog Engine", "path": "/root/claude-blog", "badge": "Core Tool"},
    {"name": "Root Workspace", "path": "/root", "badge": "General"},
]

# Quick presets for Claude SEO & Claude Blog
PRESETS = [
    {
        "category": "Claude SEO",
        "items": [
            {
                "id": "seo_doctor",
                "title": "SEO Doctor & Setup Diagnostic",
                "desc": "Kiểm tra cấu hình MCP, API key (DataForSEO, Firecrawl) và tính toàn vẹn của skills",
                "cmd": "claude -p '/seo doctor'",
                "type": "cli",
                "args": []
            },
            {
                "id": "seo_audit",
                "title": "Toàn diện Site Audit (Technical + Content + Schema)",
                "desc": "Chạy full audit cho website đích",
                "cmd": "claude -p '/seo:audit {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "https://example.com", "placeholder": "https://..."}]
            },
            {
                "id": "seo_page",
                "title": "Phân tích chuyên sâu 1 Trang (Deep Page Analysis)",
                "desc": "Kiểm tra chi tiết thẻ meta, cấu trúc heading, nội dung, schema của 1 URL",
                "cmd": "claude -p '/seo:page {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Page URL", "default": "", "placeholder": "https://example.com/bai-viet"}]
            },
            {
                "id": "seo_content_brief",
                "title": "Tạo Content Brief chuẩn SEO & E-E-A-T",
                "desc": "Lập dàn ý nội dung bài viết chuyên sâu dựa trên từ khóa mục tiêu",
                "cmd": "claude -p '/seo:content-brief {keyword}'",
                "type": "cli",
                "args": [{"name": "keyword", "label": "Từ khóa chính", "default": "", "placeholder": "dầu nhớt công nghiệp"}]
            },
            {
                "id": "seo_geo",
                "title": "AI Search & GEO Optimization",
                "desc": "Tối ưu hóa để được trích dẫn trên AI search (ChatGPT, Perplexity, Claude)",
                "cmd": "claude -p '/seo:geo {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "URL hoặc Topic", "default": "", "placeholder": "https://example.com hoặc từ khóa"}]
            },
            {
                "id": "seo_technical",
                "title": "Kiểm tra Technical SEO",
                "desc": "Đánh giá tốc độ, robots.txt, sitemap.xml, canonical, hreflang",
                "cmd": "claude -p '/seo:technical {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "", "placeholder": "https://..."}]
            }
        ]
    },
    {
        "category": "Claude Blog",
        "items": [
            {
                "id": "blog_analyze",
                "title": "Đánh giá chất lượng bài viết (analyze_blog.py)",
                "desc": "Chấm điểm 5 tiêu chí: E-E-A-T, cấu trúc, mật độ từ khóa, readability",
                "cmd": "python3 /root/claude-blog/scripts/analyze_blog.py {file_path}",
                "type": "python",
                "args": [{"name": "file_path", "label": "Đường dẫn file Markdown", "default": "/root/ke-hoach-seo-dau-cong-nghiep-pro.md", "placeholder": "/path/to/post.md"}]
            },
            {
                "id": "blog_preflight",
                "title": "Blog Preflight Contract Gate (5-gate runner)",
                "desc": "Chạy kiểm định nghiêm ngặt trước khi xuất bản bài blog",
                "cmd": "python3 /root/claude-blog/scripts/blog_preflight.py {file_path}",
                "type": "python",
                "args": [{"name": "file_path", "label": "Đường dẫn file Markdown", "default": "/root/ke-hoach-seo-dau-cong-nghiep-pro.md", "placeholder": "/path/to/post.md"}]
            },
            {
                "id": "blog_create",
                "title": "Khởi tạo bài viết mới chuẩn AI Search",
                "desc": "Sử dụng Claude Blog skill để viết bài chuẩn GEO/AEO theo chủ đề",
                "cmd": "claude -p '/blog:create {topic}'",
                "type": "cli",
                "args": [{"name": "topic", "label": "Chủ đề bài viết", "default": "", "placeholder": "Hướng dẫn chọn dầu nhớt thủy lực 68"}]
            },
            {
                "id": "blog_decay",
                "title": "Phát hiện suy giảm nội dung (Content Decay)",
                "desc": "Quét và phát hiện các bài viết bị giảm thứ hạng hoặc traffic",
                "cmd": "python3 /root/claude-blog/scripts/content_decay.py",
                "type": "python",
                "args": []
            }
        ]
    }
]
