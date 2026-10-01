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
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "mylove2000")
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
    {"name": "Claude SEO Engine", "path": "/projects/claude-seo", "badge": "Core Tool"},
    {"name": "Claude Blog Engine", "path": "/projects/claude-blog", "badge": "Core Tool"},
    {"name": "Claude Ads Engine", "path": "/projects/claude-ads", "badge": "Core Tool"},
    {"name": "Keyword Pro Console", "path": "/projects/keywordpro", "badge": "Web App"},
    {"name": "Codex SEO Engine", "path": "/projects/codex-seo", "badge": "Core Tool"},
    {"name": "Root Workspace", "path": "/root", "badge": "General"},
]

# Quick presets for Claude SEO, Claude Blog, Claude Ads & Keyword Pro
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
                "cmd": "claude -p '/seo audit {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "https://example.com", "placeholder": "https://..."}]
            },
            {
                "id": "seo_page",
                "title": "Phân tích chuyên sâu 1 Trang (Deep Page Analysis)",
                "desc": "Kiểm tra chi tiết thẻ meta, cấu trúc heading, nội dung, schema của 1 URL",
                "cmd": "claude -p '/seo page {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Page URL", "default": "", "placeholder": "https://example.com/bai-viet"}]
            },
            {
                "id": "seo_content_brief",
                "title": "Tạo Content Brief chuẩn SEO & E-E-A-T",
                "desc": "Lập dàn ý nội dung bài viết chuyên sâu dựa trên từ khóa mục tiêu",
                "cmd": "claude -p '/seo content-brief \"{keyword}\"'",
                "type": "cli",
                "args": [{"name": "keyword", "label": "Từ khóa chính", "default": "", "placeholder": "dầu nhớt công nghiệp"}]
            },
            {
                "id": "seo_geo",
                "title": "AI Search & GEO Optimization",
                "desc": "Tối ưu hóa để được trích dẫn trên AI search (ChatGPT, Perplexity, Claude)",
                "cmd": "claude -p '/seo geo {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "URL hoặc Topic", "default": "", "placeholder": "https://example.com"}]
            },
            {
                "id": "seo_technical",
                "title": "Kiểm tra Technical SEO",
                "desc": "Đánh giá tốc độ, robots.txt, sitemap.xml, canonical, hreflang",
                "cmd": "claude -p '/seo technical {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "", "placeholder": "https://..."}]
            },
            {
                "id": "seo_dataforseo_serp",
                "title": "DataForSEO SERP Ranking",
                "desc": "Tra cứu kết quả xếp hạng thực tế từ DataForSEO API",
                "cmd": "claude -p '/seo dataforseo serp \"{keyword}\"'",
                "type": "cli",
                "args": [{"name": "keyword", "label": "Từ khóa tra cứu", "default": "", "placeholder": "dầu thủy lực 68"}]
            },
            {
                "id": "seo_firecrawl_crawl",
                "title": "Firecrawl Deep Site Crawl",
                "desc": "Thu thập toàn trang và chuyển thành Markdown cho AI xử lý",
                "cmd": "claude -p '/seo firecrawl crawl {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "", "placeholder": "https://example.com"}]
            },
            {
                "id": "seo_unlighthouse",
                "title": "Unlighthouse Full-Site Scan (Local)",
                "desc": "Quét toàn bộ website chấm điểm Lighthouse (hoàn toàn miễn phí, không cần key)",
                "cmd": "claude -p '/seo unlighthouse {url}'",
                "type": "cli",
                "args": [{"name": "url", "label": "Website URL", "default": "", "placeholder": "https://example.com"}]
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
                "cmd": "python3 /projects/claude-blog/scripts/analyze_blog.py {file_path}",
                "type": "python",
                "args": [{"name": "file_path", "label": "Đường dẫn file Markdown", "default": "/root/ke-hoach-seo-dau-cong-nghiep-pro.md", "placeholder": "/path/to/post.md"}]
            },
            {
                "id": "blog_preflight",
                "title": "Blog Preflight Contract Gate (5-gate runner)",
                "desc": "Chạy kiểm định nghiêm ngặt trước khi xuất bản bài blog",
                "cmd": "python3 /projects/claude-blog/scripts/blog_preflight.py {file_path}",
                "type": "python",
                "args": [{"name": "file_path", "label": "Đường dẫn file Markdown", "default": "/root/ke-hoach-seo-dau-cong-nghiep-pro.md", "placeholder": "/path/to/post.md"}]
            },
            {
                "id": "blog_create",
                "title": "Khởi tạo bài viết mới chuẩn AI Search",
                "desc": "Sử dụng Claude Blog skill để viết bài chuẩn GEO/AEO theo chủ đề",
                "cmd": "claude -p '/blog write \"{topic}\"'",
                "type": "cli",
                "args": [{"name": "topic", "label": "Chủ đề bài viết", "default": "", "placeholder": "Hướng dẫn chọn dầu nhớt thủy lực 68"}]
            },
            {
                "id": "blog_brief",
                "title": "Tạo Content Brief chi tiết",
                "desc": "Xây dựng bản brief bài viết blog với từ khóa LSI và cấu trúc đề xuất",
                "cmd": "claude -p '/blog brief \"{topic}\"'",
                "type": "cli",
                "args": [{"name": "topic", "label": "Chủ đề", "default": "", "placeholder": "Quy trình bảo dưỡng động cơ diesel"}]
            },
            {
                "id": "blog_cluster",
                "title": "Topic Cluster Plan (Cụm chủ đề)",
                "desc": "Lập kế hoạch cụm bài viết gồm bài Pillar và các bài vệ tinh hỗ trợ",
                "cmd": "claude -p '/blog cluster plan \"{seed}\"'",
                "type": "cli",
                "args": [{"name": "seed", "label": "Chủ đề gốc", "default": "", "placeholder": "Dầu nhớt công nghiệp"}]
            },
            {
                "id": "blog_decay",
                "title": "Phát hiện suy giảm nội dung (Content Decay)",
                "desc": "Quét và phát hiện các bài viết bị giảm thứ hạng hoặc traffic",
                "cmd": "python3 /projects/claude-blog/scripts/content_decay.py",
                "type": "python",
                "args": []
            }
        ]
    },
    {
        "category": "Claude Ads",
        "items": [
            {
                "id": "ads_setup",
                "title": "Thiết lập Hồ Sơ & Guardrails Ads (/ads setup)",
                "desc": "Cấu hình tài khoản, chỉ số KPI mục tiêu, giới hạn ngân sách và an toàn",
                "cmd": "claude -p '/ads setup'",
                "type": "cli",
                "args": []
            },
            {
                "id": "ads_audit",
                "title": "Audit Tài Khoản Quảng Cáo (/ads audit)",
                "desc": "Đánh giá toàn diện chiến dịch, phát hiện lãng phí ngân sách và lỗi tracking",
                "cmd": "claude -p '/ads audit'",
                "type": "cli",
                "args": []
            },
            {
                "id": "ads_plan",
                "title": "Lập Kế Hoạch Chiến Dịch Theo Ngành (/ads plan)",
                "desc": "Xây dựng chiến lược quảng cáo chuyên biệt (b2b, ecommerce, saas, leadgen)",
                "cmd": "claude -p '/ads plan {industry}'",
                "type": "cli",
                "args": [{"name": "industry", "label": "Ngành hàng (b2b/ecommerce/saas/leadgen)", "default": "b2b", "placeholder": "b2b"}]
            },
            {
                "id": "ads_google",
                "title": "Tối Ưu Hóa Google Ads (/ads google)",
                "desc": "Vận hành chiến dịch Google Search, PMax, Display và YouTube Ads",
                "cmd": "claude -p '/ads google'",
                "type": "cli",
                "args": []
            },
            {
                "id": "ads_budget",
                "title": "Phân Bổ Ngân Sách Đa Kênh (/ads budget)",
                "desc": "Tối ưu hóa ngân sách theo mục tiêu CPA và tối đa hóa lợi nhuận ROAS",
                "cmd": "claude -p '/ads budget'",
                "type": "cli",
                "args": []
            },
            {
                "id": "ads_creative",
                "title": "Ma Trận Sáng Tạo & Thông Điệp (/ads creative)",
                "desc": "Xây dựng thông điệp, tiêu đề và biến thể hình ảnh/nội dung thử nghiệm A/B",
                "cmd": "claude -p '/ads creative'",
                "type": "cli",
                "args": []
            }
        ]
    },
    {
        "category": "Keyword Pro",
        "items": [
            {
                "id": "kwp_status",
                "title": "Kiểm Tra Trạng Thái Dịch Vụ Keyword Pro",
                "desc": "Kiểm tra kết nối cơ sở dữ liệu PostgreSQL và Redis cache của ứng dụng",
                "cmd": "curl -s http://localhost:3002/api/health",
                "type": "bash",
                "args": []
            },
            {
                "cmd": "cd /projects/keywordpro && pnpm start",
                "id": "kwp_start",
                "title": "Khởi Chạy Keyword Pro Console (Cổng 3002)",
                "desc": "Chạy máy chủ Keyword Pro Next.js Web Console tại http://localhost:3002/keyword-pro",
                "type": "bash",
                "args": []
            },
            {
                "id": "kwp_migrate",
                "title": "Database Schema Migration",
                "desc": "Áp dụng và nâng cấp các migration cấu trúc cơ sở dữ liệu PostgreSQL",
                "cmd": "cd /projects/keywordpro && pnpm --ignore-workspace db:migrate",
                "type": "bash",
                "args": []
            },
            {
                "id": "kwp_seed",
                "title": "Seed Dữ Liệu Quản Trị Cục Bộ",
                "desc": "Nạp tài khoản người dùng cục bộ mặc định (local-user)",
                "cmd": "cd /projects/keywordpro && pnpm --ignore-workspace seed",
                "type": "bash",
                "args": []
            }
        ]
    }
]

# Comprehensive Tool Guides Data for the Right Sidebar (25% width)
GUIDES = {
    "seo": {
        "id": "seo",
        "name": "Claude SEO",
        "icon": "🔍",
        "badge": "26 Skills + 19 Agents",
        "summary": "Universal SEO skill suite cho Claude Code. Tra soát toàn diện Technical SEO, E-E-A-T, Schema JSON-LD, GEO/AEO, Core Web Vitals, DataForSEO và Firecrawl.",
        "commands": [
            {
                "cmd": "/seo audit <url>",
                "desc": "Audit tra soát toàn diện website: phân tích song song kỹ thuật, nội dung, schema, mobile và đề xuất lộ trình hành động ưu tiên.",
                "category": "Audit & Chiến lược",
                "example": "/seo audit https://example.com"
            },
            {
                "cmd": "/seo page <url>",
                "desc": "Phân tích chuyên sâu 1 trang cụ thể: thẻ title, meta description, cấu trúc heading H1-H6, mật độ nội dung, hình ảnh và schema.",
                "category": "On-Page SEO",
                "example": "/seo page https://example.com/bai-viet"
            },
            {
                "cmd": "/seo technical <url>",
                "desc": "Kiểm tra toàn bộ lỗi kỹ thuật SEO: mã phản hồi HTTP, tệp robots.txt, sơ đồ sitemap.xml, thẻ canonical, chuyển hướng redirect và hreflang.",
                "category": "Technical SEO",
                "example": "/seo technical https://example.com"
            },
            {
                "cmd": "/seo schema <url>",
                "desc": "Phát hiện, kiểm tra hợp lệ (validate) và tự động sinh mã JSON-LD Schema markup chuẩn Google Rich Results.",
                "category": "Schema Markup",
                "example": "/seo schema https://example.com"
            },
            {
                "cmd": "/seo geo <url>",
                "desc": "Tối ưu hóa tìm kiếm thế hệ mới GEO/AEO: tăng khả năng được trích dẫn nội dung trên các mô hình AI (ChatGPT, Claude, Perplexity).",
                "category": "AI Search (GEO/AEO)",
                "example": "/seo geo https://example.com"
            },
            {
                "cmd": "/seo cwv <url>",
                "desc": "Đo lường và đánh giá chỉ số trải nghiệm trang Core Web Vitals của Google: LCP (tải trang), CLS (ổn định thị giác), INP (độ nhạy tương tác).",
                "category": "Hiệu năng trang",
                "example": "/seo cwv https://example.com"
            },
            {
                "cmd": "/seo content-brief \"<từ khóa>\"",
                "desc": "Tạo bản tóm tắt nội dung (Content Brief) chi tiết, định hướng góc nhìn độc đáo chuẩn E-E-A-T dựa trên phân tích SERP thực tế.",
                "category": "Nội dung & E-E-A-T",
                "example": "/seo content-brief \"dầu nhớt công nghiệp\""
            },
            {
                "cmd": "/seo doctor",
                "desc": "Kiểm tra chẩn đoán sức khỏe hệ thống: kiểm tra môi trường Python venv, Chromium Playwright, cấu hình MCP và API keys.",
                "category": "Chẩn đoán & Cấu hình",
                "example": "/seo doctor"
            },
            {
                "cmd": "/seo dataforseo serp \"<từ khóa>\"",
                "desc": "Tra cứu dữ liệu xếp hạng SERP thời gian thực từ DataForSEO API (vị trí top 100, URL xếp hạng, đoạn trích nổi bật).",
                "category": "DataForSEO Plugin",
                "example": "/seo dataforseo serp \"thi công bê tông mài\""
            },
            {
                "cmd": "/seo dataforseo keywords \"<từ khóa hạt giống>\"",
                "desc": "Nghiên cứu danh sách từ khóa hạt giống và mở rộng, phân tích lượng tìm kiếm trung bình (Search Volume) và mức độ cạnh tranh (CPC/KD).",
                "category": "DataForSEO Plugin",
                "example": "/seo dataforseo keywords \"bê tông tươi\""
            },
            {
                "cmd": "/seo dataforseo competitors <domain>",
                "desc": "Phân tích đối thủ cạnh tranh trực tiếp trên bảng xếp hạng Google theo từng thị trường mục tiêu.",
                "category": "DataForSEO Plugin",
                "example": "/seo dataforseo competitors example.com"
            },
            {
                "cmd": "/seo dataforseo backlinks <domain>",
                "desc": "Phân tích hồ sơ liên kết ngược (Backlink profile, Referring domains, Anchor text distribution) của tên miền.",
                "category": "DataForSEO Plugin",
                "example": "/seo dataforseo backlinks example.com"
            },
            {
                "cmd": "/seo firecrawl crawl <url>",
                "desc": "Crawl thu thập toàn bộ các trang trên website bằng Firecrawl, tự động chuyển đổi sang Markdown sạch cho AI phân tích.",
                "category": "Crawl & Scrape",
                "example": "/seo firecrawl crawl https://example.com"
            },
            {
                "cmd": "/seo firecrawl map <url>",
                "desc": "Lập bản đồ toàn bộ URL của website, phát hiện trang mồ côi (orphan pages) và cấu trúc liên kết nội bộ.",
                "category": "Crawl & Scrape",
                "example": "/seo firecrawl map https://example.com"
            },
            {
                "cmd": "/seo firecrawl scrape <url>",
                "desc": "Bóc tách nội dung chi tiết bài viết, loại bỏ rác giao diện, trả về dữ liệu định dạng Markdown chuẩn.",
                "category": "Crawl & Scrape",
                "example": "/seo firecrawl scrape https://example.com/bai-viet"
            },
            {
                "cmd": "/seo unlighthouse <url>",
                "desc": "Thu thập và quét toàn bộ website cục bộ bằng Lighthouse Engine, chấm điểm hiệu năng, SEO, trợ năng (100% miễn phí, không cần API key).",
                "category": "Local Crawler",
                "example": "/seo unlighthouse https://example.com"
            }
        ]
    },
    "blog": {
        "id": "blog",
        "name": "Claude Blog",
        "icon": "📝",
        "badge": "31 Sub-skills + 5 Agents",
        "summary": "Hệ thống viết bài, tối ưu hóa và xuất bản blog quy mô lớn với quy trình kiểm duyệt 5-gate contract nghiêm ngặt và AI Citation readiness.",
        "commands": [
            {
                "cmd": "/blog write \"<chủ đề>\"",
                "desc": "Viết bài blog chuẩn chuyên gia từ đầu: cấu trúc heading tối ưu, chèn câu hỏi thường gặp FAQ, trích dẫn số liệu và chuẩn bị cho AI trích dẫn.",
                "category": "Viết & Tối ưu bài",
                "example": "/blog write \"Hướng dẫn lựa chọn dầu thủy lực ISO VG 68\""
            },
            {
                "cmd": "/blog rewrite <đường dẫn file.md>",
                "desc": "Tối ưu hóa và viết lại bài viết hiện có để vượt qua hợp đồng đánh giá chất lượng 90+ điểm.",
                "category": "Viết & Tối ưu bài",
                "example": "/blog rewrite /root/bai-viet.md"
            },
            {
                "cmd": "/blog analyze <file hoặc url>",
                "desc": "Kiểm định bài viết trên thang 100 điểm với 5 tiêu chí khắt khe: E-E-A-T, cấu trúc heading, độ dễ đọc (Readability), SEO checklist.",
                "category": "Kiểm định chất lượng",
                "example": "/blog analyze /root/bai-viet.md"
            },
            {
                "cmd": "/blog brief \"<chủ đề>\"",
                "desc": "Tạo bản tóm tắt nội dung (Content Brief) chi tiết: từ khóa chính, từ khóa phụ LSI, cấu trúc bài viết, đối tượng mục tiêu.",
                "category": "Chiến lược nội dung",
                "example": "/blog brief \"Quy trình đổ bê tông sàn nhà xưởng\""
            },
            {
                "cmd": "/blog outline \"<chủ đề>\"",
                "desc": "Xây dựng dàn ý bài viết chi tiết dựa trên phân tích ý định tìm kiếm (Search Intent) và đối thủ trên SERP.",
                "category": "Chiến lược nội dung",
                "example": "/blog outline \"Bảo dưỡng dầu nhớt động cơ diesel\""
            },
            {
                "cmd": "/blog strategy \"<ngách thị trường>\"",
                "desc": "Lập chiến lược phát triển blog tổng thể: nghiên cứu cụm chủ đề, lộ trình xuất bản và định vị thương hiệu.",
                "category": "Chiến lược nội dung",
                "example": "/blog strategy \"dầu nhớt công nghiệp nặng\""
            },
            {
                "cmd": "/blog calendar",
                "desc": "Lên lịch biên tập xuất bản nội dung blog tự động theo tuần, tháng hoặc quý.",
                "category": "Lập kế hoạch",
                "example": "/blog calendar"
            },
            {
                "cmd": "/blog seo-check <đường dẫn file.md>",
                "desc": "Rà soát toàn diện danh sách kiểm tra SEO on-page của bài viết trước khi xuất bản lên CMS.",
                "category": "Kiểm định chất lượng",
                "example": "/blog seo-check /root/bai-viet.md"
            },
            {
                "cmd": "/blog schema <đường dẫn file.md>",
                "desc": "Tự động sinh mã cấu trúc JSON-LD phù hợp: Article, BlogPosting, FAQPage, HowTo cho bài viết.",
                "category": "Schema Markup",
                "example": "/blog schema /root/bai-viet.md"
            },
            {
                "cmd": "/blog geo <đường dẫn file.md>",
                "desc": "Đo lường chỉ số sẵn sàng được trích dẫn trên AI Search (AI Citation Readiness Heuristics).",
                "category": "AI Citation",
                "example": "/blog geo /root/bai-viet.md"
            },
            {
                "cmd": "/blog cannibalization <thư mục bài viết>",
                "desc": "Quét toàn bộ bài viết trong thư mục để phát hiện hiện tượng ăn thịt/xung đột từ khóa giữa các bài viết.",
                "category": "Audit nội dung",
                "example": "/blog cannibalization /root/posts"
            },
            {
                "cmd": "/blog factcheck <đường dẫn file.md>",
                "desc": "Xác minh các số liệu thống kê, dữ liệu kỹ thuật trong bài viết đối chiếu với các nguồn uy tín.",
                "category": "Kiểm định chất lượng",
                "example": "/blog factcheck /root/bai-viet.md"
            },
            {
                "cmd": "/blog cluster plan \"<chủ đề gốc>\"",
                "desc": "Lập kế hoạch cụm bài viết Topic Cluster: xác định bài viết trụ cột (Pillar Page) và các bài viết vệ tinh bao quanh.",
                "category": "Cụm chủ đề (Cluster)",
                "example": "/blog cluster plan \"Dầu truyền nhiệt công nghiệp\""
            },
            {
                "cmd": "/blog multilingual \"<chủ đề>\" --languages vi,en,ja",
                "desc": "Tạo bài viết gốc và tự động dịch, bản địa hóa sang nhiều ngôn ngữ khác nhau kèm thẻ liên kết hreflang.",
                "category": "Đa ngôn ngữ",
                "example": "/blog multilingual \"Giới thiệu mác bê tông\" --languages vi,en"
            },
            {
                "cmd": "/blog decay <current_gsc.csv> <previous_gsc.csv>",
                "desc": "Phát hiện các bài viết bị suy giảm lưu lượng (Content Decay giảm 20%+ QoQ) từ báo cáo Google Search Console.",
                "category": "Analytics & Suy giảm",
                "example": "/blog decay /root/gsc-t9.csv /root/gsc-t8.csv"
            },
            {
                "cmd": "/blog discourse \"<chủ đề>\"",
                "desc": "Nghiên cứu thảo luận thực tế của cộng đồng và khách hàng về chủ đề trong 30 ngày qua (không cần API key).",
                "category": "Nghiên cứu cộng đồng",
                "example": "/blog discourse \"tiêu chuẩn độ nhớt thủy lực\""
            }
        ]
    },
    "ads": {
        "id": "ads",
        "name": "Claude Ads",
        "icon": "📢",
        "badge": "12 Platforms + 25 Agents",
        "summary": "Bộ công cụ tự động hóa và tối ưu chiến dịch quảng cáo đa nền tảng (Google, Meta, LinkedIn), phân bổ ngân sách và ma trận sáng tạo.",
        "commands": [
            {
                "cmd": "/ads setup",
                "desc": "Khởi tạo hồ sơ khách hàng, danh mục tài khoản, mục tiêu chiến dịch (KPIs), cấu hình quyền riêng tư và hạn mức an toàn.",
                "category": "Khởi tạo & An toàn",
                "example": "/ads setup"
            },
            {
                "cmd": "/ads audit",
                "desc": "Audit rà soát toàn diện tài khoản quảng cáo: phát hiện điểm rò rỉ ngân sách, từ khóa phủ định thiếu sót và đối tượng trùng lặp.",
                "category": "Audit & Đánh giá",
                "example": "/ads audit"
            },
            {
                "cmd": "/ads plan <industry>",
                "desc": "Lập kế hoạch chiến dịch quảng cáo bài bản theo từng ngành hàng: `saas`, `ecommerce`, `b2b`, `leadgen`, `local`.",
                "category": "Chiến lược quảng cáo",
                "example": "/ads plan b2b"
            },
            {
                "cmd": "/ads google",
                "desc": "Quản lý và tối ưu chiến dịch Google Ads: Google Search, Performance Max (PMax), Display và YouTube Video Ads.",
                "category": "Kênh Google Ads",
                "example": "/ads google"
            },
            {
                "cmd": "/ads meta",
                "desc": "Tối ưu hóa chiến dịch Meta Ads: cấu hình nhóm quảng cáo Facebook, Instagram Feed, Reels và Advantage+ Shopping.",
                "category": "Kênh Meta Ads",
                "example": "/ads meta"
            },
            {
                "cmd": "/ads linkedin",
                "desc": "Thiết lập và vận hành chiến dịch B2B LinkedIn Ads: Sponsored Content, Lead Gen Forms và tiếp cận doanh nghiệp theo tệp (ABM).",
                "category": "Kênh LinkedIn Ads",
                "example": "/ads linkedin"
            },
            {
                "cmd": "/ads budget",
                "desc": "Phân tích và tối ưu hóa phân bổ ngân sách đa kênh nhằm đạt chỉ số hoàn vốn ROAS cao nhất hoặc CPA mục tiêu thấp nhất.",
                "category": "Ngân sách & Giá thầu",
                "example": "/ads budget"
            },
            {
                "cmd": "/ads creative",
                "desc": "Xây dựng ma trận nội dung quảng cáo: thông điệp thu hút (Hook), lợi ích cốt lõi (Value Proposition), lời kêu gọi hành động (CTA).",
                "category": "Ma trận sáng tạo",
                "example": "/ads creative"
            },
            {
                "cmd": "/ads experiment",
                "desc": "Thiết kế và theo dõi thử nghiệm phân tách A/B testing khoa học: kiểm định mẫu quảng cáo, trang đích và tệp đối tượng.",
                "category": "Thử nghiệm A/B",
                "example": "/ads experiment"
            },
            {
                "cmd": "/ads tracking",
                "desc": "Kiểm tra luồng đo lường chuyển đổi: rà soát thẻ Meta Pixel, Conversions API (CAPI), Google Tag Manager và GA4 Events.",
                "category": "Đo lường & Tracking",
                "example": "/ads tracking"
            },
            {
                "cmd": "/ads monitor",
                "desc": "Thiết lập hệ thống giám sát tự động: cảnh báo khi chi phí tăng đột biến, tần suất quảng cáo quá cao hoặc suy giảm chuyển đổi.",
                "category": "Giám sát & Cảnh báo",
                "example": "/ads monitor"
            },
            {
                "cmd": "/ads report",
                "desc": "Tổng hợp và xuất báo cáo hiệu suất chiến dịch quảng cáo định dạng Markdown hoặc PDF gửi cho khách hàng/sếp.",
                "category": "Báo cáo hiệu quả",
                "example": "/ads report"
            }
        ]
    },
    "keyword": {
        "id": "keyword",
        "name": "Keyword Pro",
        "icon": "🔑",
        "badge": "94 Markets + 46 Languages",
        "summary": "Bàn làm việc nghiên cứu từ khóa chuyên sâu cục bộ kết nối DataForSEO API, hỗ trợ 94 thị trường, 46 ngôn ngữ, PostgreSQL và Redis.",
        "commands": [
            {
                "cmd": "cd /projects/keywordpro && pnpm start",
                "desc": "Khởi động ứng dụng Keyword Pro Console ở chế độ Production tại cổng 3002 (truy cập `http://localhost:3002/keyword-pro`).",
                "category": "Máy chủ ứng dụng",
                "example": "cd /projects/keywordpro && pnpm start"
            },
            {
                "cmd": "cd /projects/keywordpro && pnpm dev",
                "desc": "Khởi động Keyword Pro Console ở chế độ Development (môi trường phát triển cục bộ có hot-reload).",
                "category": "Máy chủ ứng dụng",
                "example": "cd /projects/keywordpro && pnpm dev"
            },
            {
                "cmd": "curl -s http://localhost:3002/api/health",
                "desc": "Kiểm tra trạng thái kết nối máy chủ, kiểm tra độ sẵn sàng của PostgreSQL và Redis cache.",
                "category": "API & Sức khỏe",
                "example": "curl -s http://localhost:3002/api/health"
            },
            {
                "cmd": "pnpm --ignore-workspace db:migrate",
                "desc": "Chạy migration cập nhật cấu trúc bảng dữ liệu (schema) trong PostgreSQL `keyword_pro` an toàn.",
                "category": "Cơ sở dữ liệu",
                "example": "cd /projects/keywordpro && pnpm --ignore-workspace db:migrate"
            },
            {
                "cmd": "pnpm --ignore-workspace seed",
                "desc": "Khởi tạo dữ liệu người dùng cục bộ mặc định (`local-user`) vào cơ sở dữ liệu.",
                "category": "Cơ sở dữ liệu",
                "example": "cd /projects/keywordpro && pnpm --ignore-workspace seed"
            },
            {
                "cmd": "Mở URL: /keyword-pro",
                "desc": "Giao diện bàn làm việc: tìm kiếm từ khóa, biểu đồ xu hướng nhu cầu tìm kiếm, phân tích độ khó và cơ hội tăng trưởng.",
                "category": "Trang Web Console",
                "example": "http://localhost:3002/keyword-pro"
            },
            {
                "cmd": "Mở URL: /settings/connections",
                "desc": "Cài đặt kết nối tài khoản DataForSEO (thông tin đăng nhập được mã hóa AES-256-GCM an toàn trong database).",
                "category": "Trang Web Console",
                "example": "http://localhost:3002/settings/connections"
            },
            {
                "cmd": "POST /api/v1/research/run",
                "desc": "Endpoint REST API trực tiếp thực thi 1 lệnh truy vấn DataForSEO cho từ khóa (Search volume, CPC, Intent, Competition).",
                "category": "REST API",
                "example": "POST /api/v1/research/run"
            },
            {
                "cmd": "POST /api/v1/research/module/run",
                "desc": "Endpoint REST API chạy tổ hợp báo cáo từ khóa chuyên sâu (SERP overview, PAA câu hỏi thường gặp, từ khóa liên quan).",
                "category": "REST API",
                "example": "POST /api/v1/research/module/run"
            },
            {
                "cmd": "pnpm --ignore-workspace legacy:inventory",
                "desc": "Kiểm tra và thống kê danh mục dữ liệu các phiên nghiên cứu từ khóa đã được lưu trữ trong cơ sở dữ liệu.",
                "category": "Bảo trì & Backup",
                "example": "cd /projects/keywordpro && pnpm --ignore-workspace legacy:inventory"
            }
        ]
    }
}

