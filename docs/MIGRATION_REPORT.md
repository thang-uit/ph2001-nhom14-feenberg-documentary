# Báo cáo chuẩn hóa repo — 07/10/2026

## Nguồn và đích

- Nguồn V13 bất biến: gói `Downloads/03_PH2001_TrietHoc/04_BaiTap/` do người dùng cung cấp.
- Đích làm việc: `ph2001-nhom14-feenberg-documentary/` ở gốc học phần.
- Remote: `https://github.com/thang-uit/ph2001-nhom14-feenberg-documentary.git`.
- Nhánh xuất bản: `main`, push bình thường, không force-push.

## Phạm vi thay đổi

- Dùng V13 làm nguồn duy nhất; không dựng lại phim và không chỉnh nội dung master.
- Bỏ tầng `04_BaiTap` khỏi cây làm việc sau khi repo mới đã được kiểm checksum.
- Gom source, tài nguyên đang dùng, credit V4 và sản phẩm giao nộp vào một repo.
- Đổi tên thư mục kỹ thuật `remotion_v13/` thành `remotion/`; cập nhật toàn bộ đường dẫn pipeline.
- Tách `delivery/`, `templates/`, `assets/credit/`, `docs/research/` để người mới định vị nhanh.
- Giữ 55 clip được PLAN V13 tham chiếu, 90 chunk TTS và hai master; không giữ bản phim cũ,
  render trung gian, ZIP cũ hoặc resource không được PLAN dùng.
- Mẫu DOCX cũ được giữ riêng trong `templates/` vì script xuất DOCX cần nó để bảo toàn format.

## Dữ liệu không công khai

- `materials/instructor/`: học liệu gốc của khóa học; giữ trên máy để nghiên cứu, ignore khỏi Git public.
- `docs/local/`: nhật ký sản xuất gốc có email/tài khoản/đường dẫn máy; giữ cục bộ, ignore khỏi Git public.
- Không copy cookie, token, session browser, khóa hay file `.env`.

## Kiểm tra trước khi xóa bản cũ

- Python compile và Bash syntax: PASS.
- `npm run lint` (ESLint + TypeScript): PASS.
- `npm run build` (Remotion bundle, không render phim): PASS.
- Export tạo 127 shot, 55 clip, 217 cue; JSON film và SRT trùng bản V13 đầu vào.
- 55/55 clip được PLAN dùng, mức lặp tối đa 2; đủ 90 cache TTS.
- Credit V4, hai master V13 và DOCX trình duyệt giữ nguyên SHA-256.
- Hai master probe được: 19:40,73, 30p, H.264 High, AAC-LC 48 kHz, BT.709;
  độ phân giải lần lượt 1920×1080 và 2560×1440.
- DOCX trình duyệt và mẫu: ZIP container hợp lệ, không thay đổi format.
- 26 học liệu được kiểm hash với bản gốc trước khi chuyển thư mục.
- Đối chiếu checksum nguồn: 594/595 khớp, một DOCX cập nhật được giữ nguyên;
  xem `docs/transfer/INPUT_VALIDATION.md`.
- Rà staged: không có mẫu bí mật mục tiêu, không có local history/học liệu,
  toàn bộ 155 file media được stage dưới dạng LFS pointer. `git lfs fsck`: PASS.

Không render lại và không chạy lại full audio/video decode trong lượt di chuyển;
hash byte-identical bảo toàn media đã cung cấp, không chứng nhận lại chất lượng
học thuật hay loại bỏ các nguồn vẫn còn cần đối chiếu.

## Dọn thư mục cũ

- Đã xóa vĩnh viễn đúng thư mục `04_BaiTap/` cũ (20,105 GiB dung lượng cấp phát),
  gồm source/version cũ, render và ZIP `Nhom14_Feenberg_TOAN_BO_SOURCE_2026-10-04.zip`.
- 26 học liệu gốc được chuyển sang `materials/instructor/`, kiểm SHA-256 trước
  khi loại bản sao ở `01_Slide/`; không mất học liệu.
- Bỏ `02_TaiLieuThamKhao/` rỗng và bundle QA mới có thể tái tạo.
- Trong học phần hiện chỉ có thư mục repo; gói V13 ở Downloads không bị sửa/xóa.
- Không còn bản ZIP/bản phim cũ cục bộ để khôi phục từ thùng rác. Lịch sử mã
  nguồn Git vẫn được giữ, master/source V13 có bản dự phòng trong Downloads.

## Cảnh báo dependency được giữ minh bạch

`npm audit --omit=dev`: 0 vulnerability. `npm audit` đầy đủ: 10 high thuộc
chuỗi dev-only `@remotion/eslint-config-flat → typescript-eslint@8.21.0 →
fast-glob → micromatch → braces`, advisory `GHSA-vfj7-8cjw-p6xm` (DoS qua
pattern lồng sâu). Gói Remotion hiện tại khóa parser cũ và npm không áp dụng
được override tương thích vào cây khóa. Không giữ override không có tác dụng,
không nâng framework hoặc chạy `audit fix --force`; cần xử lý riêng khi nâng
tool lint. Không dùng toolchain này như một dịch vụ xử lý input không tin cậy.

## Quyết định Git LFS

Media lớn được theo dõi bằng LFS để không tạo blob Git vượt 100 MiB. Đây là công cụ
miễn phí cục bộ; không mua quota, không bypass giới hạn và không coi push thành công
nếu endpoint LFS của GitHub từ chối quota/quyền. Khi push lỗi, giữ commit local,
ghi chính xác lỗi và không giả vờ đã xuất bản media.
