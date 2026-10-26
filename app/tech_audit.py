"""
Technical (Schema & Citation) Audit
Chấm điểm hoàn thiện kỹ thuật theo Mục VI của check_EEAT.md.

Điểm này tính bằng quy tắc cố định từ JSON-LD của HTML gốc (không qua AI),
báo song song và KHÔNG cộng vào điểm nội dung (overallScore).
"""

import re
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx

logger = logging.getLogger("tech_audit")

ARTICLE_TYPES = {"Article", "BlogPosting", "NewsArticle", "TechArticle"}
STANDARD_HOSTS = ("astm.org", "iso.org", "din.de", "vsqi.gov.vn", "tcvn.gov.vn", "api.org", "sae.org", "jis", "nlgi.org")
# Nguồn không được dùng làm citation cho blog (Mục 6.4 – A4)
WEAK_SOURCE_HOSTS = ("facebook.com", "shopee.vn", "lazada.vn", "tiki.vn", "reddit.com", "tiktok.com", "youtube.com", "zalo.me", "eng-tips.com", "otofun.net", "webtretho.com", "voz.vn")

SCALE = [
    {"min": 90, "label": "Hoàn thiện", "level": "high", "action": "Đăng / giữ nguyên"},
    {"min": 75, "label": "Khá", "level": "high", "action": "Sửa các mục thiếu ở lần cập nhật tới"},
    {"min": 60, "label": "Thiếu", "level": "medium", "action": "Sửa trước khi chạy quảng cáo hoặc gửi lập chỉ mục"},
    {"min": 0, "label": "Chưa đạt", "level": "low", "action": "Sửa ngay (thường do sai loại schema hoặc citation rỗng)"},
]

PAGE_TYPE_LABELS = {
    "product": "Trang sản phẩm",
    "blog": "Bài blog / hỗ trợ kỹ thuật",
    "price": "Trang báo giá",
    "category": "Trang danh mục",
    "other": "Chưa xác định",
}


# ---------- Đọc JSON-LD ----------

def extract_jsonld(html: str) -> Dict[str, Any]:
    """Trả về danh sách node (đã gộp theo @id) và số khối lỗi cú pháp"""
    blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    raw_nodes: List[Dict[str, Any]] = []
    errors = 0
    for b in blocks:
        try:
            data = json.loads(b.strip())
        except Exception:
            errors += 1
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        raw_nodes.extend(x for x in items if isinstance(x, dict))

    # Trang tách một thực thể ra nhiều khối cùng @id (ví dụ ItemPage + khối text) -> gộp lại
    merged: Dict[str, Dict[str, Any]] = {}
    nodes: List[Dict[str, Any]] = []
    for n in raw_nodes:
        nid = n.get("@id")
        if nid and nid in merged:
            merged[nid].update({k: v for k, v in n.items() if k not in merged[nid]})
            continue
        node = dict(n)
        if nid:
            merged[nid] = node
        nodes.append(node)
    return {"nodes": nodes, "errors": errors, "blocks": len(blocks)}


def types_of(node: Dict[str, Any]) -> set:
    t = node.get("@type", [])
    return set(t if isinstance(t, list) else [t])


def find(nodes, *type_names) -> Optional[Dict[str, Any]]:
    for n in nodes:
        if types_of(n) & set(type_names):
            return n
    return None


def resolve(nodes, ref) -> Optional[Dict[str, Any]]:
    """Lấy node thật từ tham chiếu {"@id": ...}"""
    if isinstance(ref, list):
        ref = ref[0] if ref else None
    if not isinstance(ref, dict):
        return None
    if "@id" in ref and len(ref) <= 2:
        for n in nodes:
            if n.get("@id") == ref["@id"]:
                return n
    return ref


def has(node: Optional[Dict[str, Any]], key: str) -> bool:
    if not node:
        return False
    v = node.get(key)
    return v not in (None, "", [], {})


def as_list(v) -> List[Any]:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


# ---------- Loại trang ----------

def detect_page_type(nodes, url: str) -> str:
    path = urlparse(url).path.lower()
    all_types = set().union(*[types_of(n) for n in nodes]) if nodes else set()
    if "Product" in all_types or "ItemPage" in all_types:
        return "product"
    if path.startswith("/bao-gia"):
        return "price"
    if all_types & ARTICLE_TYPES or path.startswith("/ho-tro-ky-thuat"):
        return "blog"
    if "CollectionPage" in all_types:
        return "category"
    return "other"


# ---------- Kiểm tra link citation ----------

async def check_links(urls: List[str]) -> Dict[str, int]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; EEATStudio/1.1)"}
    sem = asyncio.Semaphore(6)

    async def one(client, u):
        async with sem:
            try:
                r = await client.head(u, headers=headers)
                if r.status_code in (403, 405) or r.status_code >= 500:
                    r = await client.get(u, headers=headers)
                return u, r.status_code
            except Exception:
                return u, 0

    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        results = await asyncio.gather(*(one(client, u) for u in urls[:25]))
    return dict(results)


def link_state(code: int) -> str:
    """ok: mở được; dead: 404/410; unverified: máy chủ chặn bot, quá tải hoặc hết thời gian (kiểm tay)"""
    if 200 <= code < 400:
        return "ok"
    if code in (404, 410):
        return "dead"
    return "unverified"


def usable(u: str, link_status: Dict[str, int]) -> bool:
    return link_state(link_status.get(u, 0)) != "dead"


def citation_urls(node: Optional[Dict[str, Any]], base: str) -> List[str]:
    out = []
    for c in as_list((node or {}).get("citation")):
        u = c if isinstance(c, str) else (c.get("url") or c.get("@id")) if isinstance(c, dict) else None
        if u:
            out.append(urljoin(base, u))
    return list(dict.fromkeys(out))


def classify_citation(u: str, product_page: bool = False) -> str:
    host = urlparse(u).netloc.lower()
    low = u.lower()
    if any(h in host for h in STANDARD_HOSTS):
        return "standard"
    if any(h in host for h in WEAK_SOURCE_HOSTS):
        return "weak"
    # Trang sản phẩm: template chỉ đưa tds_url và link tiêu chuẩn vào citation, nên link còn lại là TDS / trang hãng
    if product_page or "tds" in low or "/tai-lieu/" in low or low.endswith(".pdf"):
        return "tds"
    return "other"


# ---------- Hạng mục chung ----------

def item(id_, name, points, max_, details, applicable=True):
    points = round(max(0.0, min(points, max_)), 1) if applicable else 0
    if not applicable:
        status = "na"
    elif points >= max_:
        status = "pass"
    elif points > 0:
        status = "partial"
    else:
        status = "fail"
    return {"id": id_, "name": name, "points": points, "max": max_, "applicable": applicable, "status": status, "details": details}


def trust_entities(nodes, id_, max_):
    # Chấm Person đầy đủ nhất trong trang (tác giả hoặc người duyệt)
    persons = [n for n in nodes if "Person" in types_of(n)]
    person = max(persons, key=lambda p: sum(has(p, k) for k in ("hasCredential", "knowsAbout", "sameAs", "workExample")), default=None)
    org = find(nodes, "Organization")
    got, miss = 0.0, []
    for k in ("hasCredential", "knowsAbout", "sameAs", "workExample"):
        if has(person, k):
            got += max_ * 0.15
        else:
            miss.append(f"Person.{k}")
    for k in ("sameAs", "publishingPrinciples"):
        if has(org, k):
            got += max_ * 0.2
        else:
            miss.append(f"Organization.{k}")
    return item(id_, "Thực thể tin cậy (Person + Organization)", got, max_,
                "Đủ trường" if not miss else "Thiếu: " + ", ".join(miss))


# ---------- Bảng chấm sản phẩm (P1–P9) ----------

def score_product(nodes, errors, link_status, base) -> Dict[str, Any]:
    page = find(nodes, "ItemPage", "WebPage")
    product = find(nodes, "Product")
    has_article = any(types_of(n) & ARTICLE_TYPES for n in nodes)
    items = []

    # P1
    pt = types_of(page) if page else set()
    if has_article:
        p1, d1 = 0, "Trang sản phẩm có Article/BlogPosting → cần gỡ (thực thể chính phải là Product)."
    elif {"ItemPage", "WebPage"} <= pt and has(page, "mainEntity"):
        p1, d1 = 10, "[\"ItemPage\",\"WebPage\"] + mainEntity → Product"
    elif "ItemPage" in pt:
        p1, d1 = 6, "Có ItemPage nhưng thiếu WebPage hoặc mainEntity"
    else:
        p1, d1 = 0, "Không có ItemPage"
    items.append(item("P1", "Loại trang (ItemPage, không Article)", p1, 10, d1))

    offers = (product or {}).get("offers")
    price_ok = bool(offers)

    # P2 (không có Product vì chưa có giá → P2–P4 không áp dụng, điểm chia lại)
    fields = ["name", "brand", "sku", "image", "description", "category"]
    miss = [f for f in fields if not has(product, f)]
    items.append(item("P2", "Product cơ bản", 15 * (len(fields) - len(miss)) / len(fields), 15,
                      "Không có Product (chưa có giá) → không áp dụng" if not product else
                      ("Đủ trường" if not miss else "Thiếu: " + ", ".join(miss)),
                      applicable=bool(product)))

    # P3
    if not price_ok:
        items.append(item("P3", "Giá (offers)", 0, 15, "Chưa có giá → không áp dụng, điểm chia lại cho các mục khác", applicable=False))
    else:
        o = resolve(nodes, offers) or {}
        got, miss = 0, []
        if types_of(o) & {"AggregateOffer", "Offer"}:
            got += 5
        else:
            miss.append("@type AggregateOffer")
        if o.get("priceCurrency") == "VND":
            got += 3
        else:
            miss.append("priceCurrency VND")
        if has(o, "lowPrice") and has(o, "highPrice") or has(o, "price"):
            got += 4
        else:
            miss.append("lowPrice/highPrice")
        if has(o, "availability"):
            got += 3
        else:
            miss.append("availability")
        items.append(item("P3", "Giá (offers)", got, 15,
                          ("Đủ trường" if not miss else "Thiếu: " + ", ".join(miss)) + ". Khớp gia-cong-khai.json: kiểm tay."))

    # P4
    props = as_list((product or {}).get("additionalProperty"))
    with_method = [p for p in props if isinstance(p, dict) and has(p, "description")]
    p4 = (5 if len(props) >= 3 else len(props) * 5 / 3) + (5 * len(with_method) / len(props) if props else 0)
    items.append(item("P4", "Thông số (additionalProperty)", p4, 10,
                      f"{len(props)} thông số, {len(with_method)} có mã phương pháp thử" if product else "Không có Product → không áp dụng",
                      applicable=bool(product)))

    # P5
    cites = citation_urls(page, base)
    live = [u for u in cites if usable(u, link_status)]
    dead = [u for u in cites if u not in live]
    unverified = [u for u in live if link_state(link_status.get(u, 0)) == "unverified"]
    tds_live = [u for u in live if classify_citation(u, True) == "tds"]
    std_live = [u for u in live if classify_citation(u, True) == "standard"]
    p5 = (10 if tds_live else 0) + (10 if std_live else 0)
    if not cites:
        d5 = "citation rỗng: thiếu tds_url và specs[].method trong frontmatter"
    else:
        parts = [f"TDS: {'có' if tds_live else 'KHÔNG'}", f"tiêu chuẩn: {len(std_live)} link"]
        if dead:
            parts.append(f"{len(dead)} link chết (404)")
        if unverified:
            parts.append(f"{len(unverified)} link chặn bot / quá thời gian, kiểm tay")
        d5 = ", ".join(parts)
    items.append(item("P5", "Nguồn dẫn (citation)", p5, 20, d5))

    # P6
    got = sum(2.5 for k in ("author", "reviewedBy", "datePublished", "dateModified") if has(page, k))
    miss = [k for k in ("author", "reviewedBy", "datePublished", "dateModified") if not has(page, k)]
    items.append(item("P6", "Tác giả, ngày", got, 10,
                      ("Đủ trường" if not miss else "Thiếu: " + ", ".join(miss)) + ". Khớp byline hiển thị: kiểm tay."))

    # P7
    items.append(trust_entities(nodes, "P7", 10))

    # P8
    got = (3 if has(page, "text") and has(page, "wordCount") else 0) + (2 if find(nodes, "BreadcrumbList") else 0)
    items.append(item("P8", "Nội dung cho máy đọc (text + Breadcrumb)", got, 5,
                      f"wordCount = {(page or {}).get('wordCount', 'không có')}, BreadcrumbList: {'có' if find(nodes, 'BreadcrumbList') else 'không'}"))

    # P9
    fake_review = has(product, "review") or has(product, "aggregateRating")
    got = 5 - (5 if errors else 0) - (5 if fake_review else 0)
    issues = []
    if errors:
        issues.append(f"{errors} khối JSON-LD lỗi cú pháp")
    if fake_review:
        issues.append("có review/aggregateRating (không được tự viết)")
    items.append(item("P9", "Sạch lỗi", got, 5, "Không lỗi" if not issues else "; ".join(issues)))

    cap = {"applied": False}
    if p5 == 0:
        cap = {"applied": True, "limit": 70, "reason": "P5 = 0 (chưa có TDS / citation) → tối đa 70, trạng thái \"Chưa đạt – cần TDS\""}
    return {"items": items, "cap": cap, "citations": cites}


# ---------- Bảng chấm blog / báo giá (A1–A8) ----------

def score_article(nodes, errors, link_status, base, html) -> Dict[str, Any]:
    art = find(nodes, *ARTICLE_TYPES)
    items = []

    # A1
    if art:
        got = 6 + (2 if str(art.get("@id", "")).endswith("#article") else 0) + (2 if has(art, "mainEntityOfPage") else 0)
        d = f"@type {sorted(types_of(art) & ARTICLE_TYPES)[0]}" + ("" if got == 10 else " – thiếu @id #article hoặc mainEntityOfPage")
    else:
        got, d = 0, "Không có Article/BlogPosting → A1–A3 = 0"
    items.append(item("A1", "Có Article", got, 10, d))

    # A2 – 4 trường cốt lõi (mục "Article Schema x/4" của công cụ ngoài)
    core = {}
    core["headline"] = has(art, "headline")
    author = resolve(nodes, (art or {}).get("author"))
    core["author (Person)"] = bool(author) and "Person" in types_of(author)
    iso = re.compile(r"^\d{4}-\d{2}-\d{2}")
    core["datePublished"] = bool(art) and bool(iso.match(str(art.get("datePublished", ""))))
    core["dateModified"] = bool(art) and bool(iso.match(str(art.get("dateModified", ""))))
    ok = [k for k, v in core.items() if v]
    items.append(item("A2", f"Article {len(ok)}/4 trường cốt lõi", 5 * len(ok), 20,
                      "Đủ 4/4" if len(ok) == 4 else "Thiếu: " + ", ".join(k for k, v in core.items() if not v)))

    # A3
    miss = [k for k in ("description", "image", "publisher") if not has(art, k)]
    items.append(item("A3", "Trường bổ sung", 10 * (3 - len(miss)) / 3, 10,
                      "Đủ trường" if not miss else "Thiếu: " + ", ".join(miss)))

    # A4
    cites = citation_urls(art, base)
    live = [u for u in cites if usable(u, link_status)]
    weak = [u for u in cites if classify_citation(u) == "weak"]
    primary_live = [u for u in live if u not in weak]
    got = 20 if len(primary_live) >= 3 else 10 if primary_live else 0
    got -= 5 * len(weak)
    dead = len(cites) - len(live)
    unverified = [u for u in live if link_state(link_status.get(u, 0)) == "unverified"]
    d = f"{len(primary_live)} nguồn gốc dùng được / {len(cites)} citation"
    if weak:
        d += f"; {len(weak)} nguồn yếu (diễn đàn, sàn, mạng xã hội)"
    if dead:
        d += f"; {dead} link chết (404) cần thay"
    if unverified:
        d += f"; {len(unverified)} link chặn bot / quá thời gian, kiểm tay"
    items.append(item("A4", "Nguồn dẫn (citation)", got, 20, d if cites else "citation rỗng: thêm citations: vào frontmatter"))

    # A5
    body = (art or {}).get("articleBody") or (art or {}).get("text") or ""
    words = (art or {}).get("wordCount") or len(str(body).split())
    try:
        words = int(words)
    except Exception:
        words = 0
    got = (4 if body else 0) + min(6, 6 * words / 1000)
    items.append(item("A5", "Độ sâu (articleBody)", got, 10, f"articleBody: {'có' if body else 'không'}, {words} từ"))

    # A6 – reviewedBy nằm ở WebPage bao bài
    wp = next((n for n in nodes if "WebPage" in types_of(n) and has(n, "reviewedBy")), None) or (art if has(art, "reviewedBy") else None)
    got = (6 if wp else 0) + (4 if has(wp, "lastReviewed") else 0)
    items.append(item("A6", "Người duyệt", got, 10,
                      "Có reviewedBy" + (" + lastReviewed" if has(wp, "lastReviewed") else ", thiếu lastReviewed") if wp else "Không có reviewedBy"))

    # A7
    items.append(trust_entities(nodes, "A7", 10))

    # A8
    got, issues = 0, []
    if find(nodes, "BreadcrumbList"):
        got += 4
    else:
        issues.append("thiếu BreadcrumbList")
    faq = find(nodes, "FAQPage")
    if faq:
        visible = re.sub(r"<[^>]+>", " ", re.sub(r"<script[\s\S]*?</script>", " ", html))
        qs = [q.get("name", "") for q in as_list(faq.get("mainEntity")) if isinstance(q, dict)]
        hidden = [q for q in qs if q and q[:40] not in visible]
        if hidden:
            issues.append(f"FAQPage có {len(hidden)} câu hỏi không hiển thị trên trang")
        else:
            got += 3
    else:
        got += 3
    if any(has(n, "review") or has(n, "aggregateRating") for n in nodes):
        issues.append("có review/aggregateRating tự viết")
    else:
        got += 3
    if errors:
        got -= 3
        issues.append(f"{errors} khối JSON-LD lỗi cú pháp")
    items.append(item("A8", "Sạch lỗi", got, 10, "Không lỗi" if not issues else "; ".join(issues)))

    a4 = next(i for i in items if i["id"] == "A4")["points"]
    cap = {"applied": False}
    if not art or a4 == 0:
        cap = {"applied": True, "limit": 60, "reason": ("Không có Article" if not art else "A4 = 0 (không có nguồn dẫn)") + " → tối đa 60, trạng thái \"Chưa đạt\""}
    return {"items": items, "cap": cap, "citations": cites}


# ---------- Điều phối ----------

def status_for(score: float) -> Dict[str, Any]:
    for s in SCALE:
        if score >= s["min"]:
            return s
    return SCALE[-1]


async def run_technical_audit(html: str, url: str) -> Dict[str, Any]:
    parsed = extract_jsonld(html)
    nodes, errors = parsed["nodes"], parsed["errors"]
    page_type = detect_page_type(nodes, url)
    schema_types = [" + ".join(sorted(types_of(n))) for n in nodes]

    base_result = {
        "available": True,
        "separateFromContent": True,
        "pageType": page_type,
        "pageTypeLabel": PAGE_TYPE_LABELS[page_type],
        "schemaTypes": schema_types,
        "jsonLdBlocks": parsed["blocks"],
        "scale": SCALE,
        "notes": [],
    }

    if page_type in ("category", "other"):
        base_result.update({
            "score": None,
            "status": "Không áp dụng",
            "statusLevel": "medium",
            "items": [],
            "citations": [],
            "cap": {"applied": False},
        })
        base_result["notes"].append("Mục VI chỉ có bảng chấm cho trang sản phẩm và bài blog / báo giá.")
        return base_result

    # Lấy danh sách citation trước để kiểm link một lần
    probe = find(nodes, "ItemPage", "WebPage") if page_type == "product" else find(nodes, *ARTICLE_TYPES)
    link_status = await check_links(citation_urls(probe, url))

    if page_type == "product":
        res = score_product(nodes, errors, link_status, url)
        base_result["notes"].append("Công cụ ngoài báo \"Article Schema 0/4\" cho trang này → Không áp dụng, bỏ qua.")
    else:
        res = score_article(nodes, errors, link_status, url, html)

    applicable = [i for i in res["items"] if i["applicable"]]
    max_total = sum(i["max"] for i in applicable) or 1
    raw = sum(i["points"] for i in applicable) * 100 / max_total
    score = round(raw)
    if res["cap"].get("applied"):
        score = min(score, res["cap"]["limit"])
    st = status_for(score)
    status_label = st["label"]
    if res["cap"].get("applied") and page_type == "product":
        status_label = "Chưa đạt – cần TDS"

    base_result.update({
        "score": score,
        "rawScore": round(raw, 1),
        "status": status_label,
        "statusLevel": "low" if res["cap"].get("applied") else st["level"],
        "action": st["action"],
        "items": res["items"],
        "cap": res["cap"],
        "citations": [{"url": u, "httpStatus": link_status.get(u, 0), "state": link_state(link_status.get(u, 0)),
                       "kind": classify_citation(u, page_type == "product")} for u in res["citations"]],
    })
    base_result["notes"].append("\"Expert review process\" (eeatcheck) luôn 0 do lỗi công cụ – bỏ qua.")
    return base_result
