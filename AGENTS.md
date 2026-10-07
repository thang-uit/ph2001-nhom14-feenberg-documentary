# AGENTS.md — Quy chuẩn dự án phim Feenberg (Nhóm 14)

Áp dụng cho toàn bộ repo `ph2001-nhom14-feenberg-documentary/`. Đọc kèm `README.md`
(cấu trúc, cách chạy) và phần cuối `PRODUCTION_PROGRESS_LOG.md`.

## 1. Trạng thái hiện hành

- Bản hiện hành: **V13** (06/10/2026), sửa theo góp ý của TS Nguyễn Hữu Sơn về kịch bản V12.
  Sản phẩm: `delivery/` (video 1080p, video 2K, DOCX kịch bản, SRT).
- Nguồn sự thật của lời thoại: `scripts/v13_script_content.py`. DOCX, giọng, phụ đề, hình đều sinh ra từ file này;
  không sửa tay DOCX hay SRT.
- Không khôi phục cấu trúc `04_BaiTap/VideoCodex/`. Repo mới là nguồn làm việc duy nhất từ 07/10/2026.
- Mẫu định dạng DOCX ở `templates/`; đây là đầu vào cần thiết, không phải sản phẩm cũ để xóa.

## 2. Khóa học thuật

- Chủ đề duy nhất: dân chủ hóa thiết kế và quản trị công nghệ theo Andrew Feenberg. Câu hỏi trung tâm: dân chủ nằm ở đâu
  trong một hệ thống công nghệ — được dùng, được góp ý, hay được tham gia và làm thay đổi thiết kế, quản trị?
- Định nghĩa trước khi phân tích (dân chủ, dân chủ hóa, công nghệ, thiết kế, quản trị, giá trị công nghệ).
- Cầu nối Lênin → công nghệ dựa trên việc quyền lực công được thực hiện qua hệ thống kỹ thuật (Feenberg 1992, tr. 301),
  không dựa trên sự giống nhau của câu chữ.
- Tách bạch: dữ kiện đã kiểm chứng ≠ phân tích theo Feenberg ≠ diễn giải/đề xuất của Nhóm 14. Không gán ý của nhóm cho Feenberg.
- Không bịa trích dẫn, số trang, số liệu, điều luật. Mọi nguồn mới phải được đối chiếu và ghi vào `scripts/v13_script_tables.py`
  (CLAIM_ROWS, REFERENCES). Hồ sơ đối chiếu V13: `docs/research/`.
- Còn cần đối chiếu bản in: Lênin Toàn tập t. 33 tr. 123–124; giáo trình CNXHKH (2021) tr. 125–128.

## 3. Hình ảnh

- Một họ chữ duy nhất: Avenir Next. Bảng màu: ivory nền, cobalt cấu trúc, vermilion nhấn, charcoal chữ; sợi chỉ đỏ “tham gia”.
- Đồ họa dựng bằng Remotion (`remotion/`); mọi chuyển động tính theo frame (không CSS transition/animation).
  Nội dung đồ họa nằm trên y = 860 (dải dưới dành cho phụ đề), không đường/mũi tên cắt qua chữ.
- Clip AI (`assets/ai/`) luôn mang nhãn `MINH HỌA BẰNG AI`; footage thật (`assets/real/`) không gắn nhãn.
- Không tạo chân dung Feenberg bằng AI; không dựng giao diện VNeID; không dùng hình tái hiện cho sự kiện lịch sử.
- Mỗi asset dùng tối đa hai lần, hai cửa sổ không trùng. Footage của credit không được dùng trong nội dung.

## 4. Âm thanh và phụ đề

- Một giọng: `fr-FR-VivienneMultilingualNeural`, tốc độ +7%; nghỉ 4 s giữa chương, 0,65 s sau mỗi đoạn.
  Phiên âm chỉ áp dụng cho đầu vào TTS (VNeID, technical code); phụ đề giữ chữ gốc.
- Nhạc nền: `audio/music/SCORE_SUNO_V8_48K.wav` (từ `Feenberg-NhacNen.mp3`), duck dưới giọng; credit dùng nhạc riêng của nó.
- Phụ đề sinh từ timeline giọng, ≤ 2 dòng, Avenir Next Demi 40.

## 5. Credit

- `assets/credit/CREDIT_TPHCM_OH_YEAH_V4.mp4` (54,1 s) giữ nguyên tuyệt đối; SHA-256 `a96f6eb30342562e69b84c5e58c1d28d7b6da591a8969a35b8c013362cab4b93`
  được kiểm trước mỗi lần xuất. Nối bằng crossfade hình + âm 0,8 s. Không thêm chữ/phụ đề lên credit.

## 6. Xuất bản và QA

- Tổng thời lượng 15–20 phút (tính cả credit). Thông số YouTube: xem README.
- Trước khi giao: kiểm full decode (không đen ≥ 1 s, không đứng hình ≥ 8 s), loudness ≈ −16 LUFS, xem khung hình mẫu,
  đối chiếu giọng bằng `qa_v13_whisper.py` + `qa_v13_asr.py` (Whisper hay nghe sai tên riêng — kiểm lại bằng timeline TTS).
- Ghi nhật ký vào `PRODUCTION_PROGRESS_LOG.md` sau mỗi đợt dựng; không ghi mật khẩu, token, cookie.

## 7. Bảo mật và quản lý repo public

- Giữ lịch sử Git, push bình thường lên `main`; không force-push hay tự tăng quota/mua dịch vụ.
- Media hiện hành theo dõi bằng Git LFS. Không nén giảm chất lượng các master/clip để lách giới hạn GitHub.
- Không đăng dữ liệu phiên đăng nhập, cookie, khóa, email tài khoản sản xuất hoặc đường dẫn máy cá nhân.
- Nhật ký lịch sử gốc ở `docs/local/`; học liệu gốc ở `materials/instructor/`: đều ignored, không xóa.
- README không ghi tên cá nhân/giảng viên/thành viên. Tên trong kịch bản và credit hiện hành giữ nguyên theo sản phẩm được cung cấp.
- Không xóa asset chỉ dựa vào tên V9/Sxxx: trước tiên kiểm tra `PLAN` và timeline giọng.
- Trước commit: `python scripts/verify_repository.py`, `npm --prefix remotion run lint`,
  `python scripts/audit_staged.py`, `git diff --cached --check`, `git lfs fsck`.
