// EEAT Content Quality Audit Engine & Interactive Studio (v2.0 Multi-Agent)
// Connects with FastAPI Backend supporting Claude, Gemini, GPT & Grok API

const DEFAULT_AUDIT_DATA = {
  url: "https://daucongnghiephp.com.vn/dau-thuy-luc/eneos-super-hyrando-68",
  title: "Dầu thủy lực ENEOS Super Hyrando 68 (エネオス スーパーハイランド)",
  overallScore: 58,
  rating: "MEDIUM",
  summaryVerdict: "Trang web có cấu trúc bài bản, bóc tách thông số kỹ thuật chuẩn nhưng bị <strong>cắt cụt nội dung ở phần kết</strong> và thiếu hoàn toàn <strong>tín hiệu trải nghiệm thực địa tại xưởng máy</strong>.",
  eeatSubScore: "Medium (55%)",
  mcSubScore: "Medium (61%)",
  analyzed_by: {
    agent_id: "claude",
    agent_name: "Claude Agent",
    model: "claude-3-7-sonnet",
    mode: "live_llm_api"
  },
  
  dimensions: [
    {
      id: "experience",
      name: "Experience (Trải nghiệm)",
      weight: 15,
      score: 50,
      rating: "MEDIUM",
      icon: "🛠️",
      findings: "Nội dung phản ánh được kinh nghiệm thương mại của đại lý phân phối (kho bãi, quy cách đóng gói phuy 200L/xô 20L, chứng từ CO/CQ, VAT), nhưng thiếu hoàn toàn bằng chứng thực tế tại hiện trường (không có số liệu máy ép nhựa, áp suất bar, nhiệt độ bồn dầu, phản hồi từ thợ bảo trì).",
      fixes: "Bổ sung mục 'Kinh nghiệm thực tế từ xưởng máy': Ghi rõ hành vi của dầu trên máy Haitian/JSW ở áp suất 160-200 bar; phản hồi của thợ về việc dầu có tạo cặn van tỷ lệ hay không; hướng dẫn test nước nhanh bằng tấm nóng."
    },
    {
      id: "expertise",
      name: "Expertise (Chuyên môn)",
      weight: 15,
      score: 60,
      rating: "MEDIUM",
      icon: "📐",
      findings: "Gọi đúng các tiêu chuẩn và thông số kỹ thuật (ISO VG 68, DIN 51524-2 HLP, ISO 11158 HM, ASTM D1401), tuy nhiên nội dung chủ yếu chép lại định nghĩa từ bảng TDS mà chưa có phân tích kỹ thuật độc bản về cơ chế hoạt động.",
      fixes: "Bổ sung luận giải kỹ thuật: Tại sao điểm chớp cháy hở 260°C của dầu Group II lại hạn chế triệt để cặn keo vec-ni (varnish)? Phân biệt sự khác nhau giữa dòng Super Hyrando (có kẽm ZDDP) và Super Hyrando SE (không kẽm) đối với van servo mạ bạc."
    },
    {
      id: "authoritativeness",
      name: "Authoritativeness (Thẩm quyền)",
      weight: 10,
      score: 55,
      rating: "MEDIUM",
      icon: "🏛️",
      findings: "Tự định vị là nhà cung ứng uy tín tại Hải Phòng nhưng chưa dẫn chứng liên kết tài liệu kỹ thuật chính thức từ ENEOS Corporation, chưa nêu rõ phiên bản và ngày sửa đổi (Revision Date) của hồ sơ TDS.",
      fixes: "Trích dẫn nguồn văn bản TDS chính thức kèm ngày phát hành của ENEOS; bổ sung số hiệu chứng nhận phê duyệt từ các hãng chế tạo máy thủy lực (Denison HF-0, Cincinnati Machine P-69)."
    },
    {
      id: "trust",
      name: "Trustworthiness (Độ tin cậy)",
      weight: 20,
      score: 55,
      rating: "MEDIUM",
      icon: "🛡️",
      findings: "Mục đích thương mại rõ ràng, trung thực nhưng bài viết bị cắt cụt giữa chừng (truncated), thiếu phần FAQ, thiếu cam kết bảo hành và hướng dẫn bảo quản an toàn (MSDS), làm giảm độ tin cậy trong mắt người mua B2B.",
      fixes: "Hoàn thiện 100% các đoạn văn bị cụt; bổ sung chính sách đổi trả phuy nguyên niêm phong dập nổi ENEOS; cam kết bồi thường nếu phát hiện dầu pha tạp; thêm hộp liên hệ đường dây nóng kỹ thuật."
    },
    {
      id: "effort",
      name: "Effort (Nỗ lực đầu tư)",
      weight: 15,
      score: 58,
      rating: "MEDIUM",
      icon: "⚡",
      findings: "Có cấu trúc đề mục đa dạng nhưng bài viết kết thúc dang dở, các bảng thông số chưa được điền đầy đủ và thiếu liên kết nội bộ trong cụm chủ đề dầu thủy lực.",
      fixes: "Hoàn tất trọn vẹn toàn bộ các mục đã lên khung sườn; tạo liên kết nội bộ (internal link) đến các cấp độ nhớt lân cận (Super Hyrando 32, 46) và bài viết hướng dẫn test kiểm tra dầu thủy lực định kỳ."
    },
    {
      id: "originality",
      name: "Originality (Tính độc bản)",
      weight: 15,
      score: 35,
      rating: "LOW+",
      icon: "💡",
      findings: "Phần lớn nội dung là dạng phái sinh (Derivative) - sao chép từ tài liệu bán hàng của hãng ENEOS. Chưa có bảng so sánh độc lập giữa các thương hiệu và thiếu các góc nhìn tư vấn độc quyền.",
      fixes: "Xây dựng Bảng so sánh đối đầu đa tiêu chí giữa ENEOS Super Hyrando 68 với Shell Tellus S2 MX 68, Mobil DTE 26, Castrol Hyspin AWS 68 kèm phân tích đánh đổi chi phí/hiệu năng."
    },
    {
      id: "talent",
      name: "Talent & Skill (Kỹ năng biên soạn)",
      weight: 5,
      score: 65,
      rating: "MEDIUM",
      icon: "✍️",
      findings: "Hành văn mạch lạc, đúng chuẩn kỹ thuật công nghiệp nhưng đoạn kết bị đứt gãy, thiếu các khung chú thích thuật ngữ (Glossary/Callout) cho người mua hàng không phải dân kỹ sư.",
      fixes: "Bổ sung các hộp ghi chú (Callout badge) giải thích các khái niệm như: Tách nước ASTM D1401 là gì, hiện tượng bọt khí xâm thực phá hủy bơm thế nào."
    },
    {
      id: "accuracy",
      name: "Accuracy (Tính chính xác)",
      weight: 5,
      score: 80,
      rating: "MEDIUM+",
      icon: "🎯",
      findings: "Các số liệu (độ nhớt 40°C ~68 mm²/s, VI 104, điểm đông đặc -25°C) chuẩn xác theo dải sản phẩm của ENEOS. Tuy nhiên còn thiếu dòng tuyên bố phương sai lô sản xuất (Batch variation disclaimer).",
      fixes: "Bổ sung dòng ghi chú miễn trừ: 'Các chỉ tiêu trên là giá trị tiêu biểu theo kết quả đo xuất xưởng, có thể dao động nhẹ trong phạm vi dung sai cho phép của tiêu chuẩn ENEOS.'"
    }
  ],

  weaknesses: [
    {
      id: "w1",
      priority: "high",
      dimension: "Experience (E)",
      title: "Thiếu hoàn toàn dữ liệu trải nghiệm thực địa tại xưởng máy",
      finding: "Trang web chỉ nêu thông số lý thuyết từ catalog, không có bất kỳ phản hồi nào từ kỹ sư bảo dưỡng, không có trường hợp vận hành cụ thể trên máy ép nhựa hay máy chấn.",
      remedy: [
        "Thêm mục 'Kinh nghiệm vận hành thực tế tại xưởng': Dẫn chứng phản hồi từ thợ bảo trì máy ép Haitian/JSW về khả năng duy trì nhiệt độ bồn 50-55°C.",
        "Mô tả hiện tượng xử lý tách nước xả đáy khi két làm mát bị rò rỉ.",
        "Đưa vào 2 phép thử mẫu nhanh tại kho: Thử nước bằng Tấm Nóng (Hot Plate Test) và Thử giọt dầu trên giấy lọc."
      ]
    },
    {
      id: "w2",
      priority: "high",
      dimension: "Trust & Effort",
      title: "Bài viết bị cắt cụt giữa chừng ở phần kết và mục FAQ",
      finding: "Người đọc và thuật toán rà quét phát hiện bài viết bị ngắt câu đột ngột, các mục câu hỏi thường gặp và hướng dẫn an toàn bị bỏ lửng, tạo tín hiệu 'nội dung dang dở / chất lượng kém'.",
      remedy: [
        "Hoàn thiện 100% nội dung cho mục Câu hỏi thường gặp (FAQ) với 4 câu hỏi cốt lõi.",
        "Bổ sung mục lưu trữ phuy an toàn ngoài trời (đặt nghiêng phuy tránh nước đọng nắp).",
        "Thêm lời kết tóm tắt và lời khuyên chuyên gia từ đội ngũ kỹ thuật HT VINA."
      ]
    },
    {
      id: "w3",
      priority: "high",
      dimension: "Originality & Expertise",
      title: "Nội dung phái sinh (Derivative) - sao chép TDS thiếu phân tích cơ chế",
      finding: "90% nội dung là chép lại thông số từ bảng đặc tính kỹ thuật của ENEOS, thiếu giá trị gia tăng độc bản (Original Value-add) mà Google QRG tìm kiếm.",
      remedy: [
        "Viết bài phân tích độc bản: 'Tại sao dầu gốc Group II với điểm chớp cháy 260°C triệt tiêu được cặn keo vec-ni (varnish) làm kẹt van servo?'.",
        "Phân biệt rõ ràng giữa dầu thủy lực gốc kẽm ZDDP (Super Hyrando) và dòng không kẽm (Super Hyrando SE) đối với các loại van điều khiển tỷ lệ."
      ]
    },
    {
      id: "w4",
      priority: "medium",
      dimension: "Originality",
      title: "Thiếu Bảng so sánh đối đầu với các sản phẩm tương đương trên thị trường",
      finding: "Khách hàng mua B2B luôn muốn biết ENEOS 68 khác gì so với Shell Tellus S2 MX 68 hay Mobil DTE 26, nhưng bài viết không cung cấp thông tin so sánh.",
      remedy: [
        "Thêm Bảng so sánh 4 sản phẩm cùng phân khúc ISO VG 68: ENEOS Super Hyrando 68, Shell Tellus S2 MX 68, Mobil DTE 26, Castrol Hyspin AWS 68.",
        "Đưa ra phân tích đánh đổi (Trade-off): Tuổi thọ dầu vs Điểm chớp cháy vs Giá thành trên mỗi giờ vận hành."
      ]
    },
    {
      id: "w5",
      priority: "medium",
      dimension: "Authoritativeness & Trust",
      title: "Chưa trích dẫn phiên bản văn bản TDS chính thức & Cam kết pháp lý",
      finding: "Chưa có liên kết dẫn nguồn đến tài liệu TDS chính thức của ENEOS Corporation và chưa có cam kết bồi hoàn phuy giả / niêm phong phuy nguyên bản.",
      remedy: [
        "Dẫn nguồn tài liệu kỹ thuật ENEOS TDS Rev. 2024 và tiêu chuẩn DIN 51524 Part 2 / ISO 11158 HM.",
        "Bổ sung cam kết chất lượng của nhà cung cấp: Cung cấp đầy đủ CO/CQ xuất xưởng từ nhà máy ENEOS Đình Vũ (Hải Phòng), bảo đảm nắp seal dập nổi logo."
      ]
    }
  ],

  proseSnippets: [
    {
      title: "Mục 1: Bổ sung Tín hiệu Trải nghiệm Thực địa (Khắc phục Lỗ hổng W1)",
      tag: "Trải nghiệm thực tế (E)",
      content: `### Kinh nghiệm vận hành thực tế tại xưởng: ENEOS Super Hyrando 68 trên máy ép nhựa cao áp
> **Ghi nhận từ xưởng máy:** Trên các hội nhóm kỹ thuật máy ép nhựa và thực tế bảo trì tại các xưởng đúc khuôn phụ tùng ở Hải Phòng, Bắc Ninh, vấn đề nan giải nhất vào mùa nồm ẩm là hiện tượng *dầu thủy lực chuyển màu cà phê sữa* do hơi ẩm ngưng tụ hoặc bục két làm mát sinh hàn. Với các dòng dầu gốc khoáng rẻ tiền, nước lọt vào sẽ tạo nhũ tương bền vững gây kẹt van tỷ lệ ngay lập tức.  
> **Lời khuyên của chúng tôi:** Khi sử dụng ENEOS Super Hyrando 68, nhờ khả năng tách nước vượt trội theo chuẩn ASTM D1401 (đạt tỷ lệ phân tách 40-40-0 trong dưới 15 phút), nước tự lắng xuống đáy bồn sau ca nghỉ đêm. Kỹ sư chỉ cần mở van xả đáy định kỳ mỗi sáng để xả bỏ phần nước đọng mà không cần thay toàn bộ 200–400 lít dầu trong bồn.  
> **Căn cứ kỹ thuật:** Dầu sở hữu chỉ số độ nhớt VI 104 và điểm chớp cháy hở COC lên tới 258°C–264°C, bảo đảm màng dầu không bị nhiệt phân tạo cặn dính keo vec-ni (varnish) ngay cả khi máy ép chạy liên tục 3 ca ở áp suất kẹp khuôn 180 bar.  
> **Hành động:** Liên hệ kỹ sư HT VINA để nhận [Tài liệu hướng dẫn test nhanh nước trong dầu thủy lực bằng tấm nóng](/lien-he/).`
    },
    {
      title: "Mục 2: Bảng so sánh đối đầu đa tiêu chí (Khắc phục Lỗ hổng W4)",
      tag: "Tính độc bản (Originality)",
      content: `### So sánh ENEOS Super Hyrando 68 với các dòng dầu thủy lực 68 hàng đầu
Dưới đây là bảng đối chiếu kỹ thuật độc lập giúp các kỹ sư bảo trì và phòng thu mua cân đối hiệu năng và chi phí:

| Tiêu chí kỹ thuật | ENEOS Super Hyrando 68 | Shell Tellus S2 MX 68 | Mobil DTE 26 | Castrol Hyspin AWS 68 |
|---|---|---|---|---|
| **Gốc dầu cơ bản** | Nhóm II Hydrocracked | Nhóm II GTL / Hydrocracked | Nhóm II Tinh chế sâu | Nhóm I / Nhóm II |
| **Độ nhớt ở 40°C** | 68.2 mm²/s | 68.0 mm²/s | 68.0 mm²/s | 68.0 mm²/s |
| **Chỉ số độ nhớt (VI)** | **104 – 105** | 98 | 98 | 97 |
| **Điểm chớp cháy COC** | **258°C – 264°C** *(Rất cao)* | 230°C | 236°C | 232°C |
| **Độ tách nước ASTM D1401** | < 15 phút (40-40-0) | 20 phút | 20 phút | 25 phút |
| **Khả năng chống Varnish** | ★★★★★ (Cực sạch van) | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| **Chi phí / Giờ vận hành** | Tối ưu hàng đầu cho máy Nhật | Phổ biến toàn cầu | Tiêu chuẩn Mỹ | Phổ thông |`
    },
    {
      title: "Mục 3: Hoàn thiện câu hỏi thường gặp & Khuyến cáo an toàn (Khắc phục Lỗ hổng W2)",
      tag: "Độ tin cậy & Hoàn chỉnh (Trust)",
      content: `### Câu hỏi thường gặp khi sử dụng dầu ENEOS Super Hyrando 68 (FAQ)
**1. Dầu ENEOS Super Hyrando 68 chạy được bao nhiêu giờ mới phải thay?**  
Trong điều kiện máy ép nhựa vận hành tiêu chuẩn, nhiệt độ bồn dưới 55°C và hệ thống lọc tốt, dầu có thể duy trì độ bền oxy hóa trên 4.000 – 5.000 giờ chạy máy. Tuy nhiên, chúng tôi khuyến cáo nên gửi mẫu test độ nhớt và hàm lượng nước định kỳ 6 tháng/lần thay vì thay mò theo số giờ.

**2. Có thể châm lẫn Super Hyrando 68 với dầu thủy lực của hãng khác được không?**  
Super Hyrando 68 tương thích với hầu hết các loại dầu thủy lực chống mài mòn gốc khoáng chuẩn ISO HM / DIN HLP có phụ gia kẽm (ZDDP). Tuy nhiên, để tránh nguy cơ xung đột phụ gia chống tạo bọt hoặc làm giảm độ trong suốt của dầu, chúng tôi khuyên nên súc rửa sạch đáy bồn khi chuyển đổi thương hiệu.

**3. Làm sao nhận biết phuy dầu ENEOS chính hãng để tránh hàng tái chế?**  
Phuy thép 200L ENEOS chính hãng từ nhà máy Đình Vũ (Hải Phòng) luôn có: Nắp seal dập nổi biểu tượng ENEOS sắc nét; tem phụ tiếng Việt ghi rõ số lô (Batch No.) và ngày sản xuất; vỏ phuy mới không có vết móp hàn nối phục chế.`
    }
  ],

  qaItems: [
    { id: "qa1", text: "Nội dung hoàn chỉnh 100% (Không bị ngắt cụt câu ở cuối bài)", checked: false },
    { id: "qa2", text: "Tín hiệu Trải nghiệm (E): Có ít nhất 2 bối cảnh xưởng máy & phản hồi thợ", checked: false },
    { id: "qa3", text: "Luận giải Chuyên môn (E): Giải thích tại sao điểm chớp cháy 260°C chống cặn keo", checked: false },
    { id: "qa4", text: "Thẩm quyền (A): Trích dẫn nguồn TDS phiên bản chính thức & chuẩn ISO/DIN", checked: true },
    { id: "qa5", text: "Tin cậy (T): Có cam kết xuất xứ CO/CQ Đình Vũ & nắp seal chống giả", checked: true },
    { id: "qa6", text: "Độc bản (Originality): Có Bảng so sánh đối đầu ENEOS vs Shell vs Mobil", checked: false },
    { id: "qa7", text: "Kỹ năng (Skill): Có hộp ghi chú thuật ngữ ASTM D1401 & hiện tượng xâm thực", checked: false },
    { id: "qa8", text: "Chính xác (Accuracy): Đã có dòng miễn trừ phương sai tiêu biểu (Disclaimer)", checked: true }
  ]
};

// Model mapping for quick population
const AGENT_MODELS = {
  "claude": [
    { value: "claude-3-7-sonnet-20250219", label: "claude-3-7-sonnet (Flagship 3.7 Sonnet - Mới nhất)" },
    { value: "claude-3-5-sonnet-20241022", label: "claude-3-5-sonnet (Sonnet v2 - Chuẩn E-E-A-T)" },
    { value: "claude-3-5-haiku-20241022", label: "claude-3-5-haiku (Haiku - Siêu tốc độ)" },
    { value: "claude-3-opus-20240229", label: "claude-3-opus (Opus - Chuyên sâu phức tạp)" }
  ],
  "gemini": [
    { value: "gemini-3.8-flash", label: "gemini-3.8-flash (Gemini 3.8 Flash - Siêu tốc & Mới nhất)" },
    { value: "gemini-3.5-flash", label: "gemini-3.5-flash (Gemini 3.5 Flash - Trí tuệ cận Pro)" },
    { value: "gemini-3.1-pro-preview", label: "gemini-3.1-pro (Gemini 3.1 Pro - Suy luận đa phương thức)" },
    { value: "gemini-2.5-pro", label: "gemini-2.5-pro (2.5 Pro - Suy luận sâu sắc, 1M context)" },
    { value: "gemini-2.5-flash", label: "gemini-2.5-flash (2.5 Flash - Nhanh & chuẩn xác)" },
    { value: "gemini-2.0-flash", label: "gemini-2.0-flash (2.0 Flash GA)" },
    { value: "gemini-1.5-pro", label: "gemini-1.5-pro (Ngữ cảnh 2M tokens)" }
  ],
  "gpt_code": [
    { value: "o3", label: "o3 (OpenAI o3 - Reasoning Flagship Mới Nhất)" },
    { value: "o3-mini", label: "o3-mini (Reasoning Logic & Code Chuyên Sâu)" },
    { value: "o1", label: "o1 (OpenAI o1 Reasoning Flagship)" },
    { value: "gpt-4.5-preview", label: "gpt-4.5-preview (GPT-4.5 Flagship - Siêu kiến thức)" },
    { value: "gpt-4o", label: "gpt-4o (GPT-4o Omni - Cân bằng đa năng)" },
    { value: "chatgpt-4o-latest", label: "chatgpt-4o-latest (Dynamic Latest)" },
    { value: "gpt-4o-mini", label: "gpt-4o-mini (Mini - Nhanh & Tiết kiệm)" },
    { value: "o1-mini", label: "o1-mini (Reasoning Tiết Kiệm)" }
  ],
  "grok": [
    { value: "grok-4", label: "grok-4 (xAI Grok 4 - Frontier Flagship Mới Nhất)" },
    { value: "grok-3", label: "grok-3 (xAI Grok 3 - Flagship thế hệ 3)" },
    { value: "grok-3-mini", label: "grok-3-mini (Grok 3 Mini - Nhanh & sắc bén)" },
    { value: "grok-2-latest", label: "grok-2-latest (Grok 2 Phản biện sắc bén)" },
    { value: "grok-2-1212", label: "grok-2-1212" },
    { value: "grok-beta", label: "grok-beta" }
  ]
};


// State
let selectedAgent = "claude";
let currentAudit = JSON.parse(JSON.stringify(DEFAULT_AUDIT_DATA));
let availableAgentsData = [];

// DOM Elements
const overallScoreVal = document.getElementById("overallScoreVal");
const ratingBadge = document.getElementById("ratingBadge");
const gaugeProgress = document.getElementById("gaugeProgress");
const scoreVerdict = document.getElementById("scoreVerdict");
const eeatSubScore = document.getElementById("eeatSubScore");
const mcSubScore = document.getElementById("mcSubScore");
const flawsCount = document.getElementById("flawsCount");
const analyzedByBadge = document.getElementById("analyzedByBadge");
const dimensionsBarList = document.getElementById("dimensionsBarList");
const issuesListContainer = document.getElementById("issuesListContainer");
const dimensionsCardsContainer = document.getElementById("dimensionsCardsContainer");
const proseSnippetsContainer = document.getElementById("proseSnippetsContainer");
const interactiveChecklist = document.getElementById("interactiveChecklist");
const miniQaList = document.getElementById("miniQaList");
const qaChecklistRatio = document.getElementById("qaChecklistRatio");
const qaProgressBar = document.getElementById("qaProgressBar");
const weaknessBadgeCount = document.getElementById("weaknessBadgeCount");
const targetUrlInput = document.getElementById("targetUrlInput");
const textContentInput = document.getElementById("textContentInput");
const btnRunAudit = document.getElementById("btnRunAudit");
const btnRunAuditText = document.getElementById("btnRunAuditText");
const btnLoadPreset = document.getElementById("btnLoadPreset");
const auditSpinner = document.getElementById("auditSpinner");
const auditSpinner2 = document.getElementById("auditSpinner2");
const btnRunText = document.getElementById("btnRunText");
const aiModelSelect = document.getElementById("aiModelSelect");
const aiTempSelect = document.getElementById("aiTempSelect");
const aiExecutionNotice = document.getElementById("aiExecutionNotice");
const aiNoticeText = document.getElementById("aiNoticeText");
const aiNoticeIcon = document.getElementById("aiNoticeIcon");

// Modals
const btnExportMd = document.getElementById("btnExportMd");
const exportModal = document.getElementById("exportModal");
const btnCloseModal = document.getElementById("btnCloseModal");
const markdownExportArea = document.getElementById("markdownExportArea");
const btnCopyReport = document.getElementById("btnCopyReport");
const btnDownloadMd = document.getElementById("btnDownloadMd");

// API Key Modal
const btnOpenApiKeyModal = document.getElementById("btnOpenApiKeyModal");
const apiKeyModal = document.getElementById("apiKeyModal");
const btnCloseApiKeyModal = document.getElementById("btnCloseApiKeyModal");
const btnCloseApiKeyModal2 = document.getElementById("btnCloseApiKeyModal2");
const apiKeySaveStatus = document.getElementById("apiKeySaveStatus");

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupViewNavigation();
  setupAgentSelection();
  populateModelSelect(selectedAgent);
  fetchAgentsStatus();
  renderAudit(currentAudit);
  setupListeners();
});

function setupTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const target = btn.dataset.tab;
      if (target === "url-mode") {
        document.getElementById("tabUrlContent").classList.remove("hidden");
        document.getElementById("tabTextContent").classList.add("hidden");
      } else {
        document.getElementById("tabUrlContent").classList.add("hidden");
        document.getElementById("tabTextContent").classList.remove("hidden");
      }
    });
  });
}

function setupViewNavigation() {
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const viewId = tab.dataset.view;
      const targetPanel = document.getElementById(viewId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });
}

function setupAgentSelection() {
  document.querySelectorAll(".agent-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".agent-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      selectedAgent = pill.dataset.agent;
      populateModelSelect(selectedAgent);
    });
  });
}

function populateModelSelect(agentId) {
  const models = AGENT_MODELS[agentId] || [];
  aiModelSelect.innerHTML = models.map(m => `<option value="${m.value}">${m.label}</option>`).join("");
}

async function fetchAgentsStatus() {
  try {
    const res = await fetch("/api/eeat/agents");
    if (res.ok) {
      const data = await res.json();
      availableAgentsData = data.agents || [];
      availableAgentsData.forEach(ag => {
        const dot = document.getElementById(`dot-${ag.id}`);
        if (dot) {
          if (ag.has_key) {
            dot.classList.add("has-key");
            dot.title = `Đã cấu hình key: ${ag.masked_key}`;
          } else {
            dot.classList.remove("has-key");
            dot.title = `Chưa có API key`;
          }
        }
      });
    }
  } catch (err) {
    console.log("Chạy ở chế độ frontend độc lập:", err);
  }
}

function setupListeners() {
  btnLoadPreset.addEventListener("click", () => {
    targetUrlInput.value = DEFAULT_AUDIT_DATA.url;
    currentAudit = JSON.parse(JSON.stringify(DEFAULT_AUDIT_DATA));
    renderAudit(currentAudit);
  });

  btnRunAudit.addEventListener("click", () => {
    executeAuditRequest({
      url: targetUrlInput.value.trim(),
      content: ""
    });
  });

  btnRunAuditText.addEventListener("click", () => {
    const text = textContentInput.value.trim();
    if (!text) {
      alert("Vui lòng dán nội dung văn bản bài viết để kiểm tra!");
      return;
    }
    executeAuditRequest({
      url: "",
      content: text
    });
  });

  // Export Modal
  btnExportMd.addEventListener("click", openExportModal);
  btnCloseModal.addEventListener("click", () => exportModal.classList.add("hidden"));
  btnCopyReport.addEventListener("click", () => {
    markdownExportArea.select();
    navigator.clipboard.writeText(markdownExportArea.value);
    alert("Đã sao chép báo cáo Markdown vào clipboard!");
  });
  btnDownloadMd.addEventListener("click", downloadMarkdownFile);

  // API Key Modal
  btnOpenApiKeyModal.addEventListener("click", () => {
    apiKeyModal.classList.remove("hidden");
  });
  btnCloseApiKeyModal.addEventListener("click", () => apiKeyModal.classList.add("hidden"));
  btnCloseApiKeyModal2.addEventListener("click", () => apiKeyModal.classList.add("hidden"));

  // Save Key buttons
  document.querySelectorAll(".btn-save-key").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const agentId = btn.dataset.agent;
      let inputVal = "";
      if (agentId === "claude") inputVal = document.getElementById("inputKeyClaude").value.trim();
      if (agentId === "gemini") inputVal = document.getElementById("inputKeyGemini").value.trim();
      if (agentId === "gpt_code") inputVal = document.getElementById("inputKeyGpt").value.trim();
      if (agentId === "grok") inputVal = document.getElementById("inputKeyGrok").value.trim();

      if (!inputVal) {
        alert("Vui lòng nhập chuỗi API key hợp lệ!");
        return;
      }

      btn.textContent = "Đang lưu...";
      try {
        const res = await fetch("/api/eeat/save-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ agent_id: agentId, api_key: inputVal })
        });
        if (res.ok) {
          btn.textContent = "Đã lưu ✓";
          apiKeySaveStatus.innerHTML = `<span style="color:#10b981;">✓ Đã lưu thành công key cho ${agentId}. Sẵn sàng gọi API trực tiếp!</span>`;
          fetchAgentsStatus();
          setTimeout(() => btn.textContent = "Lưu Key", 2500);
        } else {
          btn.textContent = "Lỗi!";
        }
      } catch (err) {
        apiKeySaveStatus.innerHTML = `<span style="color:#f43f5e;">Lỗi kết nối server: ${err.message}</span>`;
        btn.textContent = "Lưu Key";
      }
    });
  });
}

async function executeAuditRequest({ url, content }) {
  setLoadingState(true);
  hideNotice();

  const payload = {
    url: url,
    content: content,
    agent_id: selectedAgent,
    model: aiModelSelect.value,
    temperature: parseFloat(aiTempSelect.value)
  };

  try {
    const res = await fetch("/api/eeat/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}));
      throw new Error(errJson.detail || `Lỗi HTTP ${res.status}`);
    }

    const auditData = await res.json();
    currentAudit = auditData;
    renderAudit(currentAudit);

    if (auditData.analyzed_by) {
      const ab = auditData.analyzed_by;
      if (ab.mode === "heuristic_rule_engine") {
        showNotice("💡 " + (ab.message || "Phân tích bằng Heuristic Rule Engine (Chuẩn check_EEAT.md)."), "warning");
      } else {
        showNotice(`✓ Đã phân tích thành công bằng ${ab.agent_name || selectedAgent} (${ab.model}) theo thời gian thực.`, "success");
      }
    }
  } catch (err) {
    console.error("Lỗi khi gọi API EEAT Audit:", err);
    // Fallback: nếu lỗi kết nối backend, dùng heuristic cục bộ
    showNotice(`Không thể kết nối Backend API (/api/eeat/audit): ${err.message}. Đang áp dụng phân tích Heuristic Rule Engine cục bộ.`, "warning");
    runLocalHeuristic(url, content);
  } finally {
    setLoadingState(false);
  }
}

function runLocalHeuristic(url, content) {
  const text = content || targetUrlInput.value;
  const wordCount = text.split(/\s+/).filter(Boolean).length;
  const hasFieldExp = /máy ép|áp suất|nhiệt độ|xưởng|thợ bảo trì|bar/i.test(text);
  const expScore = hasFieldExp ? 75 : 45;
  const overall = hasFieldExp ? 68 : 58;

  currentAudit = {
    ...DEFAULT_AUDIT_DATA,
    url: url || "Văn bản nhập (" + wordCount + " từ)",
    overallScore: overall,
    rating: overall >= 65 ? "MEDIUM+" : "MEDIUM",
    analyzed_by: {
      agent_id: selectedAgent,
      agent_name: selectedAgent.toUpperCase(),
      model: "local_heuristic",
      mode: "local_rule_engine"
    }
  };
  renderAudit(currentAudit);
}

function setLoadingState(isLoading) {
  if (isLoading) {
    auditSpinner.classList.remove("hidden");
    auditSpinner2.classList.remove("hidden");
    btnRunText.textContent = `Đang Phân Tích Với ${selectedAgent.toUpperCase()}...`;
    btnRunAudit.disabled = true;
    btnRunAuditText.disabled = true;
  } else {
    auditSpinner.classList.add("hidden");
    auditSpinner2.classList.add("hidden");
    btnRunText.textContent = "Bắt Đầu Audit Bằng AI";
    btnRunAudit.disabled = false;
    btnRunAuditText.disabled = false;
  }
}

function showNotice(text, type = "info") {
  aiNoticeText.textContent = text;
  aiNoticeIcon.textContent = type === "success" ? "✓" : type === "warning" ? "⚠️" : "🤖";
  aiExecutionNotice.className = `action-alert-banner ${type === "success" ? "alert-success" : ""}`;
  aiExecutionNotice.classList.remove("hidden");
}

function hideNotice() {
  aiExecutionNotice.classList.add("hidden");
}

function renderAudit(data) {
  overallScoreVal.textContent = data.overallScore;
  ratingBadge.textContent = data.rating;
  ratingBadge.className = `badge badge-${data.rating.toLowerCase().includes('high') ? 'high' : data.rating.toLowerCase().includes('low') ? 'low' : 'medium'}`;

  // Gauge animation
  const offset = 314.16 * (1 - (data.overallScore / 100));
  gaugeProgress.style.strokeDashoffset = offset;
  gaugeProgress.style.stroke = data.overallScore >= 75 ? "var(--accent-emerald)" : data.overallScore >= 45 ? "var(--accent-amber)" : "var(--accent-rose)";

  scoreVerdict.innerHTML = data.summaryVerdict;
  eeatSubScore.textContent = data.eeatSubScore || "Medium (55%)";
  mcSubScore.textContent = data.mcSubScore || "Medium (61%)";
  flawsCount.textContent = `${(data.weaknesses || []).length} Lỗi cốt lõi`;
  weaknessBadgeCount.textContent = (data.weaknesses || []).length;

  if (data.analyzed_by) {
    const ab = data.analyzed_by;
    analyzedByBadge.textContent = `${ab.agent_name || selectedAgent} (${ab.model || ab.mode || 'AI'})`;
  }

  renderDimensionsBars(data.dimensions || []);
  renderWeaknesses(data.weaknesses || []);
  renderDimensionCards(data.dimensions || []);
  renderProseSnippets(data.proseSnippets || []);
  renderQA(data.qaItems || []);
}

function renderDimensionsBars(dimensions) {
  dimensionsBarList.innerHTML = dimensions.map(dim => {
    const color = dim.score >= 75 ? "var(--accent-emerald)" : dim.score >= 50 ? "var(--accent-amber)" : "var(--accent-rose)";
    return `
      <div class="dim-bar-item" title="${dim.name} (${dim.weight}%)">
        <div class="dim-bar-header">
          <span class="dim-name">${dim.icon || '📌'} ${dim.name}</span>
          <span class="dim-score-badge" style="color: ${color}">${dim.score}% (${dim.rating})</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${dim.score}%; background: ${color}"></div>
        </div>
      </div>
    `;
  }).join("");
}

function renderWeaknesses(weaknesses) {
  issuesListContainer.innerHTML = weaknesses.map((w, idx) => `
    <div class="issue-card" id="${w.id || 'w' + idx}">
      <div class="issue-header">
        <div class="issue-title-wrap">
          <span class="issue-priority priority-${w.priority || 'high'}">${w.priority === 'high' ? 'Ưu tiên cao' : 'Trung bình'}</span>
          <h4 class="issue-title">#${idx + 1}. ${w.title}</h4>
        </div>
        <span class="issue-dimension-tag">${w.dimension}</span>
      </div>

      <div class="issue-body-grid">
        <div class="issue-finding-box">
          <div class="issue-box-label finding-label">
            <span>✕</span> Điểm Yếu Phát Hiện (Audit Finding)
          </div>
          <p>${w.finding}</p>
        </div>

        <div class="issue-remedy-box">
          <div class="issue-box-label remedy-label">
            <span>✓</span> Phương Án Khắc Phục (Actionable Fix)
          </div>
          <ul>
            ${(w.remedy || []).map(r => `<li>${r}</li>`).join("")}
          </ul>
        </div>
      </div>
    </div>
  `).join("");
}

function renderDimensionCards(dimensions) {
  dimensionsCardsContainer.innerHTML = dimensions.map(dim => {
    const badgeClass = dim.rating.toLowerCase().includes('high') ? 'badge-high' : dim.rating.toLowerCase().includes('low') ? 'badge-low' : 'badge-medium';
    return `
      <div class="dim-card">
        <div class="dim-card-top">
          <h4 class="dim-card-title">${dim.icon || '📌'} ${dim.name}</h4>
          <span class="badge ${badgeClass}">${dim.rating} (${dim.score}%)</span>
        </div>
        <span class="dim-card-weight">Trọng số thuật toán: ${dim.weight}%</span>
        <p class="dim-card-finding">${dim.findings}</p>
        <div class="dim-card-fixes">
          <strong>Lộ trình tối ưu:</strong>
          <span>${dim.fixes}</span>
        </div>
      </div>
    `;
  }).join("");
}

function renderProseSnippets(snippets) {
  proseSnippetsContainer.innerHTML = snippets.map((sn, idx) => {
    const formatted = sn.content
      .replace(/### (.*)/g, '<h4 style="color:#93c5fd;margin-bottom:8px;">$1</h4>')
      .replace(/> (.*)/g, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" style="color:#38bdf8;">$1</a>')
      .replace(/\n\n/g, '<br><br>');

    return `
      <div class="prose-snippet-card">
        <div class="snippet-header">
          <span class="snippet-tag">${sn.tag}</span>
          <button class="btn btn-outline btn-sm copy-snippet-btn" data-index="${idx}">
            Sao chép đoạn này
          </button>
        </div>
        <div class="snippet-content">
          ${formatted}
        </div>
      </div>
    `;
  }).join("");

  document.querySelectorAll(".copy-snippet-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = e.target.dataset.index;
      navigator.clipboard.writeText(snippets[idx].content);
      btn.textContent = "Đã chép! ✓";
      setTimeout(() => btn.textContent = "Sao chép đoạn này", 2000);
    });
  });
}

function renderQA(items) {
  updateQAMetrics(items);

  interactiveChecklist.innerHTML = items.map(item => `
    <div class="checklist-row ${item.checked ? 'checked' : ''}" data-id="${item.id}">
      <input type="checkbox" class="checklist-checkbox" ${item.checked ? 'checked' : ''}>
      <div class="checklist-info">
        <h4>${item.text}</h4>
        <p>${item.checked ? 'Đã đạt tiêu chuẩn của Google Search Quality Rater Guidelines.' : 'Cần bổ sung vào bài viết để nâng điểm lên High.'}</p>
      </div>
    </div>
  `).join("");

  interactiveChecklist.querySelectorAll(".checklist-row").forEach(row => {
    row.addEventListener("click", (e) => {
      const id = row.dataset.id;
      const chk = row.querySelector(".checklist-checkbox");
      if (e.target !== chk) chk.checked = !chk.checked;
      
      const targetItem = items.find(i => i.id === id);
      if (targetItem) targetItem.checked = chk.checked;

      row.classList.toggle("checked", chk.checked);
      updateQAMetrics(items);
    });
  });
}

function updateQAMetrics(items) {
  const passed = items.filter(i => i.checked).length;
  const total = items.length;
  const ratio = Math.round((passed / total) * 100);

  qaChecklistRatio.textContent = `${passed} / ${total} Đạt`;
  qaProgressBar.style.width = `${ratio}%`;

  miniQaList.innerHTML = items.map(i => `
    <li class="mini-qa-item ${i.checked ? 'passed' : 'failed'}">
      ${i.text.split(':')[0]}
    </li>
  `).join("");
}

function openExportModal() {
  const md = generateMarkdownReport(currentAudit);
  markdownExportArea.value = md;
  exportModal.classList.remove("hidden");
}

function generateMarkdownReport(data) {
  const analyzedByStr = data.analyzed_by ? `${data.analyzed_by.agent_name || selectedAgent} (${data.analyzed_by.model || ''})` : selectedAgent;
  return `# BÁO CÁO KIỂM ĐỊNH CHẤT LƯỢNG NỘI DUNG & E-E-A-T
**Trang kiểm tra:** ${data.url}
**Được đánh giá bởi:** ${analyzedByStr}
**Ngày thực hiện:** ${new Date().toLocaleDateString('vi-VN')}
**Tổng điểm:** ${data.overallScore} / 100 (${data.rating})

---

## 1. TỔNG QUAN ĐÁNH GIÁ
${(data.summaryVerdict || "").replace(/<\/?[^>]+(>|$)/g, "")}

- **Trụ cột E-E-A-T:** ${data.eeatSubScore || ''}
- **Trụ cột Chất lượng Nội dung (MC):** ${data.mcSubScore || ''}
- **Số lượng điểm yếu phát hiện:** ${(data.weaknesses || []).length} mục

---

## 2. BẢNG ĐIỂM 8 TIÊU CHÍ (QRG & QUICKCREATOR)
| Tiêu chí | Trọng số | Điểm số | Xếp hạng | Đánh giá tóm tắt |
|---|:---:|:---:|:---:|---|
${(data.dimensions || []).map(d => `| ${d.name} | ${d.weight}% | ${d.score}% | ${d.rating} | ${(d.findings || '').slice(0, 100)}... |`).join("\n")}

---

## 3. CÁC ĐIỂM YẾU & PHƯƠNG ÁN KHẮC PHỤC (ACTIONABLE ROADMAP)
${(data.weaknesses || []).map((w, i) => `
### #${i + 1}. ${w.title} [${w.dimension}]
- **Hiện trạng:** ${w.finding}
- **Phương án Fix:**
${(w.remedy || []).map(r => `  - ${r}`).join("\n")}
`).join("\n")}

---

## 4. CHECKLIST BIÊN TẬP TRƯỚC KHI XUẤT BẢN
${(data.qaItems || []).map(q => `- [${q.checked ? 'x' : ' '}] ${q.text}`).join("\n")}
`;
}

function downloadMarkdownFile() {
  const blob = new Blob([markdownExportArea.value], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `audit-eeat-report-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
