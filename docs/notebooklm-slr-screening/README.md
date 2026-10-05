# Sàng lọc bài báo SLR bằng NotebookLM

Bộ tài liệu gồm 3 phần:

1. **Hướng dẫn cấu hình notebook** (mục A–C bên dưới).
2. **Custom instructions** dán vào Settings: [`custom-instructions.txt`](custom-instructions.txt), khoảng 7.600 ký tự, dưới giới hạn 10.000 ký tự của NotebookLM.
3. **Các prompt chạy từng lượt** (mục D).

---

## A. Chuẩn bị nguồn (sources)

NotebookLM tìm kiếm theo đoạn văn, nên bảng tính lớn dễ bị bỏ sót dòng. Vì vậy nên chia nhỏ dữ liệu.

**Vòng tiêu đề–tóm tắt (TiAb)**

- Xuất file 32 (đã gộp nhóm A và B) thành nhiều Google Docs hoặc file `.txt`, mỗi file **25–40 bài**. Đặt tên theo lô, ví dụ `Batch_01_ID001-040`.
- Mỗi bài là một khối có nhãn trường rõ ràng để mô hình không phải đoán:

```
=== ID: 017 ===
Title: ...
Authors: ... | Year: ... | DOI: ...
Journal: ... | Document type: Article
Rank: Level=1 ; ABDC=A ; SJR=Q1
Biz: Y            (Y / N / ?)
Group: A          (A / B)
Retraction: No
Abstract: ...
```

- Trường `ID`, `Rank` và `Biz` là bắt buộc. NotebookLM được yêu cầu **không tự tra** xếp hạng tạp chí, chỉ dùng giá trị bạn cung cấp.
  - Thiếu `ID` thì bảng sẽ có cột ID trống, như lượt pilot 1.
  - Thiếu `Rank`/`Biz` thì IC7/EC10 không được xét.

**Vòng toàn văn (FT)**

- Mỗi PDF là một nguồn, đặt tên `ID_TacGia_Nam.pdf` (vd. `017_Nguyen_2024.pdf`) để ID xuất hiện trong trích dẫn.
- PDF phải có lớp chữ. Nếu là bản scan, chạy OCR trước khi tải lên.

> Giới hạn nguồn: bản miễn phí 50 nguồn/notebook, bản Pro 300. Nếu nhiều PDF hơn, chia thành nhiều notebook.

## B. Cấu hình Settings

Custom instructions áp dụng cho cả notebook, nên **tạo 2 notebook riêng**: một cho TiAb, một cho FT. Dùng cùng một bộ instructions; prompt từng lượt sẽ báo đang ở vòng nào.

1. Mở notebook, trong khung **Chat** bấm biểu tượng cấu hình (⚙ / *Configure notebook*). Tên mục có thể hơi khác tùy phiên bản.
2. **Conversational goal / Define your conversational style** → chọn **Custom**.
3. Mở [`custom-instructions.txt`](custom-instructions.txt) và điền 2 chỗ để trống:
   - `[DANH SÁCH CẶP THỰC PHẨM MỤC TIÊU ...]`
   - `[ĐỊNH NGHĨA RQ1–RQ4]`

   Sau đó dán toàn bộ nội dung vào ô Custom. Không để lại ngoặc vuông: nếu còn, NotebookLM sẽ tự đoán (lượt pilot 1 đã tự suy ra "4 cặp thực phẩm mục tiêu" và gắn RQ1 cho mọi bài).
4. **Response length** → chọn **Longer**, để bảng nhiều dòng không bị cắt.
5. Bấm **Save**. Mở chat mới để cấu hình có hiệu lực.

Thói quen khi chạy:

- Ở cột Sources, **chỉ tick lô hoặc PDF đang sàng lọc**, bỏ tick các nguồn khác.
- Mỗi lượt chat tối đa khoảng **15–20 bài** (TiAb) hoặc **1 bài** (FT). Câu trả lời dài dễ bị cắt hoặc thiếu dòng.
- Kết quả dùng được thì bấm **Save to note**, rồi copy bảng sang Google Sheets (dán bảng Markdown vào Sheets sẽ tự tách cột).

## C. Kiểm soát chất lượng (nên làm)

1. **Pilot**: tự mã hóa trước 20–30 bài, cho NotebookLM chạy (prompt D1 + D2), rồi so sánh từng bài. Chỗ nào lệch thì sửa câu chữ của tiêu chí trong instructions và chạy lại. Ghi lại tỷ lệ đồng thuận để báo cáo.
2. **Mọi quyết định EXCLUDE ở vòng FT** và mọi dòng trong mục "CẦN NGƯỜI KIỂM TRA" phải được người đọc lại. NotebookLM chỉ đóng vai người sàng lọc thứ hai, không phải người quyết định cuối cùng.
3. Lưu phiên bản instructions và ngày chạy, để báo cáo minh bạch việc dùng AI trong PRISMA.
4. Câu trả lời có thể khác nhau giữa các lần chạy. Với bài khó, chạy lại D3 thay vì tin lần đầu.

### Các giả định trong instructions (sửa nếu không đúng ý bạn)

- Thứ tự xét loại theo đúng thứ tự trong danh sách của bạn. Mã đầu tiên thỏa là **mã loại chính**.
- Thêm quyết định **UNCERTAIN** cho vòng TiAb (nguyên tắc "nghi ngờ thì giữ").
- EC1: giữ bản đầy đủ nhất trong các bản trùng.
- **PI hiểu theo nghĩa hẹp**: ý định mua/chọn sản phẩm. Ý định tiếp tục dùng, tiếp nhận thông tin, chấp nhận công nghệ, engagement hay ý định du lịch không tính là PI.
- **EC2** gồm cả avatar giống người nhưng chỉ đóng vai trợ lý mua sắm/CSKH, không chứng thực sản phẩm.
- **IC1** gồm cả bài khái niệm/triết học, mẫu là nhân viên/nhà sản xuất, và bài chỉ phân tích đầu ra của AI.
- **EC6** gồm cả bài thực phẩm chỉ đo tiêu thụ/dinh dưỡng.
- Thực phẩm thay thế không thuộc danh sách mục tiêu và không có trong EC7 thì xếp **IC2**.
- **RQ2-fit** chỉ gắn khi bài đo/thao tác trực tiếp sự phù hợp. Loại sản phẩm chỉ làm biến điều tiết thì chưa đủ.
- EC5: nghiên cứu hỗn hợp có phần định lượng trên người tiêu dùng thì **không** bị loại.
- TierF-core "so sánh với nguyên bản" chỉ tính khi so sánh trên PI/WTP/lựa chọn. So sánh chỉ về cảm quan thì thuộc EC6 (Q6).
- A-TF khác TierF ở chỗ có yếu tố truyền thông hoặc người chứng thực.
- "AI vô hình" (IC2) được hiểu là AI chạy ngầm, không hiện ra thành nội dung hay nhân vật.

---

## D. Prompt chạy từng lượt

### D0. Kiểm tra cấu hình (chạy 1 lần khi mở notebook)

```
Trước khi sàng lọc, hãy tóm tắt lại bằng 1 bảng: thứ tự 13 mã loại, điều kiện đặc biệt của EC10, EC9, EC5, và sự khác nhau giữa A-TF và TierF. Không sàng lọc bài nào.
```

Nếu tóm tắt sai hoặc thiếu, nghĩa là custom instructions chưa được lưu hoặc bị cắt.

### D1. Sàng lọc vòng tiêu đề–tóm tắt

```
VÒNG: TIÊU ĐỀ–TÓM TẮT (TiAb)
Nguồn: [Batch_01_ID001-040]
Phạm vi: các bài có ID từ [001] đến [020] (tối đa 20 bài/lượt).

Sàng lọc từng bài theo đúng Bước 1 (xét loại theo thứ tự) và Bước 2 (gắn nhãn) trong hướng dẫn của notebook.
- Để trống cột Tier F (vòng này chưa gắn).
- Nghi ngờ thì chọn UNCERTAIN, không EXCLUDE.
- Lý do phải trích dẫn câu trong tóm tắt hoặc metadata.
- Mã loại chính phải là mã có số thứ tự nhỏ nhất trong các mã thỏa; tự kiểm tra trước khi xuất.
- Không đánh "Cao" mặc định: áp dụng đúng thang ĐỘ TIN CẬY.
Cuối bảng, xác nhận: "Đã xử lý N/N bài" và liệt kê ID bị thiếu (nếu có).
```

### D2. Sàng lọc vòng toàn văn (mỗi lượt 1 PDF)

```
VÒNG: TOÀN VĂN (FT)
Nguồn: [017_Nguyen_2024.pdf] (chỉ dùng nguồn này).

1. Trước tiên trích xuất ngắn (có trích dẫn trang/đoạn): loại tài liệu, tạp chí, thiết kế nghiên cứu, mẫu (ai, bao nhiêu), loại AI/người chứng thực/sản phẩm, biến phụ thuộc (PI, WTP, choice, thái độ, cảm quan), có công khai AI hay không, loại dữ liệu.
2. Dựa trên phần trích xuất, áp dụng Bước 1 và Bước 2. Quyết định chỉ là INCLUDE hoặc EXCLUDE.
3. Nếu thuộc TierF hoặc A-TF, gắn TierF-core hoặc TierF-context và nêu căn cứ.
4. Xuất bảng 1 dòng theo định dạng chuẩn.
```

### D3. Kiểm tra lại các bài UNCERTAIN hoặc bị nghi sai

```
Xem lại các bài ID: [005, 012, 019].
Với từng bài:
1. Nêu quyết định trước đó và mã/nhãn đã gắn.
2. Đặt 3 câu hỏi kiểm chứng cho chính quyết định đó (vd. "Mẫu có thật là người tiêu dùng không?", "Biến đo có phải PI/WTP không?", "Có mã loại nào đứng trước trong thứ tự bị bỏ qua không?").
3. Trả lời từng câu chỉ bằng trích dẫn từ nguồn.
4. Đưa ra quyết định cuối và ghi rõ "GIỮ NGUYÊN" hoặc "THAY ĐỔI: ... vì ...".
Xuất lại bảng theo định dạng chuẩn cho các bài này.
```

### D4. Kiểm tra trùng lặp (EC1) trong một lô

```
Trong các nguồn đang chọn, tìm các cặp bài có cùng DOI, cùng tiêu đề gần giống nhau, hoặc cùng tác giả + cùng mô tả mẫu/dữ liệu.
Xuất bảng: | ID giữ | ID loại (EC1) | Căn cứ trùng | Tin cậy |
Không kết luận trùng nếu chỉ giống chủ đề.
```

### D4b. Kiểm tra lại thứ tự mã và nhãn (chạy sau D1)

```
Rà lại bảng vừa xuất, KHÔNG sàng lọc lại từ đầu. Liệt kê và sửa các dòng vi phạm:
(a) mã phụ có số nhỏ hơn mã chính;
(b) có EC10 hoặc social-mkt khi nguồn không có trường Biz;
(c) có gắn PI cho biến không phải ý định mua/chọn;
(d) có RQ2-fit mà không đo trực tiếp fit/congruence;
(e) TierF mà bài có nhãn, thông điệp hoặc người chứng thực (phải là A-TF);
(f) ID trống.
Xuất bảng: | ID | Lỗi | Trước | Sau |. Sau đó xuất lại bảng đầy đủ chỉ cho các dòng đã sửa.
```

### D5. Tổng hợp cuối lô

```
Từ các bảng sàng lọc trong cuộc trò chuyện này, tổng hợp:
1. Số bài INCLUDE / EXCLUDE / UNCERTAIN.
2. Số bài theo từng mã loại chính (phục vụ sơ đồ PRISMA).
3. Số bài theo từng nhánh (A-T1, A-T2, A-T3, A-Disc, A-TF, TierF, B-Meta) và theo RQ.
4. Danh sách ID gắn snowball và context.
Chỉ dùng số liệu đã có trong các bảng, không sàng lọc lại.
```

---

## E. Nhật ký hiệu chỉnh

### Pilot 1 (50 bài, vòng TiAb)

| Vấn đề quan sát | Ví dụ | Sửa trong instructions |
| :--- | :--- | :--- |
| Cột ID trống; mục kiểm tra có 50 dòng `****` | toàn bộ lô | Quy tắc ID dự phòng `STT-TácGiả-Năm`; báo thiếu Rank/Biz bằng một dòng chung |
| Sai thứ tự mã chính/phụ | *Ethical Problems…* (IC2 > IC1); *Pseudo-Confidence…* (IC2 > EC2); *Stakeholder perspectives…* (EC5 > EC10) | Đánh số mã `01–13`, bắt buộc tự kiểm tra |
| Dùng EC10 khi nguồn không có Biz | *Frontal facial analysis…*, *Yeast strains…* | Không có Biz thì cấm EC10/social-mkt |
| Gắn PI quá rộng | continued use, information adoption, usage intention, engagement, travel intention | Định nghĩa PI hẹp |
| Avatar trợ lý mua sắm được xếp A-T2 | *Demystifying the Impact of Homophily…* | EC2 gồm avatar trợ lý không chứng thực |
| Nhãn thực vật xếp TierF thay vì A-TF | *From Niche to Norm…* | A-TF = có kích thích truyền thông (kể cả nhãn) |
| Gắn RQ2-fit khi chỉ có điều tiết hedonic/utilitarian | *The power of facial allure…* | RQ2-fit chỉ khi đo fit trực tiếp |
| Tin cậy đều là "Cao" | toàn bộ lô | Thêm thang Cao/TB/Thấp và giới hạn trần |
| Tự suy ra "4 cặp thực phẩm mục tiêu" | pasta, cream cheese, fava spread | Thêm mục THỰC PHẨM MỤC TIÊU (cần người dùng điền) |
