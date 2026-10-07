# Đối chiếu gói nguồn được cung cấp

Checksum ban đầu có 595 dòng. Khi đối chiếu cả phần học liệu còn nằm trên máy
và mẫu DOCX cần phục hồi, **594 tệp khớp**, không còn tệp thiếu.

Gói Downloads không chứa `01_Slide/`; 26 học liệu được lấy từ thư mục học phần
hiện hữu và đều khớp checksum đầu vào. File mẫu DOCX thiếu trong gói mới được
phục hồi từ repo cũ, khớp checksum bản mẫu.

## Một khác biệt cần giữ

File kịch bản trình duyệt trong checksum tên cũ có hậu tố `_V13.docx`, hash:

`ec877240d86adf69c6f899d84838348532f7c8daeb9337f51437d843b70036be`

File DOCX thực tế người dùng cung cấp đã đổi tên, sửa ngày 07/10/2026;
cả bản nằm trong source và bản trong thư mục sản phẩm trùng nhau, hash:

`b6f72384193671f057a1d6e3661dac95d46af7eecb62d18ad98851b4e8747a90`

Repo giữ **file thực tế mới nhất** này tại
`delivery/KICH_BAN_TRINH_DUYET_FEENBERG_NHOM_14.docx` và không sinh lại DOCX
trong lượt chuẩn hóa, nhằm không ghi đè chỉnh sửa thủ công đã được cung cấp.
Checksum đầu vào chỉ được lưu làm bằng chứng, không dùng để tuyên bố mọi
tệp khớp hoặc tự ghi lại file đã khác.

Hai master video, credit V4 và SRT đều giữ nguyên checksum so với gói mới.
