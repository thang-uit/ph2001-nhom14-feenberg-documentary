# Hướng dẫn cộng tác

Cảm ơn bạn đã muốn sửa hoặc tái dựng phim của Nhóm 14. Repo này là **source-first**: Git giữ kịch bản, quy tắc học thuật và script; media nặng nằm ngoài Git và được khôi phục bằng manifest SHA-256.

## Quy tắc trước khi sửa

1. Đọc `AGENTS.md` từ đầu đến cuối.
2. Xác định bản hiện hành là V11 R6 và kiểm tra checksum trong báo cáo QA.
3. Không commit video, audio, ảnh render, cache, tài liệu PDF ngoài hoặc log có đường dẫn/tài khoản cá nhân.
4. Không đổi thuật ngữ Feenberg nếu chưa cập nhật `research/terminology_dictionary.csv`, claim ledger và storyboard.
5. Mọi cảnh phải có liên kết ngữ nghĩa với lời thoại; không dùng hình đẹp nhưng lệch luận điểm.

## Luồng làm việc đề nghị

```bash
git clone https://github.com/thang-uit/ph2001-nhom14-feenberg-documentary.git
cd ph2001-nhom14-feenberg-documentary
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/verify_external_assets.py --manifest docs/EXTERNAL_MEDIA_INDEX.csv --strict
```

Sau khi khôi phục media vào đúng đường dẫn tương đối, chạy kiểm tra cú pháp và audit public repo trước khi commit:

```bash
python3 -m py_compile scripts/*.py
python3 scripts/audit_public_repo.py
```

Khi thay timeline, dùng các script V11 với thư mục output riêng. Không ghi đè bản giao nộp cho tới khi QA học thuật, semantic-match, subtitle, audio, full-decode và YouTube đều PASS.

## Commit và pull request

- Commit nhỏ, mô tả rõ mục đích: `docs: clarify Feenberg claim boundaries` hoặc `fix: retime subtitle cue S042`.
- Không đưa secret, cookie, URL project cá nhân, email tài khoản hoặc tài liệu bản quyền vào issue/commit.
- Pull request cần nêu: file đã đổi, ảnh hưởng timeline, cách kiểm tra, checksum trước/sau và trạng thái QA.
- Nếu chỉ có media mới, gửi manifest/hash và hướng dẫn khôi phục; không đẩy media >100 MiB vào Git.
