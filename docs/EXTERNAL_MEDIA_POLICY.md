# Chính sách media ngoài Git

## Vì sao không commit media nặng?

GitHub giới hạn file thường ở 100 MiB. Video/audio render còn làm clone, diff và lịch sử Git phình rất nhanh. Vì vậy repo công khai chỉ giữ **mô tả, hash, thông số kỹ thuật và script**; file binary được lưu trong kho nhóm/Drive hoặc ổ lưu trữ riêng.

## Quy tắc kho nhóm

- Giữ quyền chỉnh sửa chỉ cho thành viên nhóm; nếu chia sẻ cho người ngoài, đổi quyền liên kết từ **Editor** sang **Viewer**.
- Không đăng liên kết thư mục có quyền Editor vào README, issue hoặc commit public.
- Không xóa ba file delivery đang có trong Drive. Khi thay file, thêm phiên bản mới và giữ file cũ cho tới khi checksum đã được đối chiếu.
- Tên file nên giữ nguyên đường dẫn tương đối trong manifest để script có thể tìm thấy.

## Khôi phục và xác minh

1. Tải media theo `docs/EXTERNAL_MEDIA_INDEX.csv` về đúng thư mục dự án. Bản Markdown chỉ liệt kê các file nặng từ 50 MiB để ưu tiên upload.
2. Chạy `python3 scripts/verify_external_assets.py --manifest docs/EXTERNAL_MEDIA_INDEX.csv --strict`.
3. Chỉ dùng file có `sha256` khớp. File thiếu hoặc khác hash phải được đánh dấu và tải lại; không âm thầm thay bằng bản nén/độ phân giải thấp.

Manifest chỉ là danh sách kỹ thuật; quyền sử dụng ảnh, footage, nhạc và tài liệu vẫn phải được kiểm tra theo nguồn/giấy phép tương ứng.
