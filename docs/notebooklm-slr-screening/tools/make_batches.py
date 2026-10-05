#!/usr/bin/env python3
"""Xuất file bản ghi (CSV/XLSX) thành các lô khối văn bản để tải lên NotebookLM.

Lô KHÔNG chứa hạng tạp chí: IC7 được lọc riêng ở bước cuối bằng rank_journals.py.

Ví dụ:
  python3 make_batches.py --records file32.csv --out out/ --batch-size 20

Kết quả:
  out/batches/Batch_XX_IDaaa-bbb.txt
"""
import argparse
import os

from rank_journals import COLS, find_col, read_records


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", required=True, help="file bản ghi (CSV/XLSX)")
    ap.add_argument("--out", default="out")
    ap.add_argument("--batch-size", type=int, default=20)
    for k in COLS:
        ap.add_argument(f"--col-{k}", help=f"tên cột {k} nếu không tự nhận ra")
    a = ap.parse_args()

    df = read_records(a.records)
    c = {k: find_col(df, k, getattr(a, f"col_{k}")) for k in COLS}
    print("Cột nhận diện:", {k: v for k, v in c.items() if v})
    if not c["title"]:
        raise SystemExit(f"Không tìm thấy cột tiêu đề. Các cột hiện có: {list(df.columns)}. Dùng --col-title.")
    if not c["id"]:
        df.insert(0, "ID", [f"{i + 1:03d}" for i in range(len(df))])
        c["id"] = "ID"
        print("File không có cột ID: đã tự đánh số 001, 002, …")

    bdir = os.path.join(a.out, "batches")
    os.makedirs(bdir, exist_ok=True)
    get = lambda r, k: str(r[c[k]]).strip() if c[k] else ""
    for b in range(0, len(df), a.batch_size):
        part = df.iloc[b:b + a.batch_size]
        first, last = get(part.iloc[0], "id"), get(part.iloc[-1], "id")
        name = f"Batch_{b // a.batch_size + 1:02d}_ID{first}-{last}.txt"
        with open(os.path.join(bdir, name), "w", encoding="utf-8") as f:
            for _, r in part.iterrows():
                f.write(
                    f"=== ID: {get(r, 'id')} ===\n"
                    f"Title: {get(r, 'title')}\n"
                    f"Authors: {get(r, 'authors')} | Year: {get(r, 'year')} | DOI: {get(r, 'doi')}\n"
                    f"Journal: {get(r, 'journal')} | Document type: {get(r, 'type')}\n"
                    f"Biz: {get(r, 'biz') or 'không có dữ liệu'}\n"
                    f"Group: {get(r, 'group') or '-'}\n"
                    f"Retraction: {get(r, 'retraction') or '-'}\n"
                    f"Abstract: {get(r, 'abstract') or '(không có tóm tắt)'}\n\n"
                )
    print(f"Đã xuất {len(os.listdir(bdir))} lô vào {bdir}")


if __name__ == "__main__":
    main()
