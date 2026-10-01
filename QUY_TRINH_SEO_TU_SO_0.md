# QUY TRÌNH TRIỂN KHAI SEO TOÀN DIỆN CHO WEBSITE MỚI TỪ CON SỐ 0
> **Áp dụng cho:** Website mới chỉ có thông tin ngành nghề và sản phẩm  
> **Bộ công cụ tích hợp:** `claude-seo` (Kiến trúc & Kỹ thuật) + `claude-blog` (Xưởng nội dung) + `Keyword Pro` (Khảo sát từ khóa)

---

## 1. TỔNG QUAN PHÂN VAI HỆ THỐNG

Khi bắt đầu từ con số 0, **không thể chỉ dùng một công cụ đơn lẻ**. Hai công cụ đóng vai trò bổ trợ chặt chẽ theo hai giai đoạn chiến lược:

```
[Ngành nghề & Sản phẩm]
           │
           ▼
┌──────────────────────────────────────────────┐
│  GIAI ĐOẠN 1: CHIẾN LƯỢC & KIẾN TRÚC SITE     │
│  Công cụ: claude-seo + Keyword Pro           │
│  - Phân tích từ khóa, Search Intent          │
│  - Gom cụm từ khóa (Semantic Clustering)     │
│  - Xây dựng cấu trúc Silo (Pillar / Cluster)  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  GIAI ĐOẠN 2: CHIẾN LƯỢC NỘI DUNG & SẢN XUẤT  │
│  Công cụ: claude-blog                        │
│  - Định hình thương hiệu (BRAND/VOICE)       │
│  - Lập bản đồ Hub & Spoke & Lịch đăng bài    │
│  - Viết bài chuẩn 5-Gate Contract (Điểm ≥ 90)│
│  - Tối ưu AI Citations & Schema tự động      │
└──────────────────────────────────────────────┘
```

| Tiêu chí | `claude-seo` (Tổng công trình sư) | `claude-blog` (Xưởng sản xuất nội dung) |
|---|---|---|
| **Vai trò cốt lõi** | Thiết kế bản vẽ kiến trúc, cấu trúc Silo, Audit kỹ thuật, Schema cấp website | Nghiên cứu chủ đề bài viết, viết bài chuẩn SEO, tối ưu AI Citation (GEO) |
| **Giai đoạn áp dụng** | **Bước 1 & Bước 2** (Khởi động, định hình nền tảng) | **Bước 3 & Bước 4** (Sản xuất, phủ nội dung, cập nhật) |
| **Đầu ra (Deliverables)** | Bản kế hoạch SEO, cấu trúc URL, cụm từ khóa, Sitemap, Robots.txt | Các bài viết hoàn chỉnh (Markdown/HTML), điểm kiểm duyệt ≥ 90, JSON-LD Schema |

---

## 2. QUY TRÌNH 4 BƯỚC TRIỂN KHAI CHI TIẾT

### BƯỚC 1: Khảo sát từ khóa & Phân nhóm ý định tìm kiếm (Search Intent)
*Mục đích: Xác định đâu là từ khóa để bán hàng (Sản phẩm) và đâu là từ khóa để kéo traffic (Bài viết/Blog).*

1. **Khảo sát từ khóa gốc (Seed Keywords) trên Keyword Pro:**
   - Mở giao diện **Keyword Pro** (trên cổng Hub hoặc cổng port tương ứng).
   - Nhập từ khóa gốc của ngành (Ví dụ: `dầu thủy lực`, `bê tông tươi`, `máy nén khí`).
   - Lọc ra 3 nhóm từ khóa:
     - **Commercial / Transactional (Giao dịch/Bán hàng):** Mua, báo giá, địa chỉ bán, phân phối $\rightarrow$ Đưa vào trang Danh mục & Sản phẩm.
     - **Informational (Thông tin/Thắc mắc):** Là gì, cách sử dụng, so sánh, lỗi thường gặp $\rightarrow$ Đưa vào cụm Blog.
     - **People Also Ask & Related Searches:** Các câu hỏi thực tế từ người dùng.

2. **Gom cụm ngữ nghĩa bằng `claude-seo`:**
   Chạy lệnh gom cụm tự động trên terminal:
   ```bash
   claude -p "/seo cluster <từ_khóa_chính_của_ngành>"
   ```
   *Ví dụ:*
   ```bash
   claude -p "/seo cluster 'dầu máy may công nghiệp'"
   ```
   *Kết quả trả về:* Danh sách các cụm từ khóa (Semantic Clusters) đã được nhóm theo ngữ nghĩa, tránh tình trạng viết bài trùng lặp (cannibalization).

---

### BƯỚC 2: Thiết kế kiến trúc website & Lập kế hoạch SEO (Silo Architecture)
*Mục đích: Thiết lập cấu trúc website chuẩn SEO ngay trước khi bắt tay vào làm web.*

1. **Khởi tạo kế hoạch SEO theo mô hình kinh doanh:**
   ```bash
   # Nếu là trang bán hàng, thương mại điện tử, sản phẩm:
   claude -p "/seo plan ecommerce"

   # Nếu là doanh nghiệp dịch vụ tại địa phương:
   claude -p "/seo plan local"

   # Hoặc nếu là phần mềm / giải pháp B2B:
   claude -p "/seo plan saas"
   ```

2. **Các hạng mục cần chốt từ Bước 2:**
   - **Cấu trúc URL chuẩn:**
     - Trang Pillar (Danh mục chính): `/danh-muc-san-pham/`
     - Trang Spoke (Sản phẩm chi tiết): `/san-pham/ten-san-pham/`
     - Trang Pillar Blog (Cụm kiến thức): `/kien-thuc/ten-chu-de/`
     - Trang Spoke Blog (Bài viết chi tiết): `/kien-thuc/ten-chu-de/bai-viet/`
   - **Internal Linking Framework:** Quy tắc bài blog dẫn link nội bộ về trang sản phẩm liên quan (Anchor text chính xác & bổ trợ).
   - **Schema Blueprint:** Khung dữ liệu có cấu trúc cho `Organization`, `Product`, `BreadcrumbList`, `FAQPage`.

---

### BƯỚC 3: Định hình thương hiệu & Lên lịch biên tập (Content Strategy)
*Mục đích: Lên toàn bộ chiến lược bài viết và chuẩn hóa tông giọng trước khi viết.*

1. **Thiết lập hồ sơ thương hiệu (`BRAND.md` & `VOICE.md`):**
   ```bash
   claude -p "/blog brand init"
   ```
   - Điền thông tin ngành nghề, sản phẩm nổi bật, lợi thế cạnh tranh (USP), đối tượng khách hàng mục tiêu (B2B/B2C).
   - Tất cả các bài viết sau đó sẽ tự động kế thừa giọng văn chuyên gia này.

2. **Bóc tách chiến lược nội dung cho ngách (Topic Ideation):**
   ```bash
   claude -p "/blog strategy <tên_ngành_hoặc_ngách_sản_phẩm>"
   ```
   *Ví dụ:*
   ```bash
   claude -p "/blog strategy 'dầu nhớt bôi trơn cho nhà máy dệt may'"
   ```
   *Kết quả:* Hệ thống tự động chia các chủ đề theo ma trận:
   - Bài hướng dẫn chọn mua (Buyer's Guide)
   - Bài giải quyết sự cố kỹ thuật (Troubleshooting)
   - Bài so sánh thông số/thương hiệu (Comparison)
   - Bài dự toán chi phí, bảng giá (Cost & Pricing)

3. **Lập sơ đồ cụm chủ đề Hub & Spoke:**
   ```bash
   claude -p "/blog cluster plan <chủ_đề_cốt_lõi>"
   ```
   *Ví dụ: `/blog cluster plan "cách bảo dưỡng hệ thống thủy lực"`*

4. **Lập lịch biên tập 30 - 60 ngày đầu tiên:**
   ```bash
   claude -p "/blog calendar monthly"
   ```
   Hệ thống sẽ xếp lịch ưu tiên: viết bài Pillar trước, sau đó viết các bài Spoke xoay quanh.

---

### BƯỚC 4: Sản xuất & Tối ưu bài viết chuẩn 5-Gate Delivery Contract
*Mục đích: Viết các bài viết có chiều sâu, điểm số chuyên môn cao và tối ưu cho cả Google lẫn AI Search (ChatGPT, Gemini, Perplexity).*

1. **Tạo Content Brief chi tiết cho từng bài:**
   ```bash
   claude -p "/blog brief <tiêu_đề_hoặc_từ_khóa>"
   ```
   Brief xác định rõ: Mục tiêu tìm kiếm, cấu trúc H1/H2/H3, nguồn tham chiếu kỹ thuật, anchor text dẫn về trang sản phẩm.

2. **Viết bài tự động với cơ chế kiểm duyệt 5 tầng (5-Gate Contract):**
   ```bash
   claude -p "/blog write <tên_chủ_đề_từ_brief>"
   ```
   *Đặc điểm quy trình 5-Gate:*
   - Tự động chấm điểm trên thang điểm 100 theo tiêu chuẩn hữu ích của Google (Helpful Content) và E-E-A-T.
   - Nếu bài viết dưới **90 điểm**, hệ thống tự động lặp lại quy trình viết/sửa tối đa 3 lần cho đến khi đạt chuẩn.
   - Tự động nhúng Schema JSON-LD (`Article`, `HowTo`, `FAQPage`).
   - Tối ưu khả năng trích dẫn AI (`llms.txt`, bảng biểu dữ liệu, số liệu chứng minh).

3. **Kiểm tra và nghiệm thu trước khi đăng tải:**
   ```bash
   claude -p "/blog seo-check <đường_dẫn_file_bài_viết.md>"
   claude -p "/blog geo <đường_dẫn_file_bài_viết.md>"  # Kiểm tra độ sẵn sàng cho AI Search
   ```

---

## 3. CHECKLIST TÓM TẮT THỰC THI (QUICK RUN)

| Tuần | Hạng mục | Công cụ chính | Lệnh thực thi chính |
|---|---|---|---|
| **Tuần 1** | Khảo sát từ khóa & Lập sơ đồ Silo | `Keyword Pro` + `claude-seo` | `/seo cluster <keyword>`<br>`/seo plan ecommerce` |
| **Tuần 2** | Định hình thương hiệu & Lên khung cụm nội dung | `claude-blog` | `/blog brand init`<br>`/blog strategy <niche>`<br>`/blog cluster plan <seed>` |
| **Tuần 3** | Sản xuất 5-10 bài viết cốt lõi (Pillars) | `claude-blog` | `/blog brief <topic>`<br>`/blog write <topic>` |
| **Tuần 4** | Sản xuất bài viết vệ tinh (Spokes) & Liên kết nội bộ | `claude-blog` | `/blog write <spoke-topic>`<br>`/blog seo-check <file>` |
| **Sau ra mắt**| Audit kỹ thuật toàn trang định kỳ | `claude-seo` | `/seo audit <domain>`<br>`/seo doctor` |
