# GHI NHỚ TIẾN TRÌNH SLR – SÀNG LỌC BẰNG NOTEBOOKLM
*Cập nhật: 07/10/2026. Trạng thái: đã hiệu chỉnh qua 5 lượt chạy thử, đề xuất chốt instructions.*

> Dùng ghi nhớ này làm bối cảnh cho các phiên tiếp theo. Các quyết định dưới đây **đã được chốt**, không cần bàn lại trừ khi tôi yêu cầu.

---

## 1. Bối cảnh nghiên cứu

**Câu hỏi tổng hợp.** Bằng chứng hiện có cho biết gì về tác động của việc chứng thực bằng người đại diện tổng hợp (deepfake/AI) có công khai đến mức sẵn sàng chi trả (WTP) và các phản ứng liên quan của người tiêu dùng? Tác động này thay đổi thế nào theo sự phù hợp sản phẩm–người chứng thực, cảm nhận tính đổi mới, và loại thực phẩm (mô phỏng so với nguyên bản)?

| RQ | Nhãn | Gắn khi bài… |
|---|---|---|
| RQ1 | `RQ1` | Có người chứng thực hoặc nội dung tổng hợp, hoặc có nhãn/công khai AI, **và** đo phản ứng người tiêu dùng. Gồm các luồng A-T1, A-T2, A-T3, A-Disc. Bài thực phẩm không có AI hay người chứng thực tổng hợp thì **không** gắn RQ1. |
| RQ2 | `RQ2-fit` | Đo hoặc thao tác sự phù hợp (fit, match-up, congruence) giữa người chứng thực tổng hợp và sản phẩm/thương hiệu/điểm đến; **hoặc** so sánh theo loại sản phẩm (hedonic/utilitarian, sensory, search/experience). |
| RQ3 | `RQ3-innovativeness` | Có biến perceived innovativeness, novelty, creativity hoặc consumer innovativeness; hoặc thiết kế do AI tạo được đánh giá về tính đổi mới. **Không** tính realism, anthropomorphism, attractiveness. |
| RQ4 | `RQ4-food` | Có thực phẩm mô phỏng hoặc nguyên bản thuộc 4 cặp. Gồm các luồng A-TF và TierF. |

**Kết quả đo trong phạm vi**
- **Chính:** WTP.
- **Phụ:** PI; độ tin cậy/niềm tin (credibility, trust, brand trust); tính chân thực (authenticity); cảm nhận đổi mới; thái độ với quảng cáo/thương hiệu (kể cả message liking).
- Bài đo ít nhất một biến trong danh sách này là "trong phạm vi".

**Thiết kế:** định lượng (thực nghiệm, khảo sát SEM, choice experiment, meta-analysis).

**4 cặp thực phẩm mục tiêu (mô phỏng – nguyên bản):**
1. Thịt thực vật – thịt
2. Sữa thực vật – sữa
3. Bia không cồn – bia
4. Margarine – bơ

---

## 2. Quy trình hai giai đoạn (đã chốt)

| Giai đoạn | Công cụ | Tiêu chí |
|---|---|---|
| **1. Sàng lọc nội dung** (tiêu đề–tóm tắt, rồi toàn văn) | NotebookLM + người kiểm tra | 11 mã loại (mục 3) và các nhãn chọn (mục 4) |
| **2. Lọc tạp chí** (chỉ với danh sách INCLUDE cuối) | Script `rank_journals.py` + người kiểm tra | IC7 (hạng tạp chí) và EC10 (lĩnh vực kinh doanh) |

- **IC7 và EC10 đã được chuyển khỏi NotebookLM** theo quyết định của tôi. Lý do:
  - NotebookLM không tra được danh sách khoảng 17.800 tạp chí một cách tin cậy.
  - File nguồn không có cờ Biz.
- Trong PRISMA, ghi số bài loại vì IC7 và vì EC10 thành **các bước riêng, sau vòng toàn văn**.

---

## 3. Tiêu chí loại ở NotebookLM: 11 mã, xét theo thứ tự bắt buộc

Mã có **số nhỏ nhất** thỏa là mã loại chính; các mã khác thỏa là mã phụ.

| Mã | Nội dung |
|---|---|
| 01-Retracted | Bài bị rút. |
| 02-IC5 | Không phải bài báo tạp chí: chương sách, bài hội nghị, xã luận, errata. |
| 03-EC1 | Trùng DOI hoặc trùng dữ liệu. Giữ bản đầy đủ nhất. |
| 04-EC9 | Tổng quan, scoping, bibliometric, research agenda. Meta-analysis không thuộc mã này (gắn B-Meta). Luôn gắn `snowball`. |
| 05-IC1 | Không có mẫu người tiêu dùng: mô hình, mô phỏng máy tính, lý thuyết trò chơi, bài khái niệm/triết học, phòng thí nghiệm, thuật toán; mẫu chỉ là nhà quản lý/nhân viên/nhà sản xuất/chuyên gia; hoặc chỉ phân tích đầu ra của AI. **Bài không có người tham gia luôn lấy 05-IC1 làm mã chính.** |
| 06-EC2 | Chatbot, trợ lý giọng nói, robot, AI tạo sinh dạng công cụ. Gồm cả **avatar giống người chỉ làm trợ lý mua sắm/CSKH**, không chứng thực sản phẩm. |
| 07-EC3 | Chỉ khi bài về deepfake hoặc phát hiện nội dung AI (kỹ thuật, pháp lý, chính trị, tin giả) mà không đo phản ứng với nhãn hàng. |
| 08-EC7 | Thịt nuôi cấy, côn trùng, tảo, nấm, trứng thực vật (kể cả chất thay lòng trắng trứng như aquafaba), hải sản thực vật; hoặc sản phẩm có thành phần/chức năng thay thế thuộc nhóm này. |
| 09-IC2 | VTuber/giải trí, AI chạy ngầm, cá nhân hóa bằng AI, chủ đề ngoài phạm vi, hoặc thực phẩm ngoài 4 cặp. **Không dùng IC2 chỉ vì bài thuộc lĩnh vực phi marketing.** |
| 10-EC6 | **Chỉ áp dụng cho thực phẩm thuộc 4 cặp** (kể cả khi làm mã phụ) có mẫu người nhưng không đo PI/WTP: chỉ đo chấp nhận, thái độ, cảm quan, tiêu thụ tự báo cáo, dinh dưỡng. Gồm trường hợp Q6 (chỉ so sánh cảm quan giữa sản phẩm mô phỏng và nguyên bản). Bài chỉ đo tiêu thụ tự báo cáo thì gắn thêm `context`. |
| 11-EC5 | Định tính: phỏng vấn, focus group, netnography, phân tích nội dung/bình luận, case study. Gắn `context` dù là mã chính hay mã phụ. Nghiên cứu hỗn hợp có phần định lượng trên người tiêu dùng thì **không** thuộc mã này. |

**Những thay đổi so với danh sách tiêu chí gốc**
- Bỏ IC7 và EC10 khỏi NotebookLM (chuyển xuống giai đoạn 2).
- **EC7 được đặt trước IC2.** Đổi chỗ này không làm thay đổi quyết định chọn/loại của bài nào, chỉ đổi mã loại chính.
- Thêm quyết định **UNCERTAIN** cho vòng tiêu đề–tóm tắt (nghi ngờ thì giữ).

---

## 4. Tiêu chí chọn và các nhãn

**Nhánh** (có thể gắn nhiều nhánh):
- **A-T1:** bản sao người thật (deepfake, digital twin, "hồi sinh").
- **A-T2:** nhân vật hư cấu giống người đóng vai chứng thực/giới thiệu sản phẩm (influencer ảo, digital human, AI streamer, virtual anchor).
- **A-T3:** nội dung marketing do AI tạo hoặc thiết kế (quảng cáo, bao bì, hình ảnh).
- **A-Disc:** thao tác hoặc đo nhãn/công khai AI. **Nhãn thực phẩm (plant-based, thành phần, dinh dưỡng) không phải A-Disc.**
- **A-TF:** thực phẩm mục tiêu + kích thích truyền thông (nhãn, thông điệp, quảng cáo, người chứng thực) + đo PI/WTP hoặc so sánh với nguyên bản.
- **TierF:** thực phẩm mục tiêu có đo PI/WTP đúng định nghĩa, **không** có kích thích truyền thông.
- **B-Meta:** meta-analysis.

**Tầng Tier F** (chỉ gắn ở vòng toàn văn):
- **TierF-core:** có WTP, choice/conjoint, hoặc so sánh mô phỏng với nguyên bản trên PI/WTP/lựa chọn.
- **TierF-context:** khảo sát yếu tố quyết định PI.

**Đặc điểm:** `disclosure`, `WTP`, `PI`, `obs-data`. Nhãn `social-mkt` được gắn ở giai đoạn 2, khi Biz = ?.

**Ghi chú xử lý:**
- `no-abstract`, `design-unclear`
- `snowball` (đi kèm EC9)
- `context` (đi kèm EC5; đi kèm EC6 khi bài chỉ đo tiêu thụ)
- `promote-A` (hiếm dùng)

**Độ tin cậy:** Cao / TB / Thấp. Bài INCLUDE thuộc lĩnh vực phi marketing thì tối đa TB. Bài không đo biến nào trong phạm vi vẫn gắn RQ1 nhưng tối đa TB, ghi "kết quả ngoài phạm vi".

---

## 5. Các định nghĩa và quyết định đã chốt

1. **PI theo nghĩa hẹp:** ý định MUA/chọn sản phẩm, hoặc dữ liệu mua/chọn **khách quan** (lựa chọn trong thực nghiệm, lựa chọn có khuyến khích, scanner, dữ liệu bán hàng).
   - **Không phải PI:** ý định tiếp tục dùng, ý định sử dụng chương trình/dịch vụ, ý định chấp nhận (acceptance intention), tiếp nhận thông tin, engagement, ý định du lịch/tham gia, mức tiêu thụ **tự báo cáo**, tần suất ăn, khẩu phần.
2. **WTP:** mức giá sẵn sàng trả, đấu giá, choice/conjoint có thuộc tính giá.
3. **Mức tiêu thụ tự báo cáo** (ví dụ R0028): loại theo **EC6** và gắn `context`. Không xếp thành TierF-context. Lý do: giữ đúng văn bản tiêu chí, tránh làm tràn Tier F, và loại dữ liệu này không trả lời được RQ4.
4. **Đồ uống thực vật** (plant-based beverage, milk alternative), **kể cả loại lên men**, thuộc cặp 2 nếu không được gọi là yogurt/kefir. Phô mai, sữa chua/yogurt/kefir, kem, sốt, bánh, pasta không thuộc 4 cặp. Không rõ định vị thì UNCERTAIN.
5. **Sản phẩm phải được định vị thay thế đúng một vế nguyên bản**, ví dụ burger thực vật thuộc cặp 1.
6. **Lĩnh vực:**
   - Du lịch/điểm đến, bán lẻ, dịch vụ, livestream, thực phẩm **là** marketing.
   - Y tế, giáo dục, tài chính/đầu tư, tuyển dụng, chính sách công/xã hội là phi marketing. Với bài INCLUDE/UNCERTAIN thuộc nhóm này, ghi "Lĩnh vực: …" vào cột Lý do để đối chiếu với cờ Biz ở giai đoạn 2. Bài EXCLUDE thì không ghi.
7. **EC10 vẫn nằm trong đề cương** nhưng được xét ở giai đoạn 2. Cờ Biz suy ra từ lĩnh vực của tạp chí (mục 6).
8. **Nghĩa của "mô phỏng":** trong IC1 là mô hình máy tính hoặc mô hình toán. "Thực phẩm mô phỏng" là sản phẩm thay thế.

**Quyết định cho từng bài cụ thể**

| Bài | Quyết định | Căn cứ |
|---|---|---|
| R0002 *Fermented quinoa–chickpea beverages* (Food Bioscience 82, 2026) | **EXCLUDE – 10-EC6** | Đã đọc toàn văn. Sản phẩm được định vị là plant-based beverage, đối chứng là đồ uống đậu nành thương mại. Chỉ có thang hedonic 7 điểm (n = 94), không có PI/WTP, không so sánh với sữa bò. |
| R0028 *The meat of the matter* | **EXCLUDE – 10-EC6 + context** | Chỉ đo tiêu thụ tự báo cáo. |
| R0017 avatar trợ lý mua sắm | **EXCLUDE – 06-EC2** | Avatar không chứng thực sản phẩm. |
| R0009 AI streamer, hedonic/utilitarian | **INCLUDE, gắn RQ2-fit** | So sánh theo loại sản phẩm được tính theo định nghĩa RQ2. |
| R0029 *From Niche to Norm* | **INCLUDE – A-TF, RQ4-food, PI** | Không gắn RQ1 và disclosure, vì nhãn thực phẩm không phải công khai AI. |

---

## 6. Giai đoạn 2: lọc tạp chí (IC7 + EC10)

**IC7 đạt** khi tạp chí thuộc ít nhất một trong ba danh sách:
- Marketing Level 1, gồm cả Elite. Trong danh sách: "JAMS" là *Journal of the Academy of Marketing Science*; "Journal of Services Research" là *Journal of Service Research*.
- ABDC JQL 2025 hạng A\*, A hoặc B.
- SJR 2025 Best Quartile Q1 hoặc Q2.

Cả 20 tạp chí Level 1 đều là SJR Q1. Danh sách gộp có khoảng 17.818 tạp chí.

**Cờ Biz** được suy ra theo tạp chí:

| Biz | Điều kiện | Xử lý |
|---|---|---|
| Y | Có trong ABDC hoặc Level 1, hoặc SJR Areas thuộc Business / Economics / Decision Sciences | Giữ |
| ? | SJR Areas thuộc Psychology / Social Sciences / Arts & Humanities / Multidisciplinary, hoặc Categories thuộc Food Science, Nutrition, Communication, Tourism, HCI | Giữ, gắn `social-mkt` |
| N | Không thuộc các nhóm trên | EC10, kiểm tay trước khi loại |
| Không xác định | Không tìm thấy tạp chí | Kiểm tay |

**Food Science bắt buộc xếp `?`**, để các bài TierF đăng trên *Food Quality and Preference*, *Appetite*, *Foods* không bị loại oan.

**Lệnh chạy:**
```
python3 tools/rank_journals.py --records danh_sach_cuoi.csv --sjr scimagojr_2025_1.csv --abdc ABDC-JQL-2025-v3-210926.xlsx --out out/
```

**Kết quả:**
- `records_ranked.csv`: có các cột Level1, ABDC_2025, SJR_Q, IC7, Biz, EC10, Tag.
- `final_review.csv`: các bài cần kiểm tay.
- `whitelist.csv`: toàn bộ tạp chí đạt IC7.

---

## 7. Cấu hình NotebookLM và quy trình chạy

**Cấu hình:**
- Tạo 2 notebook: một cho vòng tiêu đề–tóm tắt, một cho vòng toàn văn.
- Settings: Conversational style chọn **Custom**, dán toàn bộ `custom-instructions.txt` (khoảng 8.160 ký tự, giới hạn 10.000). Response length chọn **Longer**.
- Mỗi lần cập nhật: **xóa toàn bộ nội dung cũ trong ô Custom rồi mới dán bản mới**, sau đó **xóa lịch sử chat**. Nếu không xóa, notebook sẽ bắt chước các bảng cũ.

**Nguồn:**
- Vòng tiêu đề–tóm tắt: `tools/make_batches.py` chia file 32 thành các lô 20 bài, mỗi bài là một khối gồm ID, Title, Authors/Year/DOI, Journal/Type, Group, Retraction, Abstract.
- Vòng toàn văn: mỗi PDF là một nguồn, đặt tên `ID_TacGia_Nam.pdf`.
- Chỉ tick nguồn đang sàng lọc. Mỗi lượt tối đa 20 bài (tiêu đề–tóm tắt) hoặc 1 bài (toàn văn).

**Bảng kết quả:**
```
| ID | Tiêu đề gốc | Quyết định | Mã loại chính | Mã loại phụ | Nhánh | Tier F | RQ | Đặc điểm | Ghi chú xử lý | Lý do | Tin cậy |
```
- Cột Lý do: tối đa 2 câu, kèm một trích dẫn nguyên văn tiếng Anh trong ngoặc kép.
- Sau bảng có mục "CẦN NGƯỜI KIỂM TRA" và dòng "Đã xử lý N/N bài".

**Các prompt:**

| Prompt | Mục đích |
|---|---|
| D0 | Kiểm tra cấu hình. Đúng khi liệt kê 11 mã từ 01 đến 11, có **05-IC1, 08-EC7, 09-IC2, 10-EC6**, và xác nhận không xét IC7/EC10. |
| D1 | Sàng lọc vòng tiêu đề–tóm tắt. |
| D2 | Sàng lọc vòng toàn văn: trích xuất trước, quyết định sau, gắn Tier F. |
| D3 | Kiểm chứng lại các bài UNCERTAIN hoặc nghi sai. |
| D4 | Tìm bài trùng lặp (EC1). |
| **D4b** | Rà lỗi bảng vừa xuất theo danh sách mục (a)–(w), **luôn chạy ngay sau D1**. D4b không được tự suy ra thông tin không có trong nguồn. |
| D5 | Tổng hợp số liệu PRISMA và danh sách INCLUDE để chuyển sang giai đoạn 2. |

---

## 8. Lịch sử hiệu chỉnh (cùng lô 50 bài R0001–R0050)

| Lượt | Lỗi chính | Cách xử lý |
|---|---|---|
| Pilot 1 | ID trống; sai thứ tự mã; dùng EC10 khi không có Biz; PI quá rộng; độ tin cậy toàn "Cao"; tự đoán "4 cặp" | Đánh số mã; định nghĩa PI hẹp; thêm định nghĩa RQ và 4 cặp; thêm thang độ tin cậy |
| Pilot 2 | Coi tiêu thụ là PI; coi authenticity/trust là ngoài phạm vi; gắn RQ3 cho realism | Thêm danh mục kết quả đo trong phạm vi; siết định nghĩa EC3, EC6, RQ3 |
| Pilot 3 | Notebook vẫn chạy bản instructions cũ; bỏ qua IC1 với bài phòng thí nghiệm | Bổ sung quy trình xóa nội dung cũ và xóa lịch sử chat; IC1 luôn là mã chính khi không có người tham gia |
| Pilot 4 | R0028 và R0023 sai lại; quy tắc ngoại lệ EC7 không được áp dụng | Đổi chỗ EC7 lên trước IC2; ghi rõ lĩnh vực nào là marketing; bắt buộc trích dẫn nguyên văn |
| Pilot 5 | **Quyết định INCLUDE/EXCLUDE khớp 50/50.** Còn lỗi mã/nhãn ở R0020, R0024, R0029, R0006; D4b tự bịa lĩnh vực cho bài loại | Chỉ ghi "Lĩnh vực" cho bài giữ; thêm ví dụ aquafaba; tách nhãn thực phẩm khỏi disclosure/RQ1 |

**14 bài INCLUDE ở vòng tiêu đề–tóm tắt (lô R0001–R0050):** R0003, R0004, R0009, R0012, R0016, R0018, R0023, R0025, R0026, R0027, R0029, R0033, R0035, R0042.

**Bài học:**
- NotebookLM cho kết quả khác nhau giữa các lần chạy. Sửa instructions thêm sẽ không loại hết được lỗi, nên cần D4b và người kiểm tra.
- Đếm ký tự tiếng Việt phải dùng Python. Lệnh `wc -m` có thể đếm theo byte, khiến con số bị thổi phồng.

---

## 9. Trạng thái hiện tại và việc tiếp theo

1. **Chốt bản instructions sau Pilot 5**: ghi số phiên bản và ngày chốt, rồi dùng nguyên văn cho mọi lô. Không sửa giữa các lô.
   - *Tùy chọn:* chạy lại lô R0001–R0050 một lần với bản này để xác nhận trước khi chốt.
2. Chạy các lô tiếp theo của file 32 theo trình tự: D1, rồi D4b, rồi người kiểm tra đọc **100% bài INCLUDE** và **10–20% bài EXCLUDE** chọn ngẫu nhiên.
3. Vòng toàn văn: dùng D2 cho từng PDF, gắn TierF-core/TierF-context.
4. Giai đoạn 2: chạy `rank_journals.py` trên danh sách INCLUDE cuối, kiểm tay `final_review.csv`, ghi các bước loại IC7/EC10 vào PRISMA.
5. Báo cáo phương pháp: nêu việc dùng NotebookLM làm người sàng lọc thứ hai, phiên bản instructions, tỷ lệ đồng thuận ở các lượt pilot, và các sửa đổi so với đề cương gốc (mục 3 và 5).

**Vị trí tài liệu:** repo `dnbaoquyen/prompt-architect`, nhánh `claude/blissful-dirac-fjbk2f`, thư mục `docs/notebooklm-slr-screening/`:
- `custom-instructions.txt`
- `README.md` (hướng dẫn, các prompt D0–D5, nhật ký hiệu chỉnh)
- `tools/make_batches.py`
- `tools/rank_journals.py`
