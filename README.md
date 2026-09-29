# Python Warp Web Claude (`python_warp_web_claude`)

> **Claude Studio Hub (SEO & Blog Commander)** - Giao diện Web GUI hiện đại bọc (wrap) CLI Claude Code, tích hợp sâu bộ công cụ [Claude SEO](https://github.com/AgriciDaniel/claude-seo) và [Claude Blog](https://github.com/AgriciDaniel/claude-blog).

---

## 🌟 Tính Năng Nổi Bật

1. **⚡ Command Hub (1-Click Actions)**:
   - Các Preset định sẵn cho **Claude SEO**: Full Site Audit, Deep Page Analysis, Technical SEO Check, Content Brief chuẩn E-E-A-T, AI Search & GEO Optimization, Doctor setup check.
   - Các Preset cho **Claude Blog**: Đánh giá chất lượng (`analyze_blog.py`), 5-gate Preflight check (`blog_preflight.py`), khởi tạo bài viết chuẩn GEO/AEO, phát hiện suy giảm nội dung (`content_decay.py`).
   - Ô nhập lệnh tự do (chạy lệnh Claude CLI, Python hoặc Bash tùy ý).
   - Live Console stream output theo thời gian thực (SSE) kèm đồng hồ bấm giờ, badge trạng thái và nút dừng task.

2. **🖥️ Interactive Web Terminal (PTY Bridge)**:
   - Nhúng trình giả lập Terminal `xterm.js` kết nối qua WebSocket vào Pseudo-Terminal (`pty`) của Linux.
   - Tương thích 100% với giao diện tương tác dòng lệnh của `claude` CLI: giữ nguyên màu sắc ANSI 256, phím điều hướng mũi tên, thanh tiến trình spinner, xác nhận yes/no.
   - **Tự động sao chép (Auto-Copy on Select)** ngay khi bôi đen chuột và nút **`📋 Copy Text`** sao chép toàn bộ màn hình terminal vào Clipboard.

3. **📑 Trình Đọc Báo Cáo (Reports Explorer)**:
   - Tự động quét và lập danh mục toàn bộ file báo cáo Markdown (`.md`) và HTML trong các thư mục dự án.
   - Xem định dạng chuẩn Markdown (bảng biểu, heading, code block, callout) và nút chuyển đổi xem mã thô.

4. **📜 Quản Lý Log In/Out Đầy Đủ**:
   - Tự động lưu 100% câu lệnh, dữ liệu đầu vào và đầu ra vào các file `.log` kèm timestamp và metadata.
   - Hỗ trợ xem trực tiếp và tải file log về máy tính cá nhân.

5. **🛡️ Lớp Bảo Mật Mật Khẩu & Chống Brute-Force**:
   - Đăng nhập xác thực bằng mật khẩu quản trị (không cần username).
   - Cơ chế giới hạn: **Tối đa 10 lần thử trong 60 giây**. Tự động khóa và hiển thị đồng hồ đếm ngược nếu vượt quá số lần cho phép.
   - Phiên làm việc duy trì an toàn qua `HttpOnly Cookie`.

---

## 🏗️ Cấu Trúc Dự Án

```
python_warp_web_claude/
├── app/
│   ├── main.py             # FastAPI REST endpoints, SSE task streaming & WebSockets
│   ├── auth.py             # Module xác thực mật khẩu & Rate Limiter chống Brute-Force
│   ├── config.py           # Cấu hình danh mục dự án, presets, cổng mạng và mật khẩu
│   ├── task_runner.py      # Async Process Runner stream output qua SSE
│   ├── pty_manager.py      # Cầu nối PTY (Pseudo-Terminal) kết nối với xterm.js
│   ├── log_manager.py      # Quản lý đọc, tải và xóa file log In/Out
│   └── reports_manager.py  # Quét và hiển thị các file báo cáo Markdown/HTML
├── templates/
│   └── index.html          # Giao diện Single Page Application
├── static/
│   ├── styles.css          # Giao diện Cyber-Terracotta Dark Mode cao cấp
│   ├── app.js             # Logic Frontend, WebSocket & SSE streaming
│   └── lib/                # Thư viện offline: xterm.js, xterm-addon-fit, marked.js
├── nginx.conf              # Cấu hình Nginx Reverse Proxy (Port 80 & 443)
├── claude-web-gui.service  # File cấu hình Systemd tự động chạy ngầm
├── manage.sh               # Script quản lý dịch vụ (start/stop/restart/status/logs)
├── run.sh                  # Script khởi chạy uvicorn backend
└── requirements.txt        # Danh sách thư viện Python cần thiết
```

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Yêu cầu hệ thống
* Linux (Ubuntu 22.04+ khuyến nghị)
* Python 3.10+
* Nginx (cho port 80 & 443)

### 2. Cài đặt môi trường
```bash
git clone https://github.com/teamseohpvn/python_warp_web_claude.git
cd python_warp_web_claude

# Tạo virtual environment và cài đặt thư viện
python3 -m venv venv
venv/bin/pip install -r requirements.txt
chmod +x run.sh manage.sh
```

### 3. Cấu hình Systemd Service
```bash
# Copy file service vào systemd
cp claude-web-gui.service /etc/systemd/system/claude-web-gui.service

# Nạp cấu hình và khởi động
systemctl daemon-reload
systemctl enable claude-web-gui
systemctl start claude-web-gui
```

### 4. Cấu hình Nginx (HTTP & HTTPS)
```bash
# Cài đặt Nginx
apt-get install -y nginx

# Tạo chứng chỉ SSL tự ký cho HTTPS
mkdir -p /etc/ssl/claude-web-gui
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/claude-web-gui/server.key \
  -out /etc/ssl/claude-web-gui/server.crt \
  -subj "/C=VN/ST=Hanoi/L=Hanoi/O=ClaudeStudio/CN=localhost"

# Kích hoạt cấu hình Nginx
cp nginx.conf /etc/nginx/sites-available/claude-web-gui
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/claude-web-gui /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

---

## 🛠️ Lệnh Quản Trị Nhanh

Bạn có thể liên kết script `manage.sh` vào hệ thống để dùng lệnh `claude-hub`:
```bash
ln -sf $(pwd)/manage.sh /usr/local/bin/claude-hub

# Các lệnh khả dụng:
claude-hub start     # Khởi động dịch vụ
claude-hub restart   # Khởi động lại
claude-hub stop      # Dừng dịch vụ
claude-hub status    # Kiểm tra trạng thái hoạt động
claude-hub logs      # Theo dõi log thời gian thực
```

---

## 🔐 Đổi Mật Khẩu Quản Trị

Mật khẩu mặc định là: `claude2026`.

Để đổi mật khẩu, bạn có thể chỉnh sửa trong file `/etc/systemd/system/claude-web-gui.service`:
```ini
Environment=AUTH_PASSWORD=mat_khau_moi_cua_ban
```
Sau đó khởi động lại dịch vụ:
```bash
systemctl daemon-reload
systemctl restart claude-web-gui
```

---

## 📄 License
Phát hành theo giấy phép MIT.
