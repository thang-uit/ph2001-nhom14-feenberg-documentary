# AGENTS.md — Quy chuẩn bắt buộc cho phim Feenberg

## 1. Phạm vi và thứ tự khôi phục công việc

Tệp này áp dụng cho toàn bộ thư mục `VideoCodex` và mọi tệp con.

Mỗi lần bắt đầu hoặc tiếp tục sau khi context bị rút gọn, phải làm theo đúng thứ tự:

1. Đọc toàn bộ `AGENTS.md`.
2. Đọc phần cuối `PRODUCTION_PROGRESS_LOG.md`.
3. Kiểm tra các tệp trạng thái/kế hoạch V11 mới nhất trong `qa/`, `scripts/`, `renders/` và `build/`; V10 chỉ là bản dự phòng và nguồn tham khảo đã được audit.
4. Kiểm tra tiến trình đang chạy trước khi khởi động lại render hoặc tải tài nguyên.
5. Ghi log sau từng batch tạo, tải, kiểm tra, dựng và render.

`Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4` hiện là bản V11 R6 đã khóa và là tên bắt buộc của file MP4 giao nộp từ ngày 20/09/2026. R6 là patch typography cô lập trên chín source-card: bỏ rail xanh xuyên kicker, bỏ disclosure `CROP ĐÃ HIGHLIGHT · NỘI DUNG GỐC GIỮ NGUYÊN` và thay glyph mũi tên không được hỗ trợ ở S070; lời thoại, phụ đề, nhạc, footage và credit được giữ nguyên tuyệt đối. Hardlink R6 nằm tại `renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R6_LOCKED.mp4`; hardlink R5 vẫn được giữ nguyên để rollback tại `renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R5_LOCKED.mp4`. Candidate/cache R6 chỉ được dọn sau khi người dùng xác nhận bản giao nộp.

## 1A. Chỉ thị V11 — ưu tiên cao nhất trong dự án

Các quy tắc dưới đây thay thế mọi quy tắc V10 mâu thuẫn ở phần sau:

- Không hiển thị nhãn `FOOTAGE QUAY THẬT`, `FOOTAGE THẬT` hoặc bất kỳ disclosure nào trên ảnh/video quay thật. Chỉ cảnh AI/tái dựng AI mới mang nhãn nhỏ, thống nhất `MINH HỌA BẰNG AI`.
- Footage dùng trong nội dung chính phải **tách biệt tuyệt đối** với footage của credit: không dùng cùng file, cùng source clip, cùng đoạn quay hoặc biến thể crop của clip credit. QA phải so tập asset nội dung với manifest credit và yêu cầu giao rỗng.
- Tỷ lệ mục tiêu của hình động nội dung chính là khoảng **40% footage quay thật riêng cho nội dung / 60% Veo–Flow đã qua QA**; motion graphic và source-card được thống kê riêng, không dùng để làm sai tỷ lệ.
- Hình phải khớp ngữ nghĩa với câu thoại đang phát. Cấm cityscape, món ăn hoặc B-roll đẹp nhưng không giải thích đúng câu. Mỗi placement phải có trường giải thích `visual_argument_link`; nếu không nêu được hình giúp hiểu ý nào thì thay.
- Loại hoàn toàn mọi người có da sáp/bột/nhựa, CGI/3D/cartoon, mặt/tay giả hoặc màn hình trắng/rỗng vô nghĩa. Các cảnh bị người dùng chỉ ra quanh bản V10 tại khoảng 07:19, 09:44, 10:36, 13:55 và 15:05 phải được truy ngược asset và đưa vào blacklist V11, không chỉ cắt ngắn để che.
- Không tái dùng cảnh chỉ vì từng được dùng ở V8/V9/V10. Ưu tiên mỗi asset xuất hiện đúng một lần; tối đa hai lần chỉ khi là hai cửa sổ chuyển động không trùng và có lý do kể chuyện rõ.
- Phụ đề V11 dùng đúng transcript Vale, tối đa hai dòng, nhưng giảm kích thước vừa phải so với V10; vẫn phải đọc rõ khi chiếu lớp, nằm trong title-safe và không che chủ thể.
- Sửa toàn bộ motion graphic có đường gạch xuyên chữ, shape lệch/cắt và glyph `?` thay ký tự. Typography phải qua QA frame đầu–giữa–cuối; không cho đường/mũi tên chạy qua vùng chữ.
- Bổ sung đoạn ngắn giới thiệu **Andrew Feenberg là ai** bằng thông tin đã kiểm chứng và ít nhất một ảnh người thật có nguồn đáng tin cậy. Không tạo chân dung Feenberg bằng AI, không dùng ảnh người khác và không bịa tiểu sử.
- Credit V11 dùng đúng `CREDIT_TPHCM_OH_YEAH_V4.mp4` dài 54,1 giây: layout bo góc, cột mã học viên ghi `MSHV`, đủ roster và lời cảm ơn. Cấm quay lại credit v1/v2 cũ. Chỉ credit dùng `oh-yeah.mp3`; phải crossfade mềm từ nhạc nội dung. Credit được dựng từ bộ footage credit riêng và bộ đó bị cấm trong nội dung.
- Kịch bản tiếp tục tập trung đúng chủ đề, phải đủ năm tầng: định nghĩa; phân tích triết học và thực tế; luận điểm Nhóm 14; nên/không nên/đề xuất tương lai; chốt vấn đề. Khi thêm tiểu sử Feenberg, chỉ thêm lượng tối thiểu cần định vị học giả, không biến thành phần kể tiểu sử lan man.
- V11 phải Full HD trở lên, không phóng nguồn nhỏ gây nhòe/vỡ, 16:9, Rec.709, H.264 High, AAC-LC 48 kHz, sẵn sàng tải YouTube. Không promote nếu manual QA chuyển động, typography, semantic-match và asset-separation chưa PASS.

## 2. Mục tiêu phim

- Chủ đề duy nhất: **Dân chủ hóa thiết kế và quản trị công nghệ theo Andrew Feenberg**.
- Dạng phim: video essay/tài liệu học thuật điện ảnh, không phải slideshow AI hoặc avatar thuyết trình.
- Thời lượng cuối: từ 15 đến 20 phút, tính cả kết và credit.
- Đầu ra: MP4, 16:9, tối thiểu 1920×1080, H.264 High Profile, AAC-LC 48 kHz, progressive, Rec.709 SDR; hình rõ khi chiếu lớp và sẵn sàng tải YouTube.
- Phần mở đầu phải có lời chào, giới thiệu Nhóm 14 và chủ đề.
- Phần kết phải trở lại câu hỏi trung tâm, rút ra ý nghĩa phương pháp luận, cảm ơn TS Nguyễn Hữu Sơn và người xem; credit như phim điện ảnh.

## 3. Khóa học thuật

Nguồn ưu tiên: tài liệu trong `../../01_Slide`, sau đó là tác phẩm của Feenberg và nguồn học thuật đáng tin cậy. Không thêm dữ kiện hoặc khẳng định học thuật khi chưa kiểm chứng.

Mọi cảnh và lời giải thích phải phục vụ câu hỏi trung tâm:

> Công nghệ có thực sự trung lập, hay những giá trị, lợi ích và quan hệ quyền lực có thể được đưa vào ngay trong quá trình thiết kế và quản trị công nghệ?

Phải giữ chính xác các phân biệt sau:

- sử dụng công nghệ ≠ thiết kế công nghệ;
- tiếp cận công nghệ ≠ tham gia vào quyết định công nghệ;
- `technical code`/mã kỹ thuật ≠ mã nguồn phần mềm;
- tính bất định tương đối của thiết kế ≠ muốn thiết kế thế nào cũng được;
- dân chủ hóa công nghệ ≠ chỉ làm cho nhiều người được dùng công nghệ;
- dữ kiện đã kiểm chứng ≠ diễn giải minh họa ≠ phân tích theo Feenberg;
- lý tính hóa dân chủ không phải phủ nhận hiệu quả kỹ thuật, mà là mở thiết kế và quản trị cho những lợi ích/kinh nghiệm bị gạt ra ngoài trong phạm vi khả thi kỹ thuật.

Không bịa trích dẫn, trang, số liệu, sự kiện, tài liệu, tên riêng hoặc lời của Feenberg. Không gán ví dụ của nhóm thành phát biểu trực tiếp của Feenberg. Nếu chưa xác minh được, đánh dấu trong hồ sơ sản xuất và không đưa lên bản phim như một sự thật.

Lời thoại phải tập trung vào định nghĩa, cơ chế, lập luận, ví dụ và ý nghĩa phương pháp luận; không lan man kể tên học giả chỉ để tạo vẻ học thuật.

### Cấu trúc luận giải V10 bắt buộc

Kịch bản phải dẫn người xem qua năm tầng rõ ràng, có liên kết nhân quả thay vì ghép các mẩu lý thuyết rời rạc:

1. **Lý thuyết và định nghĩa:** giải thích chính xác công nghệ, thiết kế công nghệ, quản trị công nghệ, dân chủ hóa công nghệ, mã kỹ thuật và lý tính hóa dân chủ trong đúng phạm vi cần cho chủ đề.
2. **Phân tích triết học và thực tế:** từ câu hỏi về tính trung lập, chỉ ra cách giá trị, lợi ích và quyền lực có thể kết tinh trong phương án thiết kế và cơ chế quản trị; mọi ví dụ phải phân biệt dữ kiện với phần nhóm diễn giải.
3. **Luận điểm của Nhóm 14:** nêu rõ lập trường của nhóm bằng ngôn ngữ riêng, không gán cho Feenberg và không biến ý kiến nhóm thành chân lý đã được nguồn xác nhận.
4. **Nên làm, không nên làm và đề xuất tương lai:** đề xuất phải nối trực tiếp với phân tích trước đó, khả thi và không đồng nhất dân chủ hóa với bỏ chuyên môn hoặc lấy biểu quyết thay cho mọi quyết định kỹ thuật.
5. **Chốt vấn đề:** trả lời câu hỏi trung tâm có điều kiện, nêu ý nghĩa phương pháp luận và kết bằng lời cảm ơn tự nhiên.

Khi sửa lời thoại, ưu tiên giữ những câu đã đúng và rõ. Không đọc trích dẫn dày đặc trong phim; nguồn và vị trí kiểm chứng vẫn phải được lưu trong claim ledger/fact-check nội bộ.

## 4. Khóa giọng đọc và phụ đề

- Chỉ dùng **một giọng Vale duy nhất** trong toàn phim.
- Nguồn giọng thu duy nhất: `audio/vo/vale_unified_v7/VO_VALE_UNIFIED_V7_48K.wav`.
- Master timeline V9 bắt buộc dùng khi dựng: `audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav`; đây vẫn là đúng master Vale V7, chỉ chèn tám khoảng im lặng số, không ghép giọng khác và không time-stretch.
- Giọng trong sáng, cao vừa, to rõ, tốc độ cuốn hút, phát âm chuẩn tiếng Việt; không ngọng, không hụt chữ, không đổi chất giọng, không “ừm/ờ”, không có đoạn khựng.
- Không time-stretch giọng đến mức biến dạng. Chèn 6–8 khoảng nghỉ hình/nhạc có chủ đích, khoảng 3–5 giây, thay vì đọc liền một mạch.
- Phụ đề phải sinh trực tiếp từ lời thoại cuối, đúng 100% chữ đã đọc, Unicode tiếng Việt chuẩn, tối đa hai dòng, ngắt câu tự nhiên, không che chủ thể hoặc bị cắt bởi safe area.
- Sau mọi thay đổi timeline giọng, phải retime lại SRT, storyboard, âm nhạc và hiệu ứng.

## 5. Visual identity V10 — Civic Daylight / Red Thread

Chỉ dùng một hệ thẩm mỹ xuyên suốt:

- footage tài liệu người thật, ánh sáng ban ngày tự nhiên, ống kính 35/50 mm, tương phản mềm, màu da thật, texture phim rất nhẹ;
- nền warm ivory; màu cấu trúc deep cobalt; màu nhấn vermilion/đỏ gạch; chữ charcoal;
- motif “đường tham gia” đỏ/cobalt đi từ kinh nghiệm người chịu tác động → bàn thiết kế → tiêu chuẩn → quản trị → tái thiết kế;
- đồ họa editorial/architectural nền sáng, đường và mũi tên có động cơ, cân bằng, thẳng hàng và nằm trong safe area;
- chuyển cảnh bằng match cut hành động/vật thể/đường dẫn/giấy/cửa; dissolve có kiểm soát; không glitch, flash hoặc zoom ngẫu nhiên;
- đoạn kết là montage điện ảnh của công nghệ được tái thiết kế và không gian chung thực sự mở, sau đó cảm ơn/credit trên footage chuyển động.

Cấm quay lại phong cách dark-tech obsidian–amber–teal, neon cube, wireframe lưới, thẻ bo góc hàng loạt hoặc template Codex phổ biến. Không sao chép hình, bố cục, cách kể hoặc màu của video Nhóm 5; chỉ dùng video đó làm benchmark để tránh lặp và nhận diện lỗi.

## 6. Quy tắc người thật và Veo/Flow

- Mục tiêu phân bổ hình động của bản V10 là khoảng **30% footage quay thật/người thật có nguồn rõ ràng và 70% cảnh Veo/Flow đã qua QA**. Đồ họa khái niệm và crop tài liệu chỉ dùng đúng lúc cần giải thích, không dùng để lấp thời lượng; bảng kiểm cuối phải báo tỷ lệ theo giây.
- Ưu tiên tận dụng các output Veo/Flow đã tạo và đã tải trước khi tiêu thêm credit. Credit không phải mục tiêu tự thân: clip sai người, sai vật lý, sai logic hoặc lệch style vẫn phải loại.

- Không AI avatar đứng thuyết trình.
- Người phải photoreal live-action: da có lỗ chân lông tự nhiên, tóc/tay/mắt/khuôn mặt đúng giải phẫu, trang phục và chuyển động đời thực.
- Cấm CGI, 3D, hoạt hình, da sáp, da nhựa, doll/plastic/clay/powder skin hoặc look game engine.
- Một shot chỉ có một hành động rõ, hoàn chỉnh, có nguyên nhân và kết quả vật lý hợp lý.
- Cấm loop hoặc reverse hành động người. Không kéo một clip vượt quá chuyển động gốc của nó.
- Cấm nhân vật/vật thể morph, teleport; cấm tay thừa, vật xuyên nhau, cửa tự đổi trạng thái, màn hình phản ứng không khớp thao tác hoặc chuyển động vô mục đích.
- Tránh nhân vật nhìn camera hoặc nói lộ khẩu hình vì phim dùng voice-over.
- Không nhờ Veo sinh chữ, logo, biển hiệu, tài liệu hoặc giao diện cần đọc. Chữ quan trọng và màn hình có nghĩa phải làm hậu kỳ.
- Cảnh lịch sử hoặc tái dựng phải có nhãn nhỏ `MINH HỌA BẰNG AI`; tuyệt đối không trình bày như bằng chứng lưu trữ thật.
- Prompt mỗi clip phải khóa: photoreal live-action, Vietnamese adults khi phù hợp, natural daylight, realistic skin/hair/hands, subtle purposeful camera, one physically complete action, no text/logo/signage, no CGI/3D/wax/plastic skin, no morphing/teleport/reverse/impossible physics.

Mỗi clip mới phải được kiểm tra frame ở tần suất ít nhất 2 fps, và xem chuyển động toàn clip. Bắt buộc kiểm:

- mặt, mắt, da, tóc và tay;
- cửa, màn hình, công cụ và vật thể tương tác;
- continuity đầu–cuối;
- nguyên nhân–kết quả của hành động;
- vật lý, phối cảnh và ánh sáng;
- sự phù hợp với lời thoại và visual identity V9.

Clip không đạt phải loại, không “chữa” bằng crop hoặc cắt quá nhanh để che lỗi.

## 7. Đa dạng cảnh và giới hạn tái sử dụng

- Một asset hình/video được xuất hiện tối đa **hai lần trong toàn phim**; mục tiêu ưu tiên là một lần.
- Không dùng cùng một đoạn chuyển động hai lần nếu người xem có thể nhận ra.
- Mỗi chương phải có đủ establishing shot, hành động con người, chi tiết vật thể, đồ họa giải thích và nhịp thở thị giác.
- Dùng chuỗi nhiều shot logic hoặc extension continuity để có đoạn dài; không loop một clip 8 giây để lấp thời lượng.
- Nếu hết motion asset phù hợp, dùng ảnh photoreal chất lượng cao với pan/parallax tinh tế hoặc đồ họa nguyên bản, thay vì lặp clip lỗi.
- Kế hoạch cuối phải có bảng `asset → scene → timestamp → reuse count → keep/reject`; mọi reuse count phải ≤2.

Các asset bị cấm tuyệt đối trong V9 vì người dùng đã xác định lỗi:

- `assets/editorial_selects/S014_affected_users_1080p.mp4` — người như sáp/bột, lặp quá nhiều;
- `assets/flow_selected/S031_flow_1080p.mp4` — thao tác máy lặp khó chịu;
- `assets/flow_v8_odoo/S031_meta_choice_ramp_1080p.mp4` — logic cửa sai.

Các asset V10 bị cấm bổ sung cho V11 sau phản hồi trực tiếp của người dùng:

- `assets/flow_selected/S063_codesign_kiosk_1080p.mp4` — người mang look sáp/bột và màn hình trắng, khoảng 07:19.
- `assets/flow_selected/S071_flow_1080p.mp4` — người mang look sáp/bột, khoảng 09:44.
- `assets/flow_selected/S073_flow_1080p.mp4` — cận mặt mang look sáp/bột, khoảng 10:36.
- `assets/flow_selected/S013_schedule_exclusion_1080p.mp4` — người mang look sáp/bột, khoảng 13:55.
- `assets/flow_selected/S090_feedback_redesign_retest_1080p.mp4` — người/màn hình mang look CGI, khoảng 15:05.

Mọi asset khác có cùng hiện tượng phải bị loại dù không nằm trong danh sách tên trên. Danh sách này là mức tối thiểu, không phải danh sách duy nhất được phép reject.

Các asset dùng từ 3 lần trở lên trong V8 phải được audit và phân bổ lại; không được tự động giữ lại chỉ vì đã render được.

## 8. Đồ họa, chữ và slide nguồn

- Khi minh họa nội dung từ slide của thầy, crop đúng vùng liên quan và highlight đúng câu/khái niệm được nói tới; người xem phải có đủ thời gian đọc.
- Shape, đường, mũi tên và chữ phải được dựng bằng vector/hậu kỳ, không dùng pseudo-text do AI sinh.
- Căn theo lưới, cân bằng thị giác, không lệch, không cắt, không chạm mép; kiểm safe area ở 1920×1080.
- Đồ họa phải giải thích quan hệ khái niệm, không chỉ trang trí.
- Không dùng disclosure kỹ thuật/AI trong credit. Chỉ dùng nhãn `MINH HỌA BẰNG AI` ở cảnh minh họa cần thiết.

## 9. Âm nhạc, hiệu ứng và mix

- Chỉ dùng nhạc nguồn `Feenberg-NhacNen.mp3`; master hiện tại là `audio/music/SCORE_SUNO_V8_48K.wav`.
- Không dùng Udio và xóa sản phẩm Udio khi đã xác định chắc chắn không còn phụ thuộc trong build.
- Nhạc phải nhẹ, hiện đại, cuốn hút và chạy có chủ đích; duck dưới narration, không lấn giọng.
- Không dùng tiếng lật trang ở cuối; hạn chế whoosh/click trang trí. SFX chỉ tồn tại khi có nguyên nhân hình ảnh rõ.
- Các khoảng nghỉ chương cho phép nhạc nhô lên nhẹ rồi hạ xuống trước khi giọng trở lại.
- Kết phim không dùng loop nhạc nhàm chán; chọn đoạn cao trào phù hợp từ chính nguồn nhạc đã khóa rồi hạ tự nhiên.
- Nội dung chính chỉ dùng `Feenberg-NhacNen.mp3`/master 48 kHz tương ứng. Credit cuối chỉ dùng nhạc từ `oh-yeah.mp3` đã nằm trong artifact V4.
- Khi đi từ kết luận sang credit, phải crossfade hình có chủ đích và crossfade âm thanh: nhạc nội dung hạ dần, `oh-yeah` nâng dần trước hoặc ngay tại điểm nối sao cho không đổi bài đột ngột và không che câu cảm ơn.

## 10. Ending credit V10 đã khóa

- Bỏ hoàn toàn credit cũ của phim chính.
- Dùng đúng artifact có chữ `CREDIT_TPHCM_OH_YEAH_V4.mp4`, dài khoảng 54,1 giây, 1920×1080/30 fps; không dùng bản clean và không tái tạo lại nếu artifact vẫn qua QA.
- Credit V4 được tính vào tổng thời lượng 15–20 phút. Phần nội dung trước credit phải được rút/retime tương ứng để tổng thời lượng không vượt 20 phút.
- Không thêm disclosure kỹ thuật, tên công cụ hoặc ghi chú giọng/hình AI vào credit. Giữ lời cảm ơn thầy và các bạn cùng roster đã khóa trong V4.

## 11. Bảo toàn, dọn dẹp và QA

- Bản V11 R6 hiện hành có SHA-256 khóa `22e39eced2b8454d1ad8fdbe35d7f3d34e7e7a2cce63cc34400d99b513feb788`; phải xác minh checksum này trước và sau mọi thao tác dọn dẹp/promote. R5 rollback có SHA-256 `8b7e88a4bf2849369bc4f8bf25e721afba332a201b8e8da588a3720bacd39102` và không được ghi đè.
- Keep-set R6 được xác định bằng `qa/v11/picture_r6/manifest.json`, `qa/v11/source_cards_r6/manifest.json`, `assets/v11_source_cards_r6/`, picture master R6, candidate delivery QA, audio master Vale/R5, credit V4 và overlay R3. Script dọn an toàn là `scripts/cleanup_latest_v11_r6.py`, dry-run là mặc định; không xóa candidate/rollback trước khi người dùng xác nhận.
- Không promote bản thay thế R6 sang tên giao nộp nếu chưa qua:
  - academic/fact QA;
  - manual visual QA từng shot và toàn phim;
  - asset reuse QA (≤2);
  - physics/continuity/style QA;
  - narration, subtitle và sync QA;
  - audio/loudness/ducking QA;
  - kiểm freeze, black frame và full decode;
  - timing 15–20 phút;
  - tỷ lệ footage thật/Veo được đo và báo cáo;
  - credit V4 cùng crossfade hình/nhạc được xem thủ công ở tốc độ thật;
  - codec/resolution/YouTube QA.
- Nếu một mục chưa đạt, trạng thái là NOT READY và FINAL/hardlink R6 không bị thay thế.

## 12. Nhật ký bắt buộc

Sau mỗi batch, thêm vào `PRODUCTION_PROGRESS_LOG.md`:

- thời gian;
- việc đã làm;
- asset/tệp tạo hoặc thay đổi;
- kết quả QA và lý do reject;
- credit nếu giao diện hiển thị;
- bước tiếp theo chính xác;
- tiến trình/session đang chạy nếu có.

Không ghi mật khẩu, token, cookie hoặc dữ liệu đăng nhập vào log.
