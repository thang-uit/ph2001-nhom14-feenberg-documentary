# Nhật ký dự án — bản công khai

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
