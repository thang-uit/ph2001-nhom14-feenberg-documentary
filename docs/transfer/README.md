# Ghi chú chuyển máy

Repo này là bản V13 đã chuẩn hóa. Hai file MP4 giao nộp và toàn bộ tài nguyên
media đang được theo dõi bằng Git LFS; sau khi clone cần chạy:

```bash
git lfs install
git lfs pull
```

Thư mục `materials/instructor/` (học liệu khóa học) và `docs/local/` (nhật ký
nội bộ) chỉ được giữ cục bộ, không phát hành trong repo public. Nếu cần dựng
lại từ đầu, xem `README.md` và chạy `./setup.sh`.

File `docs/local/INPUT_CHECKSUM_SHA256.txt` là checksum của gói Downloads ban đầu,
chỉ để đối chiếu nguồn (không public vì chứa tên tệp học liệu nội bộ). Kết quả
đối chiếu được ghi tại `INPUT_VALIDATION.md`; checksum V13 hiện nằm trong
`scripts/verify_repository.py` và `docs/media/manifest.json`.
