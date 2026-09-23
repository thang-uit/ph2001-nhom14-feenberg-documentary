# Bản đồ repository

```text
.
├── AGENTS.md                         # Quy chuẩn bất biến của dự án
├── README.md                         # Hướng dẫn chính
├── requirements.txt                  # Python dependencies
├── 01_narration.txt                  # Lời thoại sản xuất
├── 03_visual_prompts.txt             # Prompt và negative constraints
├── 04_audio_script.txt               # Kịch bản âm thanh
├── 05_subtitles.srt                  # Phụ đề Unicode dự phòng
├── 06_source_manifest.json           # Provenance học thuật đã bỏ đường dẫn riêng tư
├── 07_fact_check_report.txt          # Audit học thuật
├── 08_subtitle_QA_report.txt         # QA phụ đề
├── 09_visual_QA_report.txt           # QA hình ảnh
├── 10_production_plan.txt            # Hồ sơ delivery V11 R6
├── KICH_BAN_CHI_TIET_*.docx          # Kịch bản Word gửi nhóm
├── qa/v11/02_storyboard_v11.csv      # Storyboard hiện hành, semantic-linked
├── research/
│   ├── claim_ledger.csv              # Claim → nguồn → trạng thái
│   ├── terminology_dictionary.csv    # Từ điển thuật ngữ khóa
│   ├── source_inventory.md            # Kiểm kê nguồn
│   ├── evidence_protocol.md           # Quy tắc phân biệt fact/diễn giải
│   └── narrative_architecture.md     # Kiến trúc lập luận
├── scripts/                          # Pipeline deterministic Python/FFmpeg
├── docs/
│   ├── assets/feenberg-banner.svg    # Banner README có chuyển động nhẹ
│   ├── CONTRIBUTING.md
│   ├── EXTERNAL_MEDIA_POLICY.md
│   ├── EXTERNAL_MEDIA_INDEX.csv      # Chỉ mục SHA-256 cho mọi media ngoài Git
│   ├── HEAVY_FILES_TO_UPLOAD_DRIVE.* # Sinh từ manifest, không upload tự động
│   └── PRODUCTION_HISTORY.md
└── media ngoài Git                  # assets/, audio/, renders/, *.mp4/*.wav…
```

Các thư mục `assets/`, `audio/`, `renders/` và bản PDF/khai thác nguồn ngoài được `.gitignore` có chủ ý. Tên đường dẫn vẫn xuất hiện trong storyboard/script để người dựng biết phải khôi phục gì.
