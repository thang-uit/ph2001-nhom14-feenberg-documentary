# Nhật ký dự án — bản công khai

## 2026-10-11 — Phụ đề tiếng Anh

- Tạo `delivery/PhuDe_V13_en.srt` từ lời thoại V13, dịch thủ công theo ngữ cảnh học thuật và giữ nguyên 217 cue/timestamp của phụ đề tiếng Việt.
- Giữ nhất quán các thuật ngữ: democratization, technology governance, technical code, democratic rationalization, participant interests, VNeID.
- Đã kiểm tra số cue, thứ tự cue và toàn bộ timestamp khớp với `delivery/PhuDe_V13.srt`; không thay đổi video, audio hoặc phụ đề tiếng Việt.

## 2026-10-11 — Chuẩn bị metadata YouTube và thumbnail

- Đọc mốc chương từ `audio/vo/v13_vivienne/timeline.json` và `renders/v13/plan.json`, dùng mốc thẻ chương thực tế để tạo chapter timestamps.
- Soạn `docs/youtube_metadata.md` gồm tiêu đề khuyến nghị, hai tiêu đề thay thế, mô tả copy-paste, chapter và hashtag.
- Dựng `delivery/thumbnail_youtube_feenberg_v1.png` ở 1920×1080 từ footage mở đầu quay thật và ảnh Andrew Feenberg có nguồn Wikimedia; chữ tiếng Việt được render hậu kỳ bằng font có đủ glyph Unicode.
- Không thay đổi video master, giọng, phụ đề hoặc credit. Thumbnail có thể tải trực tiếp lên YouTube Studio.

## 2026-10-11 — Đóng gói Git không gồm master 4K

- Xóa master 4K UHD cục bộ khỏi `delivery/` trước khi push để tránh đưa tệp khoảng 2,5 GB lên Git LFS.
- Giữ nguyên hai bản giao nộp Full HD và 2K; metadata YouTube trỏ về bản 2K.
- Thêm quy tắc ignore cho các tệp `delivery/*_4K_2160p.mp4` phát sinh về sau.

## 2026-10-07 — Chuyển sang repo V13 thống nhất

- Dùng source và hai master V13 từ gói Downloads làm nguồn duy nhất; không sửa nội dung, hình ảnh hoặc mix âm thanh.
- Bỏ tầng `04_BaiTap` và `VideoCodex`; gom source, media và sản phẩm vào cùng repo.
- Đổi `remotion_v13/` thành `remotion/`, hồ sơ nguồn thành `docs/research/`, sản phẩm thành `delivery/`.
- Di chuyển credit nguyên bản sang `assets/credit/`; giữ đúng checksum V4.
- Khôi phục mẫu DOCX định dạng ở `templates/` vì gói mới thiếu đầu vào mà script DOCX vẫn tham chiếu.
- Giữ 55 clip đang dùng và 90 chunk TTS V13; không đưa render trung gian, bản phim cũ hay ZIP cũ vào repo.
- Lịch sử sản xuất có tài khoản cá nhân được giữ tại `docs/local/` và ignored. Học liệu gốc được giữ tại `materials/instructor/` và ignored.
- Chỉ thay đường dẫn/hướng dẫn/kiểm tra repo; không chạy TTS, không build DOCX, không render lại toàn phim.
- Trạng thái xuất bản và kết quả kiểm tra được ghi ở `docs/MIGRATION_REPORT.md`.
- Kiểm tra: setup, Python/Bash syntax, ESLint/TypeScript, Remotion bundle,
  checksum, LFS fsck và audit staged đều pass. Không render lại media.
- `04_BaiTap/` cũ đã xóa vĩnh viễn (20,105 GiB); học liệu được chuyển nguyên vẹn.
- Cảnh báo npm dev-only được ghi rõ trong README/báo cáo; runtime audit sạch.
