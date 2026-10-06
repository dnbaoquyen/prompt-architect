# Sàng lọc bài báo SLR bằng NotebookLM

Quy trình gồm 2 giai đoạn:

| Giai đoạn | Ai làm | Tiêu chí |
| :--- | :--- | :--- |
| **1. Sàng lọc nội dung** (TiAb → FT) | NotebookLM + người kiểm tra | 12 mã loại (mọi mã trừ IC7) và nhãn chọn |
| **2. Lọc hạng tạp chí (IC7)** | Script [`tools/rank_journals.py`](tools/rank_journals.py) + người kiểm tra | Level 1 / ABDC A\*–A–B / SJR Q1–Q2 |

NotebookLM **không xét hạng tạp chí**. IC7 chỉ áp dụng cho danh sách cuối, sau khi đã chốt INCLUDE theo nội dung (mục E).

Bộ tài liệu gồm:

1. Hướng dẫn chuẩn bị nguồn và cấu hình notebook (mục A–C).
2. Custom instructions để dán vào Settings: [`custom-instructions.txt`](custom-instructions.txt), khoảng 9.300 ký tự (giới hạn của NotebookLM là 10.000).
3. Các prompt chạy từng lượt (mục D).
4. Bước lọc tạp chí cuối cùng (mục E).

---

## A. Chuẩn bị nguồn (sources)

NotebookLM tìm kiếm theo đoạn văn, nên bảng tính lớn dễ bị bỏ sót dòng. Vì vậy nên chia nhỏ dữ liệu.

**Vòng tiêu đề–tóm tắt (TiAb)**

Dùng [`tools/make_batches.py`](tools/make_batches.py) để chia file 32 (đã gộp nhóm A và B) thành các lô 20 bài:

```bash
pip install pandas openpyxl
python3 tools/make_batches.py --records file32.csv --out out/ --batch-size 20
```

Mỗi bài trong lô là một khối có nhãn trường rõ ràng, để mô hình không phải đoán:

```
=== ID: 017 ===
Title: ...
Authors: ... | Year: ... | DOI: ...
Journal: ... | Document type: Article
Biz: Y            (Y / N / ?)
Group: A          (A / B)
Retraction: No
Abstract: ...
```

- Script tự nhận tên cột theo kiểu xuất của Rayyan, Scopus và WoS. Nếu không nhận ra, dùng `--col-title`, `--col-abstract`, `--col-biz`…
- File không có cột ID thì script tự đánh số `001, 002, …`. **Giữ nguyên ID này** suốt quy trình, đến bước lọc tạp chí.
- Không có cột Biz thì NotebookLM bỏ qua EC10 và nhãn social-mkt.
- Tải các file `out/batches/Batch_XX_*.txt` lên NotebookLM.

**Vòng toàn văn (FT)**

- Mỗi PDF là một nguồn, đặt tên `ID_TacGia_Nam.pdf` (vd. `017_Nguyen_2024.pdf`) để ID xuất hiện trong trích dẫn.
- PDF phải có lớp chữ. Nếu là bản scan, chạy OCR trước khi tải lên.

> Giới hạn nguồn: bản miễn phí 50 nguồn/notebook, bản Pro 300. Nếu nhiều hơn, chia thành nhiều notebook.

## B. Cấu hình Settings

Custom instructions áp dụng cho cả notebook, nên **tạo 2 notebook riêng**: một cho TiAb, một cho FT. Hai notebook dùng cùng một bộ instructions; prompt từng lượt sẽ báo đang ở vòng nào.

1. Mở notebook. Trong khung **Chat**, bấm biểu tượng cấu hình (⚙ / *Configure notebook*). Tên mục có thể hơi khác tùy phiên bản.
2. Ở **Conversational goal / Define your conversational style**, chọn **Custom**.
3. Dán toàn bộ nội dung [`custom-instructions.txt`](custom-instructions.txt) vào ô Custom.
4. Ở **Response length**, chọn **Longer** để bảng nhiều dòng không bị cắt.
5. Bấm **Save**, mở chat mới, rồi chạy **D0** để kiểm tra instructions không bị cắt.

Khi chạy:

- Ở cột Sources, **chỉ tick lô hoặc PDF đang sàng lọc**.
- Mỗi lượt tối đa **20 bài** (TiAb) hoặc **1 bài** (FT). Câu trả lời dài dễ bị cắt hoặc thiếu dòng.
- Kết quả dùng được thì bấm **Save to note**, rồi copy bảng sang Google Sheets (dán bảng Markdown vào Sheets sẽ tự tách cột).

## C. Kiểm soát chất lượng

1. **Pilot**: tự mã hóa trước 20–30 bài, cho NotebookLM chạy (D1 + D4b), rồi so sánh từng bài. Chỗ nào lệch thì sửa câu chữ tiêu chí và chạy lại. Ghi lại tỷ lệ đồng thuận để báo cáo.
2. **Mọi quyết định EXCLUDE ở vòng FT** và mọi dòng trong mục "CẦN NGƯỜI KIỂM TRA" phải được người đọc lại.
3. Lưu phiên bản instructions và ngày chạy, để báo cáo minh bạch việc dùng AI trong PRISMA.
4. Câu trả lời có thể khác nhau giữa các lần chạy. Với bài khó, chạy D3.

### Các giả định trong instructions (sửa nếu không đúng ý bạn)

**Quy trình và thứ tự mã**
- Thứ tự xét loại theo danh sách gốc, **bỏ IC7**. Còn lại 12 mã, đánh số `01–12`; mã có số nhỏ nhất thỏa là **mã loại chính**.
- Thêm quyết định **UNCERTAIN** cho vòng TiAb (nghi ngờ thì giữ).
- EC1: giữ bản đầy đủ nhất trong các bản trùng.

**Thực phẩm**
- **4 cặp thực phẩm** chỉ tính khi sản phẩm được định vị thay đúng một vế nguyên bản. Phô mai, sữa chua và đồ uống lên men thực vật không tính là "sữa thực vật".
- Thực phẩm thuộc danh sách EC7 thì dùng EC7, không dùng IC2.
- Thực phẩm ngoài 4 cặp và ngoài EC7 thì dùng IC2.
- **EC6** gồm cả bài thực phẩm chỉ đo tiêu thụ/dinh dưỡng.
- **TierF-core** "so sánh với nguyên bản" chỉ tính khi so sánh trên PI/WTP/lựa chọn. So sánh chỉ về cảm quan thì thuộc EC6 (Q6).
- **A-TF** khác TierF ở chỗ có kích thích truyền thông (nhãn, thông điệp, quảng cáo, người chứng thực).

**Biến đo và RQ**
- **PI theo nghĩa hẹp**: ý định mua/chọn sản phẩm, hoặc lựa chọn trong thực nghiệm/dữ liệu bán hàng. Mức tiêu thụ tự báo cáo không phải PI, nên bài thực phẩm chỉ đo tiêu thụ thuộc EC6.
- **Kết quả đo trong phạm vi**: WTP, PI, độ tin cậy/niềm tin, tính chân thực, cảm nhận đổi mới, thái độ với quảng cáo/thương hiệu. Bài đo ít nhất một biến này là "trong phạm vi".
- **RQ3** không tính realism, anthropomorphism, attractiveness.
- Bài có người chứng thực/nội dung tổng hợp nhưng không đo biến nào trong phạm vi (chỉ continued use, engagement, well-being…) vẫn gắn RQ1, nhưng tin cậy tối đa TB.

**Phân định các mã khác**
- **EC2** gồm cả avatar giống người chỉ đóng vai trợ lý mua sắm/CSKH.
- **IC1** gồm bài khái niệm/triết học, mẫu là nhân viên/nhà sản xuất, và bài chỉ phân tích đầu ra của AI.
- **EC5**: nghiên cứu hỗn hợp có phần định lượng trên người tiêu dùng thì **không** bị loại.
- "AI vô hình" (IC2) là AI chạy ngầm, không hiện ra thành nội dung hay nhân vật.

---

## D. Prompt chạy từng lượt

### D0. Kiểm tra cấu hình (chạy 1 lần khi mở notebook)

```
Trước khi sàng lọc, hãy tóm tắt lại bằng 1 bảng: thứ tự 12 mã loại (01–12), điều kiện đặc biệt của EC10, EC9, EC5, sự khác nhau giữa A-TF và TierF, và 4 cặp thực phẩm mục tiêu. Xác nhận bạn có xét hạng tạp chí hay không. Không sàng lọc bài nào.
```

Nếu tóm tắt sai, thiếu, hoặc nói có xét hạng tạp chí, nghĩa là custom instructions chưa được lưu hoặc bị cắt.

### D1. Sàng lọc vòng tiêu đề–tóm tắt

```
VÒNG: TIÊU ĐỀ–TÓM TẮT (TiAb)
Nguồn: [Batch_01_ID001-020]
Phạm vi: tất cả các bài trong nguồn này (tối đa 20 bài).

Sàng lọc từng bài theo đúng Bước 1 (xét 12 mã theo thứ tự) và Bước 2 (gắn nhãn) trong hướng dẫn của notebook.
- Không xét hạng tạp chí.
- Cột Tier F ghi "–" (vòng này chưa gắn).
- Nghi ngờ thì chọn UNCERTAIN, không EXCLUDE.
- Lý do phải trích dẫn câu trong tóm tắt hoặc metadata.
- Mã loại chính phải là mã có số nhỏ nhất trong các mã thỏa; tự kiểm tra trước khi xuất.
- Không đánh "Cao" mặc định: áp dụng đúng thang ĐỘ TIN CẬY.
```

### D2. Sàng lọc vòng toàn văn (mỗi lượt 1 PDF)

```
VÒNG: TOÀN VĂN (FT)
Nguồn: [017_Nguyen_2024.pdf] (chỉ dùng nguồn này).

1. Trích xuất ngắn (có trích dẫn trang/đoạn): loại tài liệu, thiết kế nghiên cứu, mẫu (ai, bao nhiêu), loại AI/người chứng thực/sản phẩm, thực phẩm thuộc cặp nào (nếu có), biến phụ thuộc (WTP, PI, choice, độ tin cậy, tính chân thực, thái độ, cảm quan), có công khai AI hay không, loại dữ liệu.
2. Dựa trên phần trích xuất, áp dụng Bước 1 và Bước 2. Quyết định chỉ là INCLUDE hoặc EXCLUDE. Không xét hạng tạp chí.
3. Nếu thuộc TierF hoặc A-TF, gắn TierF-core hoặc TierF-context và nêu căn cứ.
4. Xuất bảng 1 dòng theo định dạng chuẩn.
```

### D3. Kiểm tra lại các bài UNCERTAIN hoặc bị nghi sai

```
Xem lại các bài ID: [005, 012, 019].
Với từng bài:
1. Nêu quyết định trước đó và mã/nhãn đã gắn.
2. Đặt 3 câu hỏi kiểm chứng cho chính quyết định đó (vd. "Mẫu có thật là người tiêu dùng không?", "Biến đo có phải WTP/PI không?", "Có mã loại nào số nhỏ hơn bị bỏ qua không?").
3. Trả lời từng câu chỉ bằng trích dẫn từ nguồn.
4. Đưa ra quyết định cuối, ghi rõ "GIỮ NGUYÊN" hoặc "THAY ĐỔI: ... vì ...".
Xuất lại bảng theo định dạng chuẩn cho các bài này.
```

### D4. Kiểm tra trùng lặp (EC1) trong một lô

```
Trong các nguồn đang chọn, tìm các cặp bài có cùng DOI, tiêu đề gần giống nhau, hoặc cùng tác giả + cùng mô tả mẫu/dữ liệu.
Xuất bảng: | ID giữ | ID loại (EC1) | Căn cứ trùng | Tin cậy |
Không kết luận trùng nếu chỉ giống chủ đề.
```

### D4b. Rà lỗi bảng vừa xuất (chạy ngay sau D1)

```
Rà lại bảng vừa xuất, KHÔNG sàng lọc lại từ đầu. Liệt kê và sửa các dòng vi phạm:
(a) mã phụ có số nhỏ hơn mã chính;
(b) có EC10 hoặc social-mkt khi nguồn không có trường Biz;
(c) có gắn PI cho biến không phải ý định mua/chọn;
(d) có RQ2-fit mà không đo/thao tác fit và không so sánh theo loại sản phẩm;
(e) TierF mà bài có nhãn, thông điệp hoặc người chứng thực (phải là A-TF);
(f) loại hoặc ghi chú vì tạp chí/hạng tạp chí;
(g) ID trống;
(h) ghi "kết quả ngoài phạm vi" dù bài có đo độ tin cậy/niềm tin, tính chân thực, thái độ, cảm nhận đổi mới, PI hoặc WTP;
(i) gắn PI hoặc INCLUDE cho bài thực phẩm chỉ đo mức tiêu thụ tự báo cáo (phải là 11-EC6);
(j) gắn RQ3 cho realism, anthropomorphism, attractiveness;
(k) dùng 08-EC3 cho bài không nói về deepfake/phát hiện nội dung AI;
(l) dùng 11-EC6 cho thực phẩm ngoài 4 cặp.
Xuất bảng: | ID | Lỗi | Trước | Sau |. Sau đó xuất lại bảng đầy đủ chỉ cho các dòng đã sửa.
```

### D5. Tổng hợp cuối lô

```
Từ các bảng sàng lọc trong cuộc trò chuyện này, tổng hợp:
1. Số bài INCLUDE / EXCLUDE / UNCERTAIN.
2. Số bài theo từng mã loại chính (phục vụ sơ đồ PRISMA).
3. Số bài theo từng nhánh (A-T1, A-T2, A-T3, A-Disc, A-TF, TierF, B-Meta) và theo RQ.
4. Danh sách ID gắn snowball và context.
5. Danh sách ID INCLUDE (để chuyển sang bước lọc tạp chí).
Chỉ dùng số liệu đã có trong các bảng, không sàng lọc lại.
```

---

## E. Bước cuối: lọc hạng tạp chí (IC7)

Làm sau khi đã chốt danh sách INCLUDE ở vòng FT. Bước này không dùng NotebookLM.

1. Xuất danh sách INCLUDE ra CSV/XLSX. File cần có các cột ID, tên tạp chí, và ISSN nếu có.
2. Chạy:

   ```bash
   python3 tools/rank_journals.py \
     --records danh_sach_cuoi.csv \
     --sjr scimagojr_2025_1.csv \
     --abdc ABDC-JQL-2025-v3-210926.xlsx \
     --out out/
   ```

3. Kết quả:
   - `out/records_ranked.csv`: danh sách cuối kèm các cột `Level1`, `ABDC_2025`, `SJR_Q`, `IC7` (Đạt / Không đạt / Không tìm thấy).
   - `out/ic7_review.csv`: chỉ những bài **Không đạt** hoặc **Không tìm thấy**. Kiểm tay những bài này, vì tên tạp chí có thể viết khác hoặc tạp chí có thể đã đổi tên.
   - `out/whitelist.csv`: toàn bộ khoảng 17.800 tạp chí đạt IC7, để tra thủ công.

IC7 **đạt** khi tạp chí thuộc ít nhất một danh sách: Marketing Level 1 (gồm Elite), ABDC JQL 2025 hạng A\*/A/B, hoặc SJR 2025 Best Quartile Q1/Q2. Script khớp theo ISSN trước, sau đó theo tên tạp chí.

Ghi chú:
- Cả 20 tạp chí Level 1 đều là SJR Q1, nên danh sách Level 1 không làm thay đổi kết quả.
- Trong PDF Level 1, "JAMS" được hiểu là *Journal of the Academy of Marketing Science*, và "Journal of Services Research" là *Journal of Service Research*.
- PRISMA: ghi số bài loại do IC7 thành một bước riêng, sau sàng lọc toàn văn.
- Dữ liệu SJR/ABDC không được đưa lên repo. Thư mục `out/` đã được loại khỏi git.

---

## F. Nhật ký hiệu chỉnh

### Pilot 1 (50 bài, vòng TiAb)

| Vấn đề quan sát | Ví dụ | Sửa trong instructions |
| :--- | :--- | :--- |
| Cột ID trống; mục kiểm tra có 50 dòng `****` | toàn bộ lô | Quy tắc ID dự phòng `STT-TácGiả-Năm`; `make_batches.py` tự đánh ID |
| Gắn "IC7? cần kiểm tra" cho mọi bài | toàn bộ lô | IC7 bị bỏ khỏi NotebookLM, chuyển sang bước cuối (mục E) |
| Sai thứ tự mã chính/phụ | *Ethical Problems…* (IC2 > IC1); *Pseudo-Confidence…* (IC2 > EC2); *Stakeholder perspectives…* (EC5 > EC10) | Đánh số mã `01–12`, bắt buộc tự kiểm tra |
| Dùng EC10 khi nguồn không có Biz | *Frontal facial analysis…*, *Yeast strains…* | Không có Biz thì cấm EC10/social-mkt |
| Gắn PI quá rộng | continued use, information adoption, usage intention, engagement, travel intention | Định nghĩa PI hẹp |
| Avatar trợ lý mua sắm được xếp A-T2 | *Demystifying the Impact of Homophily…* | EC2 gồm avatar trợ lý không chứng thực |
| Nhãn thực vật xếp TierF thay vì A-TF | *From Niche to Norm…* | A-TF = có kích thích truyền thông (kể cả nhãn) |
| RQ2-fit cho điều tiết hedonic/utilitarian | *The power of facial allure…* | Đúng theo định nghĩa RQ2 chính thức; giữ nguyên |
| Tin cậy đều là "Cao" | toàn bộ lô | Thêm thang Cao/TB/Thấp và giới hạn trần |
| Tự suy ra "4 cặp thực phẩm mục tiêu" | pasta, cream cheese, fava spread | Thêm 4 cặp chính thức; EC7 ưu tiên hơn IC2 với thực phẩm |
| RQ chưa có định nghĩa, RQ1 cho mọi bài | toàn bộ lô | Thêm câu hỏi tổng hợp, phạm vi kết quả đo, định nghĩa RQ1–RQ4 |

### Pilot 2 (cùng 50 bài, vòng TiAb, sau khi bỏ IC7)

Đã khắc phục so với pilot 1: ID đầy đủ; thứ tự mã đúng; không còn dùng EC10 khi thiếu Biz; PI hẹp hơn; R0017 sang EC2; R0029 sang A-TF; độ tin cậy có phân tầng; mục kiểm tra chỉ còn 8 bài thật sự cần xem.

Người dùng đổi cột tiêu đề thành **Tiêu đề gốc** (đã cập nhật vào instructions).

| Vấn đề còn lại | Ví dụ | Sửa trong instructions |
| :--- | :--- | :--- |
| Coi mức tiêu thụ tự báo cáo là PI, INCLUDE bài lẽ ra phải là EC6 | R0028 *The meat of the matter…* | PI loại trừ tiêu thụ tự báo cáo; EC6 nêu rõ "tiêu thụ tự báo cáo" |
| Ghi "ngoài phạm vi" dù bài đo authenticity/trust/credibility | R0025, R0027, R0004 | Thêm danh mục KẾT QUẢ ĐO TRONG PHẠM VI có từ đồng nghĩa |
| Gắn RQ3 cho form realism | R0035 | RQ3 loại trừ realism, anthropomorphism, attractiveness |
| Gắn mã phụ EC3 cho bài không về deepfake | R0001 | EC3 chỉ dùng khi bài nói về deepfake/phát hiện nội dung AI |
| Gắn EC6 cho thực phẩm ngoài 4 cặp | R0002 | EC6 chỉ áp dụng cho thực phẩm thuộc 4 cặp |
| Đồ uống thực vật chưa rõ định vị nhưng chấm IC2 "Cao" | R0002 | Giữ quy tắc "không rõ định vị → UNCERTAIN"; D4b kiểm tra |
