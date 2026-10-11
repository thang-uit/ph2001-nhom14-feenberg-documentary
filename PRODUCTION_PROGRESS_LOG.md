# Nhật ký dự án — bản công khai

## 2026-10-11 — Ổn định ảnh badge README

- Thay bốn URL shields.io bằng SVG tĩnh trong `.github/assets/badges/` để không phụ thuộc dịch vụ ảnh ngoài.
- Giữ nguyên màu sắc và bố cục badge; không thay đổi banner, video, audio, phụ đề hay source dựng phim.

## 2026-10-11 — Chuẩn hóa README song ngữ

- Thêm banner SVG vector cho README, dùng đúng palette ivory–cobalt–vermilion của V13.
- Tổ chức lại README với mục lục, liên kết sản phẩm, hướng dẫn clone/LFS, QA và quy trình dựng.
- Bổ sung bản dịch tiếng Anh tương ứng; không thay đổi master video, lời thoại, phụ đề hay asset dựng phim.

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

## 2026-10-11 — Chốt cây mã nguồn V13

- Cây công khai chỉ giữ source, asset được V13 tham chiếu và hai master giao nộp hiện hành.
- Loại khỏi repo các báo cáo migration/transfer và ghi chú đóng gói trung gian; không còn archive hoặc bản phim thử nghiệm trong cây làm việc.
- Giữ nguyên 55 clip, 90 chunk TTS, credit V4, DOCX, phụ đề Việt/Anh và master Full HD/2K.
- Các ID `V9_`/`Sxxx_` vẫn là asset đầu vào của V13; không xóa theo tên phiên bản khi chưa kiểm tra `PLAN`.
