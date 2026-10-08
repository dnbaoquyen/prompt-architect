# Sàng lọc bài báo SLR bằng NotebookLM

Quy trình gồm 2 giai đoạn:

| Giai đoạn | Ai làm | Tiêu chí |
| :--- | :--- | :--- |
| **1. Sàng lọc nội dung** (TiAb → FT) | NotebookLM + người kiểm tra | 11 mã loại (mọi mã trừ IC7 và EC10) và nhãn chọn |
| **2. Lọc tạp chí** (IC7 + EC10) | Script [`tools/rank_journals.py`](tools/rank_journals.py) + người kiểm tra | Hạng: Level 1 / ABDC A\*–A–B / SJR Q1–Q2. Lĩnh vực: cờ Biz suy từ lĩnh vực tạp chí |

NotebookLM **không xét hạng tạp chí và lĩnh vực kinh doanh**. IC7, EC10 và nhãn social-mkt chỉ áp dụng cho danh sách cuối, sau khi đã chốt INCLUDE theo nội dung (mục E).

Bộ tài liệu gồm:

1. Hướng dẫn chuẩn bị nguồn và cấu hình notebook (mục A–C).
2. Custom instructions để dán vào Settings: [`custom-instructions.txt`](custom-instructions.txt), khoảng 6.900 ký tự, bản sàng lọc lại theo 5 bước (giới hạn của NotebookLM là 10.000). Đếm bằng `python3 -c "print(len(open('custom-instructions.txt',encoding='utf-8').read()))"`; không dùng `wc -m` vì lệnh này có thể đếm byte với tiếng Việt.
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
Group: A          (A / B)
Retraction: No
Abstract: ...
```

- Script tự nhận tên cột theo kiểu xuất của Rayyan, Scopus và WoS. Nếu không nhận ra, dùng `--col-title`, `--col-abstract`…
- File không có cột ID thì script tự đánh số `001, 002, …`. **Giữ nguyên ID này** suốt quy trình, đến bước lọc tạp chí.
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
5. Bấm **Save**. **Xóa lịch sử chat** (menu ⋮ của khung Chat → *Delete chat history*), để notebook không bắt chước định dạng của các bảng cũ. Sau đó chạy **D0** để kiểm tra.
   - Mỗi lần cập nhật instructions: xóa hết nội dung cũ trong ô Custom rồi mới dán bản mới, không dán nối tiếp.

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
- Thứ tự xét loại theo danh sách gốc, **bỏ IC7 và EC10** (chuyển xuống bước cuối), **đổi chỗ EC7 lên trước IC2**. Còn lại 11 mã, đánh số `01–11`; mã có số nhỏ nhất thỏa là **mã loại chính**.
- Bài thuộc bối cảnh phi marketing (y tế, giáo dục, tài chính/đầu tư, tuyển dụng, chính sách công/xã hội) được ghi "Lĩnh vực: …" trong cột Lý do, để đối chiếu với cờ Biz ở bước cuối. Du lịch/điểm đến, bán lẻ, dịch vụ, livestream và thực phẩm được coi là marketing.
- Thêm quyết định **UNCERTAIN** cho vòng TiAb (nghi ngờ thì giữ).
- EC1: giữ bản đầy đủ nhất trong các bản trùng.

**Thực phẩm**
- **4 cặp thực phẩm** chỉ tính khi sản phẩm được định vị thay đúng một vế nguyên bản. Đồ uống thực vật (plant-based beverage/milk alternative), **kể cả loại lên men**, tính là cặp 2 "sữa thực vật" nếu không được gọi là yogurt/kefir. Phô mai và sữa chua/yogurt/kefir thực vật không tính.
- **EC7 được đặt trước IC2** trong thứ tự (08-EC7, 09-IC2), để quy tắc "thực phẩm thuộc EC7 thì dùng EC7" được áp dụng máy móc theo thứ tự. Đổi chỗ này không làm thay đổi quyết định loại/chọn nào.
- Thực phẩm ngoài 4 cặp và ngoài EC7 thì dùng IC2.
- **EC6** gồm cả bài thực phẩm chỉ đo tiêu thụ tự báo cáo/dinh dưỡng. Bài chỉ đo tiêu thụ tự báo cáo hoặc yếu tố quyết định tiêu thụ được gắn thêm `context`, để vẫn dùng được trong phần dẫn nhập và thảo luận.
- **TierF-core** "so sánh với nguyên bản" chỉ tính khi so sánh trên PI/WTP/lựa chọn. So sánh chỉ về cảm quan thì thuộc EC6 (Q6).
- **A-TF** khác TierF ở chỗ có kích thích truyền thông (nhãn, thông điệp, quảng cáo, người chứng thực).

**Biến đo và RQ**
- **PI theo nghĩa hẹp**: ý định mua/chọn sản phẩm, hoặc dữ liệu mua/chọn **khách quan** (lựa chọn trong thực nghiệm, lựa chọn có khuyến khích, scanner, dữ liệu bán hàng). Mức tiêu thụ **tự báo cáo** không phải PI.
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

> **Đang sàng lọc lại 209 bài?** Dùng các prompt ở **mục F** (bảng 13 cột, có cột Bước). Các prompt D0–D5 bên dưới viết cho bản instructions 12 cột trước đây; D2–D5 vẫn dùng được.

### D0. Kiểm tra cấu hình (chạy 1 lần khi mở notebook)

```
Trước khi sàng lọc, hãy tóm tắt lại bằng 1 bảng: thứ tự 11 mã loại (01–11), điều kiện đặc biệt của EC9, EC5, EC6, sự khác nhau giữa A-TF và TierF, và 4 cặp thực phẩm mục tiêu. Xác nhận bạn có xét hạng tạp chí và lĩnh vực kinh doanh (EC10) hay không. Không sàng lọc bài nào.
```

Kết quả đúng phải liệt kê **11 mã, từ 01-Retracted đến 11-EC5**, với **05-IC1**, **08-EC7**, **09-IC2** và **10-EC6**. Nếu thấy 12 mã, thấy EC10, hoặc thấy notebook nói có xét hạng tạp chí, nghĩa là custom instructions chưa được lưu hoặc bị cắt.

### D1. Sàng lọc vòng tiêu đề–tóm tắt

```
VÒNG: TIÊU ĐỀ–TÓM TẮT (TiAb)
Nguồn: [Batch_01_ID001-020]
Phạm vi: tất cả các bài trong nguồn này (tối đa 20 bài).

Sàng lọc từng bài theo đúng Bước 1 (xét 11 mã theo thứ tự) và Bước 2 (gắn nhãn) trong hướng dẫn của notebook.
- Không xét hạng tạp chí, không dùng EC10, không gắn social-mkt.
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
(b) có dùng EC10 hoặc gắn social-mkt (cả hai đã chuyển xuống bước cuối);
(c) có gắn PI cho biến không phải ý định mua/chọn;
(d) có RQ2-fit mà không đo/thao tác fit và không so sánh theo loại sản phẩm;
(e) TierF mà bài có nhãn, thông điệp hoặc người chứng thực (phải là A-TF);
(f) loại hoặc ghi chú vì tạp chí/hạng tạp chí;
(g) ID trống;
(h) ghi "kết quả ngoài phạm vi" dù bài có đo độ tin cậy/niềm tin, tính chân thực, thái độ, cảm nhận đổi mới, PI hoặc WTP;
(i) gắn PI hoặc INCLUDE cho bài thực phẩm chỉ đo mức tiêu thụ tự báo cáo (phải là 10-EC6 + context);
(j) gắn RQ3 cho realism, anthropomorphism, attractiveness;
(k) dùng 07-EC3 cho bài không nói về deepfake/phát hiện nội dung AI;
(l) dùng 10-EC6 cho thực phẩm ngoài 4 cặp;
(m) bài INCLUDE/UNCERTAIN phi marketing nhưng không ghi "Lĩnh vực: …"; hoặc bài EXCLUDE lại có ghi "Lĩnh vực: …" (phải xóa);
(n) bài không có người tham gia (phòng thí nghiệm, thuật toán, mô hình) mà mã chính không phải 05-IC1;
(o) dùng IC2 cho sản phẩm có thành phần/chức năng thay thế thuộc EC7 (phải là 08-EC7);
(p) có mã số 12, nhắc tới EC10/Biz, hoặc ghi 08-IC2 / 09-EC7 (dấu hiệu instructions cũ);
(q) gắn PI cho "acceptance intention" hoặc ý định sử dụng;
(r) EC5 (chính hoặc phụ) mà không gắn context;
(s) Lý do không có trích dẫn nguyên văn trong ngoặc kép;
(t) ghi "Lĩnh vực: …" cho du lịch/điểm đến, bán lẻ, dịch vụ, livestream, thực phẩm;
(u) dòng có số ô khác 12 (lệch cột);
(v) gắn A-Disc/disclosure hoặc RQ1 cho nhãn thực phẩm không liên quan AI;
(w) dùng IC2 làm mã chính chỉ vì bài thuộc lĩnh vực phi marketing.
Chỉ sửa khi lỗi có căn cứ trong nguồn. Không tự suy ra lĩnh vực hay thông tin không có trong tóm tắt.
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

## E. Bước cuối: lọc tạp chí (IC7 + EC10)

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
   - `out/records_ranked.csv`: danh sách cuối, thêm các cột:
     - `Level1`, `ABDC_2025`, `SJR_Q`, `SJR_Areas`;
     - `IC7` (Đạt / Không đạt / Không tìm thấy);
     - `Biz` (Y / ? / N / Không xác định), `EC10` (Loại khi Biz = N), `Tag` (social-mkt khi Biz = ?).
   - `out/final_review.csv`: chỉ những bài cần kiểm tay, tức IC7 chưa đạt, hoặc Biz là N / Không xác định.
   - `out/whitelist.csv`: toàn bộ khoảng 17.800 tạp chí đạt IC7, để tra thủ công.

**IC7 đạt** khi tạp chí thuộc ít nhất một danh sách: Marketing Level 1 (gồm Elite), ABDC JQL 2025 hạng A\*/A/B, hoặc SJR 2025 Best Quartile Q1/Q2.

**Cờ Biz** được suy ra từ lĩnh vực tạp chí:

| Biz | Điều kiện | Xử lý |
| :--- | :--- | :--- |
| Y | Có trong ABDC hoặc Level 1, hoặc SJR Areas có Business / Economics / Decision Sciences | Giữ |
| ? | SJR Areas có Psychology / Social Sciences / Arts and Humanities / Multidisciplinary, hoặc Categories có Food Science, Nutrition, Communication, Tourism, Human-Computer Interaction | Giữ, gắn `social-mkt` |
| N | Tìm thấy tạp chí nhưng không thuộc các nhóm trên (vd. y khoa thuần, nha khoa, kỹ thuật) | EC10, kiểm tay trước khi loại |
| Không xác định | Không tìm thấy tạp chí | Kiểm tay |

Ghi chú:
- **Food Science buộc phải xếp `?`.** Phần lớn bài TierF cốt lõi đăng trên tạp chí khoa học thực phẩm (*Food Quality and Preference*, *Appetite*, *Foods*). Nếu xếp N, các bài này sẽ bị loại oan.
- Cờ Biz đánh giá theo **tạp chí**, không theo bài. Hãy đối chiếu với ghi chú "Lĩnh vực: …" mà NotebookLM để lại trong cột Lý do. Ví dụ: một bài quảng cáo y tế đăng trên tạp chí truyền thông sẽ có Biz = ?.
- Script khớp theo ISSN trước, sau đó theo tên tạp chí.
- Cả 20 tạp chí Level 1 đều là SJR Q1, nên danh sách Level 1 không làm thay đổi kết quả IC7.
- Trong PDF Level 1, "JAMS" được hiểu là *Journal of the Academy of Marketing Science*, và "Journal of Services Research" là *Journal of Service Research*.
- PRISMA: ghi số bài loại do IC7 và do EC10 thành các bước riêng, sau sàng lọc toàn văn.
- Dữ liệu SJR/ABDC không được đưa lên repo. Thư mục `out/` đã được loại khỏi git.

---

## F. Sàng lọc lại 209 bài (theo hướng dẫn 5 bước)

**Bối cảnh.** Lần sàng lọc trước giữ 155/209 bài, trong đó 61 bài là TierF. Ba người sàng lọc hiểu khác nhau ở một số điểm. Lần này **không có tiêu chí mới**: dùng đúng bộ quy tắc trong ghi nhớ, nhưng áp chặt theo trình tự 5 bước. [`custom-instructions.txt`](custom-instructions.txt) đã được viết lại theo trình tự này (khoảng 6.900 ký tự).

**Thay đổi so với bản instructions sau Pilot 5**

| Điểm | Trước | Nay (theo hướng dẫn 5 bước) |
| :--- | :--- | :--- |
| Cấu trúc | Danh sách 11 mã | Cây quyết định 5 bước; thêm cột **Bước** (bước dừng) |
| Trứng thực vật (kể cả chất thay lòng trắng trứng), hải sản thực vật | 08-EC7 | **09-IC2**. EC7 chỉ còn côn trùng, thịt nuôi cấy, tảo, nấm. |
| Hybrid meat, thức ăn thú cưng, đồ uống không định vị thay sữa | Chưa nêu rõ | 09-IC2 |
| Willingness to try, intention to consume/eat | Chưa nêu rõ | Không phải PI → 10-EC6 |
| So sánh nhiều nguồn protein, có lựa chọn thực vật 4 cặp được đo PI/WTP riêng | Chưa có quy tắc | UNCERTAIN |
| Bài nhánh AI | INCLUDE nếu đạt; tin cậy theo phạm vi kết quả | Qua 4 câu hỏi 3a–3d là INCLUDE + RQ1; **không bắt buộc PI/WTP** |
| AI cá nhân hóa/gợi ý, idol ảo | 09-IC2 | Giữ nguyên, nêu rõ trong câu 3c |
| UNCERTAIN | Ghi lý do ở cột Lý do | Ghi **"Cần kiểm: …"** ở cột Ghi chú xử lý. Không dùng khi tóm tắt đã rõ chỉ đo acceptance/liking. |

**Giả định của người soạn (cần xác nhận):**
- **Đồ uống thực vật định vị thay sữa** (kể cả loại lên men, không gọi là yogurt/kefir) vẫn thuộc cặp 2, như quyết định R0002. Cụm "đồ uống nói chung" trong hướng dẫn được hiểu là đồ uống **không** định vị thay sữa.
- **Bài vừa có AI vừa có thực phẩm 4 cặp:** áp Bước 3; đạt thì INCLUDE và gắn thêm RQ4-food. Chỉ gắn A-TF khi có PI/WTP.

### Quy trình

1. Tạo **notebook mới** cho lần sàng lọc lại, dán instructions mới vào Settings (Custom, Longer). Không dùng lại notebook cũ, vì lịch sử chat cũ sẽ làm notebook bắt chước bảng 12 cột.
2. Chia 209 bài thành 11 lô 20 bài bằng `tools/make_batches.py`, giữ nguyên ID cũ.
3. **Sàng lọc mù:** không đưa quyết định cũ vào nguồn. Nếu file có cột quyết định cũ, xóa cột đó trước khi chạy `make_batches.py`. Đối chiếu với kết quả cũ sau, bằng bảng tính.
4. Mỗi lô: chạy R1, rồi R2. Dán bảng đã sửa vào Google Sheets.
5. Sau 11 lô: đối chiếu với kết quả cũ (R4 hoặc bảng tính) và với hai người sàng lọc còn lại. Người kiểm tra đọc mọi bài có quyết định thay đổi, mọi bài UNCERTAIN, và mọi bài TierF/A-TF.

### R0. Kiểm tra cấu hình

```
Trước khi sàng lọc, tóm tắt bằng 1 bảng: 5 bước của quy trình và các mã tương ứng; 4 câu hỏi 3a–3d; cách xếp các loại thực phẩm vào 4 cặp / 08-EC7 / 09-IC2; định nghĩa PI và WTP hẹp, và những gì KHÔNG tính; ba chỗ hay nhầm; định dạng 13 cột. Xác nhận có xét hạng tạp chí/EC10 hay không. Không sàng lọc bài nào.
```

Kết quả đúng phải có:
- **5 bước**, bảng **13 cột** có cột "Bước";
- trứng thực vật và hải sản thực vật xếp **09-IC2**;
- willingness to try **không** là PI;
- xác nhận **không** xét IC7/EC10.

### R1. Sàng lọc lại một lô

```
SÀNG LỌC LẠI – VÒNG TIÊU ĐỀ–TÓM TẮT
Nguồn: [Batch_01_ID001-020] (tất cả bài trong nguồn này).

Với TỪNG bài, đi đúng 5 bước theo thứ tự trong hướng dẫn và dừng ở bước đầu tiên dẫn tới EXCLUDE:
1. Loại hình thức (01–04)?
2. Có mẫu người tiêu dùng? Không → 05-IC1.
3. Nhánh AI: hỏi 3a → 3b → 3c → 3d. Qua cả 4 câu → INCLUDE + RQ1, không cần PI/WTP.
4. Nhánh thực phẩm: 4a (thuộc 4 cặp?) → 4b (PI/WTP hẹp?) → 4c (có kích thích truyền thông?).
5. Tóm tắt không đủ → UNCERTAIN + "Cần kiểm: …".
Lưu ý:
- Áp chặt ba chỗ hay nhầm. Không dùng UNCERTAIN khi tóm tắt đã rõ chỉ đo acceptance/liking/willingness to try.
- Không xét hạng tạp chí, không dùng EC10.
- Xuất bảng 13 cột, ghi bước dừng vào cột "Bước".
```

### R2. Rà lỗi bảng vừa xuất (chạy ngay sau R1)

```
Rà lại bảng vừa xuất, KHÔNG sàng lọc lại từ đầu. Chỉ sửa khi có căn cứ trong nguồn; không tự suy ra thông tin không có trong tóm tắt. Liệt kê và sửa các dòng vi phạm:
(a) mã phụ có số nhỏ hơn mã chính, hoặc cột "Bước" không khớp với mã chính (01–04 = Bước 1; 05 = Bước 2; 06, 07, 09, 11 ở nhánh AI = Bước 3; 08, 09, 10 ở nhánh thực phẩm = Bước 4);
(b) bài không có người tham gia mà mã chính không phải 05-IC1;
(c) "willingness to try", "intention to consume/eat", acceptance, liking, thái độ hoặc tiêu thụ tự báo cáo bị coi là PI, hoặc bài chỉ đo các biến này mà lại INCLUDE TierF/A-TF (phải là 10-EC6);
(d) phô mai, sữa chua, kem, trứng thực vật, hải sản thực vật, hybrid meat, bánh, pasta, sốt bị xếp vào 4 cặp hoặc 08-EC7 (phải là 09-IC2);
(e) bài chỉ có côn trùng, thịt nuôi cấy, tảo, nấm mà không phải 08-EC7;
(f) avatar/chatbot tư vấn mua sắm, agent dịch vụ, AI dạng công cụ được INCLUDE (phải là 06-EC2);
(g) bài nhánh AI qua đủ 3a–3d nhưng bị EXCLUDE vì thiếu PI/WTP hoặc vì lĩnh vực phi marketing;
(h) UNCERTAIN không có "Cần kiểm: …", hoặc UNCERTAIN trong khi tóm tắt đã rõ chỉ đo acceptance/liking;
(i) TierF có nhãn/thông điệp/quảng cáo (phải là A-TF), hoặc A-TF không có kích thích truyền thông;
(j) gắn A-Disc/disclosure hoặc RQ1 cho nhãn thực phẩm không liên quan AI;
(k) INCLUDE phi marketing không ghi "Lĩnh vực: …", hoặc bài EXCLUDE lại có ghi;
(l) có dùng EC10/social-mkt hoặc loại vì tạp chí;
(m) Lý do không có trích dẫn nguyên văn; dòng không đủ 13 ô; ID trống.
Xuất bảng: | ID | Lỗi | Trước | Sau |. Sau đó xuất lại bảng đầy đủ 13 cột chỉ cho các dòng đã sửa.
```

### R3. Kiểm chứng bài UNCERTAIN hoặc bài TierF/A-TF

```
Xem lại các bài ID: [...].
Với từng bài, trả lời bằng trích dẫn nguyên văn từ nguồn:
1. Thực phẩm cụ thể là gì? Thuộc cặp nào trong 4 cặp, hay 08-EC7 / 09-IC2?
2. Biến phụ thuộc chính xác là gì? Ghi đúng tên biến trong tóm tắt (vd. "purchase intention", "willingness to try"). Biến đó có phải PI/WTP theo định nghĩa hẹp không?
3. Có kích thích truyền thông không (thông điệp, nhãn, quảng cáo)?
4. Quyết định cuối và bước dừng; ghi "GIỮ NGUYÊN" hoặc "THAY ĐỔI: … vì …".
Xuất lại bảng 13 cột cho các bài này.
```

### R4. Tổng hợp cuối mỗi lô

```
Từ các bảng đã sửa trong cuộc trò chuyện này, tổng hợp:
1. Số bài INCLUDE / EXCLUDE / UNCERTAIN.
2. Số bài theo mã loại chính và theo bước dừng.
3. Số bài theo nhánh (A-T1, A-T2, A-T3, A-Disc, A-TF, TierF, B-Meta) và theo RQ.
4. Danh sách ID UNCERTAIN kèm nội dung "Cần kiểm".
5. Danh sách ID gắn snowball và context.
Chỉ dùng số liệu trong các bảng, không sàng lọc lại.
```

**Đối chiếu với kết quả cũ.** Làm trong Google Sheets: ghép bảng mới với quyết định cũ theo ID, lọc các dòng khác nhau. Không đưa quyết định cũ vào NotebookLM, để tránh notebook bị ảnh hưởng theo kết quả cũ.

---

## G. Nhật ký hiệu chỉnh

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

### Quyết định sau pilot 2

- **Mức tiêu thụ tự báo cáo** (R0028): loại theo **EC6**, gắn `context`. Dữ liệu mua/chọn khách quan vẫn tính là PI.
- **EC10**: giữ trong đề cương, nhưng chuyển khỏi NotebookLM xuống bước cuối. Cờ Biz suy từ lĩnh vực tạp chí (SJR Areas/Categories, ABDC), và Food Science được xếp `?`. Các mã còn lại được đánh số lại `01–11`.

### Pilot 3 (cùng 50 bài; notebook vẫn chạy bản instructions trước khi bỏ EC10)

Dấu hiệu dùng bản cũ: mã đánh số `01–12` (06-IC1, 12-EC5), và vẫn có mục "DỮ LIỆU THIẾU… EC10".

Đã đúng: R0028 → EC6; R0001 bỏ EC3; R0035 bỏ RQ3; R0025, R0026, R0027 được coi là "trong phạm vi" (authenticity, source credibility, trust).

| Vấn đề còn lại | Ví dụ | Sửa |
| :--- | :--- | :--- |
| Nhảy thẳng sang mã chủ đề, bỏ qua IC1 dù không có người tham gia | R0020 (phòng thí nghiệm, ghi EC7), R0037 (thuật toán, ghi EC3) | IC1 nêu rõ phòng thí nghiệm/thuật toán; bài không có người tham gia luôn có mã chính IC1; thêm D4b (n) |
| Gắn PI cho "ý định sử dụng chương trình" | R0016 | Thêm "ý định sử dụng chương trình/dịch vụ" vào danh sách KHÔNG là PI |
| Sản phẩm ngoài 4 cặp có thành phần thuộc EC7 được xếp IC2 | R0008 (pasta có côn trùng/tảo), R0024 (aquafaba thay lòng trắng trứng) | EC7 áp dụng khi thành phần chính hoặc chức năng thay thế thuộc EC7; thêm D4b (o) |
| Chưa gắn context cho EC6 chỉ đo tiêu thụ | R0028 | Đã có trong bản mới, do notebook chạy bản cũ |
| Chưa ghi "Lĩnh vực: …" | R0004, R0016 | Đã có trong bản mới, do notebook chạy bản cũ |

### Pilot 4 (cùng 50 bài, instructions bản 11 mã, lần đầu chạy đúng bản)

D0 xác nhận đúng 11 mã, không xét IC7/EC10.

Đã đúng: R0020, R0037 → 05-IC1; R0016 bỏ PI và có "Lĩnh vực: y tế"; R0004 có "Lĩnh vực: tài chính"; R0032 → EC6 + context; R0017 → EC2.

| Vấn đề còn lại | Ví dụ | Sửa |
| :--- | :--- | :--- |
| **Thụt lùi**: lại INCLUDE TierF + PI cho bài chỉ đo tiêu thụ tự báo cáo | R0028 | PI loại trừ có ví dụ cụ thể ("x% respondents currently consume…"); TierF nêu rõ tiêu thụ tự báo cáo là 10-EC6 |
| **Thụt lùi**: gắn PI cho acceptance intention, Tin cậy Cao | R0023 | Thêm "acceptance intention" vào danh sách KHÔNG là PI; D4b (q) |
| Vẫn xếp IC2 dù quy tắc ngoại lệ yêu cầu EC7 | R0008, R0024 | Đổi thứ tự: 08-EC7 trước 09-IC2 (bỏ ngoại lệ, dùng thứ tự) |
| Gắn EC6 làm mã phụ cho thực phẩm ngoài 4 cặp | R0002, R0043, R0045 | EC6 "CHỈ dùng, kể cả làm mã phụ, cho 4 cặp" |
| Coi du lịch là phi marketing, hạ tin cậy | R0027 | Nêu rõ du lịch/điểm đến, bán lẻ, dịch vụ, livestream, thực phẩm là marketing |
| Lý do không còn trích dẫn nguyên văn | toàn bộ lô | Bắt buộc một trích dẫn tiếng Anh ngắn trong ngoặc kép |
| EC5 làm mã phụ nhưng không gắn context (không nhất quán) | R0040, R0046, R0047 | "Gắn context dù EC5 là mã chính hay phụ" |
| Lệch cột (13 ô) | R0049 | D4b (u) |
| R0002 lúc là cặp 2, lúc ngoài 4 cặp giữa các lượt chạy | R0002 | Dấu hiệu bài thật sự mơ hồ, cần người quyết định. Cả hai cách đều EXCLUDE. |

Quy tắc "bài có mã phụ thì tin cậy tối đa TB" bị bỏ: notebook không áp dụng cho bài loại, và quy tắc này không giúp gì. Thay bằng "bài INCLUDE có ghi Lĩnh vực thì tối đa TB".

### Quyết định R0002 (sau khi đọc toàn văn)

*Fermented quinoa–chickpea beverages…* (Food Bioscience 82, 2026). Kết luận: **EXCLUDE – 10-EC6**, không mã phụ, không context.

- **Thuộc cặp 2 (sữa thực vật – sữa).** Bài định vị sản phẩm là "plant-based beverage (PBB)". Phần dẫn nhập đặt nó trong thị trường đồ uống thực vật (đậu nành, yến mạch, hạnh nhân), nhắc tới lý do thay sữa (không dung nạp lactose, dị ứng sữa), và dùng **đồ uống đậu nành thương mại** làm đối chứng cảm quan. Sản phẩm không được gọi là yogurt hay kefir.
- **Không đo PI/WTP.** Chỉ có thang hedonic 7 điểm (n = 94, hội đồng cảm quan không chuyên) và kiểm định xếp hạng ưa thích. Bài cũng không so sánh với sữa bò, nên không phải trường hợp Q6.
- **Không dùng IC2.** Lần trước notebook xếp IC2 vì quy tắc cũ ghi "đồ uống lên men khác không thuộc 4 cặp". Câu này mâu thuẫn với định vị PBB và là nguyên nhân khiến kết quả đổi qua lại giữa các lượt chạy. Quy tắc đã được sửa như trên.

### Pilot 5 (cùng 50 bài, bản 11 mã có quy tắc đồ uống thực vật; chạy D0 → D1 → D4b)

**Mức quyết định (INCLUDE/EXCLUDE): khớp toàn bộ 50/50** với đánh giá của người hiệu chỉnh. 14 bài INCLUDE: R0003, R0004, R0009, R0012, R0016, R0018, R0023, R0025, R0026, R0027, R0029, R0033, R0035, R0042.

Đã đúng: R0002 → 10-EC6; R0028 → 10-EC6 + context; R0023 bỏ PI; R0027 Cao; R0008 → EC7; R0043, R0045 không còn mã phụ EC6; Lý do có trích dẫn nguyên văn. D4b sửa đúng R0009 (thêm RQ2-fit) và R0016 (message liking là thái độ với quảng cáo, thuộc phạm vi).

| Vấn đề còn lại | Ví dụ | Sửa |
| :--- | :--- | :--- |
| Bài phòng thí nghiệm nhưng mã chính là EC7 thay vì IC1 | R0020 | Dòng EC7 nhắc lại: không có người tham gia thì mã chính là 05-IC1 |
| Aquafaba thay lòng trắng trứng xếp IC2 | R0024 | Thêm ví dụ "aquafaba" vào EC7 |
| Gắn RQ1 + disclosure cho nhãn thực phẩm thực vật | R0029 | Nhãn thực phẩm không phải A-Disc; bài thực phẩm không có AI không gắn RQ1 |
| IC2 làm mã chính vì lĩnh vực xã hội (nên là EC5) | R0006 | "Không dùng IC2 chỉ vì lĩnh vực phi marketing" |
| D4b thêm "Lĩnh vực" cho bài EXCLUDE và **bịa lĩnh vực** | R0019 ("Y tế / Tài chính"), R0038 ("Y tế") | Chỉ ghi Lĩnh vực cho INCLUDE/UNCERTAIN; D4b không được tự suy ra thông tin |
| D4b bỏ sót lỗi | R0020, R0024, R0029 | Thêm mục (v), (w); nhắc lại (n), (o) |

**Khuyến nghị:** sai sót còn lại chỉ nằm ở mã phụ/nhãn, không ảnh hưởng quyết định chọn/loại. Nên **chốt (freeze) instructions** sau bản này và chuyển sang các lô tiếp theo. Không sửa instructions giữa các lô, để mọi bài được sàng lọc bằng cùng một bộ quy tắc. Người kiểm tra đọc lại 100% bài INCLUDE và khoảng 10–20% bài EXCLUDE chọn ngẫu nhiên.
