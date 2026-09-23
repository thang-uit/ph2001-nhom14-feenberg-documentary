# Media nặng không commit Git

Manifest được sinh tự động với ngưỡng **50 MiB**; chỉ các file từ ngưỡng này trở lên được liệt kê.

> Không upload tự động. Hãy kiểm tra ba file delivery trên Drive trước, không xóa file cũ, rồi khôi phục theo đúng `relative_path`.

| Ưu tiên | Đường dẫn tương đối | Dung lượng | Loại | SHA-256 | Hành động |
| --- | --- | ---: | --- | --- | --- |
| P1 — DELIVERY SUPPORT | `CREDIT_TPHCM_OH_YEAH_V4.mp4` | 126.10 MiB | video | `a96f6eb30342562e69b84c5e58c1d28d7b6da591a8969a35b8c013362cab4b93` | Giữ một bản credit V4 đã kiểm hash |
| P1 — VERIFY DELIVERY | `Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4` | 1155.99 MiB | video | `22e39eced2b8454d1ad8fdbe35d7f3d34e7e7a2cce63cc34400d99b513feb788` | Kiểm tra file đã có trên Drive; không upload bản trùng |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_29993_1080.mp4` | 57.74 MiB | video | `dfd7981152d1d0d9e4542fdb75be1019ea8f1a6616dd761ef35ed4a5d20ec619` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_308_1080.mp4` | 60.89 MiB | video | `c58673c8c096b6c0c2974639a08d2efa2ce1e4999bb08704f0f0fc4e24d228a6` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_41165_1080.mp4` | 65.08 MiB | video | `759dc89c5d8712630866f46b244c2ce49e47dfa413f3404f5a9da08053737841` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_4169_1080.mp4` | 59.72 MiB | video | `de40a851dd102104ab2eae9194877659fd90075ae606ded4bbd52abdcfc37008` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_4401_1080.mp4` | 71.13 MiB | video | `b2afbc1c08ad7c93df5559b95072dbcd88d7ac0e20c93d9284244afc96392352` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_4547_1080.mp4` | 76.93 MiB | video | `67455cada6591e3b92a9db73fdfdc73c943d6f841a077c82b4bee4f40205b028` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_4648_1080.mp4` | 52.15 MiB | video | `490ba97c43fb6fd2b2c6614b666878090d3ce6ada4e894946240b0424318e32d` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_4809_1080.mp4` | 79.33 MiB | video | `dfaf13141e7b9d04e606d0c422036327bc3350fbb02f25e8cd39648a874e7d56` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_50598_1080.mp4` | 53.76 MiB | video | `54f46bba3fcb2aed7aadd1eafb24534f2a12ea95e8b272e6c6f9e03351e71d78` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `assets/v11_real/mixkit/mixkit_914_1080.mp4` | 58.90 MiB | video | `c85a6b27feb04779b9c20a67ac70447689f9b9abf3da9dbbc55a7ba6cf0847f3` | Upload các asset được storyboard tham chiếu |
| P2 — REBUILD INPUT | `audio/mix/FULL_MIX_V10_CONTENT_48K.wav` | 265.06 MiB | audio | `917fc44910edd0c0a8b9c38543fe0d1d32bce11d4b724041368267f78b1c9604` | Upload nếu cần tái dựng hoặc rollback |
| P2 — REBUILD INPUT | `audio/music/SCORE_SUNO_V8_48K.wav` | 267.12 MiB | audio | `2a79f53a8ef08135cdb542246a61640d5a524645c50c36775aca6fd207587dbe` | Upload nếu cần tái dựng hoặc rollback |
| P2 — REBUILD INPUT | `audio/sfx/SFX_AMBIENCE_V10_48K.wav` | 265.06 MiB | audio | `afc486ac91132d813c3bc0311a9d1568e7b3da4b8dfbe7650678485fc83f1ed8` | Upload nếu cần tái dựng hoặc rollback |
| P2 — REBUILD INPUT | `audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav` | 265.06 MiB | audio | `e25474d83319a203cb9b308e02973b6cad7ed5f7568161322176c99ea035bdb5` | Upload nếu cần tái dựng hoặc rollback |
| P3 — OPTIONAL PATCH MASTER | `renders/v11_final_r5/PICTURE_MASTER_V11_R5_1080P.mp4` | 483.57 MiB | video | `e6398399b4964ec5867683d5addc759b2e82e2a70e705d299d8f3bad369e9a43` | Hữu ích khi vá picture/subtitle; không bắt buộc để nộp |
| P3 — OPTIONAL PATCH MASTER | `renders/v11_final_r6/PICTURE_MASTER_V11_R6_1080P.mp4` | 510.28 MiB | video | `7133f415e8d682a35aa8c37695773230b8f0a46df055d3a332f53b9a4bf167c1` | Hữu ích khi vá picture/subtitle; không bắt buộc để nộp |
| P3 — OPTIONAL PATCH MASTER | `renders/v11_final_r6/subtitles/SUBTITLE_ALPHA_V11_R6_CONTENT_1080P.mov` | 282.85 MiB | video | `c3566a46d194ce64beb82825a223abbd5d16b54b70a907b4b9d8ac6f878700b9` | Hữu ích khi vá picture/subtitle; không bắt buộc để nộp |
| P3 — OPTIONAL ROLLBACK | `renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R5_LOCKED.mp4` | 1096.84 MiB | video | `8b7e88a4bf2849369bc4f8bf25e721afba332a201b8e8da588a3720bacd39102` | Chỉ upload nếu nhóm muốn giữ đường lui R5 |
| P4 — DO NOT UPLOAD | `renders/v11_final_r6/FINAL_FEENBERG_DOCUMENTARY_V11_R6_candidate.mp4` | 1155.99 MiB | video | `039bfe2c5d7ea00e1eec601f91286e634940549153243bf2ea057c47ce641c83` | Candidate có thể tái sinh; không đưa lên Drive |
| P4 — DUPLICATE | `renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R6_LOCKED.mp4` | 1155.99 MiB | video | `22e39eced2b8454d1ad8fdbe35d7f3d34e7e7a2cce63cc34400d99b513feb788` | Không upload; trùng nội dung với Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4 |
| P4 — DUPLICATE | `renders/v11_final_r5/subtitles/SUBTITLE_ALPHA_V11_R5_CONTENT_1080P.mov` | 282.85 MiB | video | `c3566a46d194ce64beb82825a223abbd5d16b54b70a907b4b9d8ac6f878700b9` | Không upload; trùng nội dung với renders/v11_final_r6/subtitles/SUBTITLE_ALPHA_V11_R6_CONTENT_1080P.mov |
| P4 — DUPLICATE | `renders/v11_final_r6/FINAL_FEENBERG_DOCUMENTARY_V11_R6_candidate_audio_exact.mp4` | 1155.99 MiB | video | `22e39eced2b8454d1ad8fdbe35d7f3d34e7e7a2cce63cc34400d99b513feb788` | Không upload; trùng nội dung với Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4 |

Tổng số file: **24** · Tổng dung lượng (tính cả hardlink theo từng đường dẫn): **8.89 GiB**.

Lệnh tái sinh:

```bash
python3 scripts/build_drive_upload_manifest.py \
  --root . \
  --csv docs/HEAVY_FILES_TO_UPLOAD_DRIVE.csv \
  --markdown docs/HEAVY_FILES_TO_UPLOAD_DRIVE.md
```
