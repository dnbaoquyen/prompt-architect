#!/usr/bin/env python3
"""Bước cuối: lọc hạng tạp chí (IC7) và lĩnh vực tạp chí (EC10) cho danh sách bài
đã qua sàng lọc nội dung.

Chạy SAU khi NotebookLM và người sàng lọc đã chốt danh sách INCLUDE.

IC7 đạt khi tạp chí thuộc ít nhất một trong ba danh sách:
  - Danh sách Marketing Level 1 (gồm cả Elite Level 1)
  - ABDC JQL 2025: A*, A hoặc B
  - SCImago (SJR) Best Quartile: Q1 hoặc Q2

Cờ Biz (cho EC10) suy ra từ lĩnh vực của tạp chí:
  - Y : có trong ABDC hoặc Level 1, hoặc SJR Areas có Business / Economics / Decision Sciences
  - ? : SJR Areas có Psychology / Social Sciences / Arts and Humanities / Multidisciplinary,
        hoặc Categories có Food Science, Nutrition, Communication, Tourism, Human-Computer
        Interaction  -> giữ, gắn social-mkt
  - N : tìm thấy tạp chí nhưng không thuộc các nhóm trên -> EC10 (vẫn cần kiểm tay)
  - Không xác định: không tìm thấy tạp chí

Khớp theo ISSN trước, sau đó theo tên tạp chí đã chuẩn hóa.

Ví dụ:
  python3 rank_journals.py \
      --records danh_sach_cuoi.csv \
      --sjr scimagojr_2025.csv \
      --abdc ABDC-JQL-2025.xlsx \
      --out out/

Kết quả:
  out/records_ranked.csv  bản ghi + cột Level1, ABDC_2025, SJR_Q, SJR_Type, SJR_Areas,
                          IC7, Biz, EC10, Tag
  out/final_review.csv    chỉ các bài cần kiểm tay: IC7 khác "Đạt" hoặc Biz khác "Y"/"?"
  out/whitelist.csv       mọi tạp chí đạt IC7 (để tra thủ công)
"""
import argparse
import os
import re
import sys

import pandas as pd

LEVEL1_ELITE = [
    "Journal of Consumer Research",
    "Journal of Marketing Research",
    "Journal of Marketing",
    "Marketing Science",
    "Journal of Retailing",
    "Journal of the Academy of Marketing Science",  # JAMS
    "Journal of Business Research",
    "Journal of Consumer Psychology",
    "International Journal of Research in Marketing",
]
LEVEL1 = [
    "European Journal of Marketing",
    "Industrial Marketing Management",
    "Journal of Advertising",
    "Journal of Consumer Marketing",
    "Journal of International Marketing",
    "Journal of Marketing Theory and Practice",
    "Journal of Personal Selling and Sales Management",
    "Journal of Services Marketing",
    "Journal of Service Research",  # ghi là "Journal of Services Research" trong PDF
    "Marketing Letters",
    "Psychology and Marketing",
]

# Tên cột thường gặp trong file xuất từ Rayyan, Scopus, Web of Science.
COLS = {
    "id": ["id", "key", "rayyan id", "record id", "stt"],
    "title": ["title", "article title", "document title"],
    "abstract": ["abstract"],
    "journal": ["journal", "source title", "source", "publication title", "journal title"],
    "issn": ["issn", "issns"],
    "eissn": ["eissn", "e-issn", "issn online"],
    "doi": ["doi"],
    "authors": ["authors", "author", "author full names"],
    "year": ["year", "publication year", "py"],
    "type": ["document type", "type", "publication type"],
    "biz": ["biz"],
    "group": ["group", "nhóm", "nhom"],
    "retraction": ["retraction", "retracted"],
}


def norm_title(s):
    s = str(s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"^the ", "", re.sub(r"\s+", " ", s).strip())
    return s


def issns(s):
    return set(re.findall(r"\d{7}[\dx]", re.sub(r"[-\s]", "", str(s or "").lower())))


def load_sjr(path):
    df = pd.read_csv(path, sep=";", dtype=str).fillna("")
    by_issn, by_title = {}, {}
    for _, r in df.iterrows():
        q = r["SJR Best Quartile"].strip()
        rec = (q if q != "-" else "", r["Type"], r["Areas"], r["Categories"])
        for i in issns(r["Issn"]):
            by_issn.setdefault(i, rec)
        by_title.setdefault(norm_title(r["Title"]), rec)
    return df, by_issn, by_title


def load_abdc(path):
    raw = pd.read_excel(path, sheet_name="2025 JQL", header=None, dtype=str)
    hdr = raw.index[raw.apply(lambda r: r.astype(str).str.strip().eq("Journal Title").any(), axis=1)][0]
    df = raw.iloc[hdr + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[hdr]]
    df = df.dropna(subset=["Journal Title"])
    rating = [c for c in df.columns if "rating" in c.lower()][0]
    by_issn, by_title = {}, {}
    for _, r in df.iterrows():
        rank = str(r[rating]).strip()
        for i in issns(f"{r.get('ISSN', '')} {r.get('ISSNOnline', '')}"):
            by_issn.setdefault(i, rank)
        by_title.setdefault(norm_title(r["Journal Title"]), rank)
    return df, rating, by_issn, by_title


BIZ_AREAS = ("business, management and accounting", "economics, econometrics and finance", "decision sciences")
SOCIAL_AREAS = ("psychology", "social sciences", "arts and humanities", "multidisciplinary")
SOCIAL_CATS = ("food science", "nutrition", "communication", "tourism", "human-computer interaction", "marketing")


def biz_of(in_abdc_or_level1, areas, cats):
    a, c = areas.lower(), cats.lower()
    if in_abdc_or_level1 or any(x in a for x in BIZ_AREAS):
        return "Y"
    if any(x in a for x in SOCIAL_AREAS) or any(x in c for x in SOCIAL_CATS):
        return "?"
    return "N" if (areas or cats) else "Không xác định"


def level1_of(title):
    t = norm_title(title)
    if t in {norm_title(x) for x in LEVEL1_ELITE}:
        return "Elite"
    if t in {norm_title(x) for x in LEVEL1}:
        return "Level1"
    return ""


def find_col(df, key, override=None):
    if override:
        return override
    lower = {c.lower().strip(): c for c in df.columns}
    for cand in COLS[key]:
        if cand in lower:
            return lower[cand]
    return None


def read_records(path):
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path, dtype=str).fillna("")
    return pd.read_csv(path, dtype=str, sep=None, engine="python").fillna("")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", help="file bản ghi (CSV/XLSX); bỏ trống thì chỉ xuất whitelist")
    ap.add_argument("--sjr", required=True)
    ap.add_argument("--abdc", required=True)
    ap.add_argument("--out", default="out")
    for k in COLS:
        ap.add_argument(f"--col-{k}", help=f"tên cột {k} nếu không tự nhận ra")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    sjr_df, sjr_issn, sjr_title = load_sjr(a.sjr)
    abdc_df, rating, abdc_issn, abdc_title = load_abdc(a.abdc)

    # Whitelist: hợp của ba danh sách.
    rows = {}
    for _, r in sjr_df.iterrows():
        q = r["SJR Best Quartile"].strip()
        if q in ("Q1", "Q2"):
            rows[norm_title(r["Title"])] = {"Journal": r["Title"], "ISSN": r["Issn"], "SJR_Q": q, "SJR_Type": r["Type"]}
    for _, r in abdc_df.iterrows():
        rk = str(r[rating]).strip()
        if rk in ("A*", "A", "B"):
            k = norm_title(r["Journal Title"])
            rows.setdefault(k, {"Journal": str(r["Journal Title"]).strip(),
                                "ISSN": f"{r.get('ISSN', '')}, {r.get('ISSNOnline', '')}".replace("\t", "")})
            rows[k]["ABDC_2025"] = rk
    for name in LEVEL1_ELITE + LEVEL1:
        rows.setdefault(norm_title(name), {"Journal": name})["Level1"] = level1_of(name)
    wl = pd.DataFrame(rows.values()).reindex(columns=["Journal", "ISSN", "Level1", "ABDC_2025", "SJR_Q", "SJR_Type"]).fillna("")
    wl.sort_values("Journal").to_csv(os.path.join(a.out, "whitelist.csv"), index=False, encoding="utf-8-sig")
    print(f"whitelist.csv: {len(wl)} tạp chí đạt IC7")

    if not a.records:
        return
    df = read_records(a.records)
    c = {k: find_col(df, k, getattr(a, f"col_{k}")) for k in COLS}
    if not c["journal"] and not c["issn"]:
        sys.exit(f"Không tìm thấy cột tạp chí/ISSN. Các cột hiện có: {list(df.columns)}. Dùng --col-journal / --col-issn.")
    print("Cột nhận diện:", {k: v for k, v in c.items() if v})

    out = []
    for _, r in df.iterrows():
        ids = issns(" ".join(str(r[c[k]]) for k in ("issn", "eissn") if c[k]))
        jt = norm_title(r[c["journal"]]) if c["journal"] else ""
        abdc = next((abdc_issn[i] for i in ids if i in abdc_issn), abdc_title.get(jt, ""))
        sq, stype, areas, cats = next((sjr_issn[i] for i in ids if i in sjr_issn), sjr_title.get(jt, ("", "", "", "")))
        lv = level1_of(r[c["journal"]]) if c["journal"] else ""
        found = bool(abdc or sq or lv)
        ok = lv or abdc in ("A*", "A", "B") or sq in ("Q1", "Q2")
        biz = biz_of(bool(abdc or lv), areas, cats)
        out.append({"Level1": lv, "ABDC_2025": abdc, "SJR_Q": sq, "SJR_Type": stype, "SJR_Areas": areas,
                    "IC7": "Đạt" if ok else ("Không đạt" if found else "Không tìm thấy"),
                    "Biz": biz, "EC10": "Loại" if biz == "N" else "",
                    "Tag": "social-mkt" if biz == "?" else ""})
    res = pd.concat([df.reset_index(drop=True), pd.DataFrame(out)], axis=1)
    if not c["id"]:
        res.insert(0, "ID", [f"{i + 1:03d}" for i in range(len(res))])
        c["id"] = "ID"
    res.to_csv(os.path.join(a.out, "records_ranked.csv"), index=False, encoding="utf-8-sig")
    print(res["IC7"].value_counts().to_string())
    print(res["Biz"].value_counts().to_string())

    review = res[(res["IC7"] != "Đạt") | ~res["Biz"].isin(["Y", "?"])]
    review.to_csv(os.path.join(a.out, "final_review.csv"), index=False, encoding="utf-8-sig")
    print(f"final_review.csv: {len(review)} bài cần kiểm tay (IC7 chưa đạt hoặc Biz = N / Không xác định)")

if __name__ == "__main__":
    main()
