"""Content of the V13 review script (Group 14, Feenberg) — data only.

Narration paragraphs are tuples (label, text). Labels are production tags that
are NOT read aloud. ``[PAUSE x]`` marks a deliberate pause of x seconds; it is
used for timing and stripped from the teacher-facing DOCX.

V13 follows the lecturer's review of the V12 DOCX: the Lenin → technology bridge
rests on public power exercised through technical systems; the seven-step ladder
becomes a rights × participation matrix; a design change is not by itself proof
of democracy; solutions name who supervises, who may request changes and who
must remedy; efficient management and rights protection are not always opposed;
shorter introduction, more Feenberg, one concrete case (AIDS patients and the
redesign of drug trials, analysed by Feenberg); citations re-checked
(qa/v13/citation_audit.md, feenberg_case_research.md, accountability_legal.md).
"""

from __future__ import annotations

LABELS = {
    "MH": "MINH HỌA CỦA NHÓM",
    "KN": "KHÁI NIỆM – CÓ NGUỒN",
    "DK": "DỮ KIỆN ĐÃ KIỂM CHỨNG",
    "FB": "PHÂN TÍCH THEO FEENBERG",
    "N14": "DIỄN GIẢI CỦA NHÓM 14",
    "LD": "LUẬN ĐIỂM CỦA NHÓM 14",
    "DN": "DẪN NHẬP / CHUYỂN Ý",
}

# Each chapter: title, goal, statement type, paragraphs, scenes, checks.
# Scene: (scene_id, para_indexes, visual, on_screen_text, audio)
CHAPTERS = [
    {
        "title": "MỞ ĐẦU: MỘT THAO TÁC, HAI CHIỀU",
        "goal": "Mở bằng một tình huống ngắn: một hệ thống số vừa phục vụ vừa tạo ra dữ liệu về con người. Đặt câu hỏi trung tâm, "
        "chào thầy, giới thiệu Nhóm 14 và chủ đề, rồi đi ngay vào hai định nghĩa nền tảng.",
        "type": "Minh họa của nhóm (tình huống chung, không gắn với ứng dụng cụ thể) và lời dẫn nhập.",
        "paras": [
            ("MH", "Một người mở ứng dụng trên điện thoại, xác thực danh tính, và vài giây sau, giấy tờ của mình hiện lên. "
             "Nhưng cùng thao tác ấy cũng tạo ra dữ liệu: ai xác thực, vào lúc nào, cho thủ tục gì. [PAUSE 0.5]"),
            ("DN", "Vậy dân chủ nằm ở đâu trong một hệ thống như thế? Ở chỗ ai cũng được dùng? Ở chỗ ai cũng được gửi góp ý? "
             "Hay ở chỗ những người chịu tác động thật sự được tham gia, và có thể làm thay đổi cách hệ thống ấy "
             "được thiết kế và quản trị? [PAUSE 0.8]"),
            ("DN", "Kính chào thầy và các bạn. Chúng em là Nhóm 14, với chủ đề: dân chủ hóa thiết kế và quản trị công nghệ "
             "theo Andrew Feenberg. Trước hết, chúng em định nghĩa hai khái niệm nền tảng: dân chủ, và dân chủ hóa. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S01", [0], "Cận bàn tay người thật cầm điện thoại, ánh sáng ban ngày; tiếp theo đồ họa vector: từ thao tác xác thực tỏa ra các nhãn dữ liệu “ai – khi nào – thủ tục gì” chảy về một kho dữ liệu.",
             "AI · KHI NÀO · THỦ TỤC GÌ", "Nhạc nền mở nhẹ, duck dưới lời."),
            ("V13-S02", [1], "Ba câu hỏi xuất hiện lần lượt trên nền ivory; đường đỏ “tham gia” chạy dưới câu hỏi thứ ba.",
             "ĐƯỢC DÙNG? · ĐƯỢC GÓP Ý? · ĐƯỢC THAM GIA VÀ LÀM THAY ĐỔI?", "Khoảng lặng ngắn sau câu hỏi."),
            ("V13-S03", [2], "Thẻ tiêu đề phim; sau đó hai thẻ khái niệm “DÂN CHỦ” và “DÂN CHỦ HÓA” đặt cạnh nhau.",
             "NHÓM 14 · DÂN CHỦ HÓA THIẾT KẾ VÀ QUẢN TRỊ CÔNG NGHỆ THEO ANDREW FEENBERG", "Nhạc nhô nhẹ ở thẻ tiêu đề rồi hạ."),
        ],
        "checks": [
            "Không dựng giao diện VNeID hay bất kỳ ứng dụng thật nào ở phần mở đầu.",
            "Phần dẫn nhập được rút gọn còn ba đoạn; câu hỏi trung tâm được nêu nhưng chưa trả lời.",
        ],
    },
    {
        "title": "DÂN CHỦ LÀ GÌ?",
        "goal": "Giải thích khái niệm dân chủ có nguồn: từ nguyên; quan điểm Mác – Lênin (giá trị xã hội và ba phương diện); Lênin về quyền "
        "ngang nhau trong việc xác định cơ cấu và quản lý nhà nước; Hồ Chí Minh; Hiến pháp 2013. Nêu định nghĩa làm việc ba lớp "
        "và tính lịch sử – cụ thể của dân chủ mà không rơi vào chủ nghĩa tương đối.",
        "type": "Khái niệm có nguồn (giáo trình, kinh điển, Hiến pháp) và diễn giải của Nhóm 14 (định nghĩa làm việc).",
        "paras": [
            ("KN", "Chữ “dân chủ” bắt nguồn từ tiếng Hy Lạp cổ: “demos” là nhân dân, “kratos” là cai trị. "
             "Nghĩa gốc là nhân dân cai trị, về sau được hiểu là quyền lực thuộc về nhân dân. [PAUSE 0.3]"),
            ("KN", "Theo cách tiếp cận Mác – Lênin trong giáo trình Chủ nghĩa xã hội khoa học, dân chủ là một giá trị xã hội "
             "phản ánh những quyền cơ bản của con người, và được hiểu trên ba phương diện. [PAUSE 0.3] "
             "Về quyền lực: dân chủ là quyền lực thuộc về nhân dân, nhân dân là chủ nhân của nhà nước. "
             "Về chế độ xã hội và trong lĩnh vực chính trị: dân chủ là một hình thức, hay hình thái nhà nước. "
             "Về tổ chức và quản lý xã hội: dân chủ là một nguyên tắc. "
             "Dân chủ cũng mang tính lịch sử, phát triển cùng lịch sử xã hội loài người. [PAUSE 0.5]"),
            ("KN", "Trong tác phẩm “Nhà nước và cách mạng”, Lênin viết: chế độ dân chủ là một hình thức nhà nước, "
             "một trong những hình thái của nhà nước. Nhưng mặt khác, chế độ dân chủ có nghĩa là chính thức thừa nhận "
             "quyền bình đẳng giữa những công dân, thừa nhận cho mọi người được quyền ngang nhau trong việc "
             "xác định cơ cấu nhà nước và quản lý nhà nước. [PAUSE 0.3] "
             "Điều nhóm em giữ lại từ định nghĩa này: dân chủ gắn với quyền ngang nhau của công dân "
             "trong việc tổ chức và thực hiện quyền lực công. [PAUSE 0.5]"),
            ("KN", "Ở Việt Nam, Chủ tịch Hồ Chí Minh viết: “Nước ta là nước dân chủ. Bao nhiêu lợi ích đều vì dân. "
             "Bao nhiêu quyền hạn đều của dân.” Hiến pháp năm 2013 khẳng định tất cả quyền lực nhà nước thuộc về Nhân dân; "
             "công dân có quyền tham gia quản lý nhà nước và xã hội, thảo luận và kiến nghị; còn Nhà nước phải công khai, "
             "minh bạch trong việc tiếp nhận và phản hồi ý kiến, kiến nghị của công dân. [PAUSE 0.5]"),
            ("N14", "Từ các nguồn trên, nhóm em dùng một định nghĩa làm việc gồm ba lớp. [PAUSE 0.3] "
             "Lớp chủ thể: quyền quyết định những vấn đề chung thuộc về nhân dân, đặc biệt là những người chịu tác động. "
             "Lớp thiết chế: quyền ấy phải được tổ chức thành quyền được biết, quy trình tham gia, cơ quan đại diện, "
             "cơ chế giám sát, giải trình và kiểm soát quyền lực. "
             "Lớp giá trị: bình đẳng, phẩm giá, bảo vệ quyền con người và khả năng phản biện. [PAUSE 0.5]"),
            ("N14", "Cần nói rõ: dân chủ mang tính lịch sử – cụ thể. Mỗi quốc gia thực hiện dân chủ qua lịch sử, "
             "thể chế và hệ giá trị của mình. Nhưng điều đó không có nghĩa là mỗi nơi muốn hiểu sao cũng được. "
             "Ở đâu, dân chủ cũng phải trả lời được những câu hỏi có thể kiểm tra: người dân có được biết, được bàn, "
             "được quyết định, được giám sát và được bảo vệ hay không. [PAUSE 0.3] "
             "Vì thế, dân chủ không chỉ là đa số biểu quyết; và một biểu mẫu góp ý cũng chưa phải là dân chủ. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S04", [0], "Typography: hai thẻ “demos” và “kratos” ghép thành “quyền lực thuộc về nhân dân”.",
             "DEMOS = NHÂN DÂN · KRATOS = CAI TRỊ, QUYỀN LỰC", "Nhạc nền mỏng."),
            ("V13-S05", [1], "Dải “giá trị xã hội” và ba thẻ phương diện: QUYỀN LỰC – CHẾ ĐỘ XÃ HỘI, CHÍNH TRỊ – TỔ CHỨC, QUẢN LÝ XÃ HỘI; mỗi thẻ hiện khi được đọc.",
             "Nguồn ở chân khung: Giáo trình CNXHKH (Bộ GD&ĐT, 2021), ch. IV", "—"),
            ("V13-S06", [2], "Thẻ trích dẫn Lênin dựng chữ (không phải ảnh chụp), đánh dấu đoạn lược bằng “[…]”; gạch chân “quyền ngang nhau” và “quản lý nhà nước” khi được đọc.",
             "LÊNIN, NHÀ NƯỚC VÀ CÁCH MẠNG (1917), CH. V · TOÀN TẬP, T. 33", "Không SFX."),
            ("V13-S07", [3], "Thẻ trích dẫn Hồ Chí Minh; sau đó bản tóm tắt Hiến pháp 2013 (Điều 2, Điều 28) với highlight đúng câu được đọc.",
             "HỒ CHÍ MINH, “DÂN VẬN” (1949) · HIẾN PHÁP 2013, ĐIỀU 2, 28", "—"),
            ("V13-S08", [4], "Sơ đồ ba vòng đồng tâm: CHỦ THỂ – THIẾT CHẾ – GIÁ TRỊ.",
             "ĐỊNH NGHĨA LÀM VIỆC CỦA NHÓM 14", "—"),
            ("V13-S09", [5], "Footage người thật họp quanh bàn; sau đó năm câu hỏi kiểm tra BIẾT – BÀN – QUYẾT ĐỊNH – GIÁM SÁT – ĐƯỢC BẢO VỆ.",
             "LỊCH SỬ – CỤ THỂ, KHÔNG TƯƠNG ĐỐI", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Giáo trình CNXHKH (2021), ch. IV (khoảng tr. 125–128, đối chiếu bản in trước khi ghi số trang); câu phương diện thứ hai dùng đúng cụm “về chế độ xã hội và trong lĩnh vực chính trị”.",
            "Câu Lênin dùng nguyên văn bản dịch Toàn tập t. 33 (tr. 123–124); trên thẻ trích dẫn đánh dấu đoạn lược.",
            "Câu “điều nhóm em giữ lại” là diễn giải của nhóm, đọc tách khỏi trích dẫn.",
        ],
    },
    {
        "title": "DÂN CHỦ HÓA LÀ GÌ?",
        "goal": "Phân biệt dân chủ (giá trị, thiết chế) với dân chủ hóa (quá trình). Nêu các nấc theo Luật Thực hiện dân chủ ở cơ sở; "
        "loại bỏ cách hiểu sai; nêu điều kiện của tham gia có hiệu lực; dùng ma trận quyền × mức độ tham gia; "
        "chỉ ra rằng một thay đổi thiết kế chưa tự chứng minh tính dân chủ.",
        "type": "Diễn giải của Nhóm 14 dựa trên khái niệm ở Chương 2 và dữ kiện pháp lý đã kiểm chứng.",
        "paras": [
            ("N14", "Nếu dân chủ là giá trị và hình thức tổ chức quyền lực, thì dân chủ hóa là một quá trình: "
             "quá trình mở rộng, trong một cấu trúc cụ thể, năm yếu tố của người chịu tác động: "
             "quyền được biết, quyền tham gia có hiệu lực, quyền phản biện, quyền yêu cầu giải trình, "
             "và khả năng tác động đến quyết định. [PAUSE 0.5]"),
            ("DK", "Luật Thực hiện dân chủ ở cơ sở năm 2022 cũng tách dân chủ thành nhiều nấc: những nội dung phải công khai để người dân biết; "
             "những nội dung Nhân dân bàn và quyết định; những nội dung Nhân dân tham gia ý kiến trước khi cơ quan có thẩm quyền quyết định; "
             "và nội dung kiểm tra, giám sát. [PAUSE 0.3] "
             "Các nấc ấy cho thấy: được biết khác với được bàn; được góp ý khác với được quyết định. [PAUSE 0.5]"),
            ("N14", "Vì vậy, dân chủ hóa không đồng nghĩa với việc ai cũng được dùng một ứng dụng hay gửi ý kiến. "
             "Chuyển một thủ tục giấy lên màn hình là số hóa, chưa phải dân chủ hóa. "
             "Dân chủ hóa cũng không phải thay chuyên môn bằng biểu quyết, và không phải công khai mọi dữ liệu cá nhân. [PAUSE 0.5]"),
            ("N14", "Sự tham gia chỉ có hiệu lực khi có đủ điều kiện: thông tin đủ để hiểu; kênh tiếp cận cho cả người yếu thế; "
             "được nói mà không sợ bị trả đũa; được phản hồi có lý do; có đường kháng nghị; có người chịu trách nhiệm; "
             "và có khả năng sửa quy tắc hay thiết kế khi có bằng chứng về tác động bất công. [PAUSE 0.5]"),
            ("N14", "Để thấy rõ các mức tham gia, nhóm em dùng một ma trận. Hàng là các quyền: được biết, được tham vấn, "
             "được cùng quyết định, và được giám sát, yêu cầu sửa đổi. Cột là mức độ: chưa có, hình thức, hay có hiệu lực. [PAUSE 0.3] "
             "Một hệ thống có thể có hiệu lực ở quyền này, nhưng chỉ hình thức ở quyền khác. "
             "Chẳng hạn, tham vấn có trả lời là mức cao nhất của quyền được tham vấn, nhưng vẫn chưa phải là cùng quyết định: "
             "đó là hai quyền khác nhau. [PAUSE 0.5]"),
            ("N14", "Cũng cần nói rõ: một thay đổi thiết kế chưa tự chứng minh tính dân chủ. Thay đổi có thể chỉ đến từ ý muốn "
             "của người quản lý, từ nhóm có tiếng nói mạnh nhất, thậm chí làm hại nhóm yếu thế. [PAUSE 0.3] "
             "Vì vậy phải hỏi bốn câu: thay đổi ấy xuất phát từ kinh nghiệm của ai; đi qua quy trình nào; "
             "phục vụ lợi ích của ai; và ai chịu trách nhiệm giải trình về nó. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S10", [0], "Đồ họa: DÂN CHỦ (giá trị) và DÂN CHỦ HÓA (quá trình) trên một mũi tên; năm yếu tố hiện dọc mũi tên.",
             "BIẾT · THAM GIA CÓ HIỆU LỰC · PHẢN BIỆN · YÊU CẦU GIẢI TRÌNH · TÁC ĐỘNG ĐẾN QUYẾT ĐỊNH", "—"),
            ("V13-S11", [1], "Bản tóm tắt Luật Thực hiện dân chủ ở cơ sở 2022: bốn nấc, highlight khi được đọc.",
             "LUẬT THỰC HIỆN DÂN CHỦ Ở CƠ SỞ 2022", "—"),
            ("V13-S12", [2], "Năm thẻ “KHÔNG ĐỒNG NGHĨA” lần lượt bị gạch bằng nét vermilion.",
             "DÙNG APP ≠ DÂN CHỦ HÓA · SỐ HÓA ≠ DÂN CHỦ HÓA · …", "—"),
            ("V13-S13", [3], "Footage người thật ở không gian công; chuyển sang checklist bảy điều kiện.",
             "ĐIỀU KIỆN THAM GIA CÓ HIỆU LỰC", "Ambience nhẹ."),
            ("V13-S14", [4], "Ma trận 4 × 3: hàng (BIẾT, THAM VẤN, CÙNG QUYẾT ĐỊNH, GIÁM SÁT & YÊU CẦU SỬA ĐỔI) × cột (CHƯA CÓ, HÌNH THỨC, CÓ HIỆU LỰC); mỗi ô có mô tả ngắn; ô “tham vấn có trả lời” và hàng “cùng quyết định” được tách bằng chú thích “hai quyền khác nhau”.",
             "MA TRẬN QUYỀN × MỨC ĐỘ THAM GIA — KHUNG PHÂN TÍCH CỦA NHÓM 14", "—"),
            ("V13-S15", [5], "Phép thử bốn câu hỏi cho một thay đổi thiết kế: TỪ KINH NGHIỆM CỦA AI? · QUA QUY TRÌNH NÀO? · VÌ LỢI ÍCH CỦA AI? · AI GIẢI TRÌNH?",
             "THAY ĐỔI THIẾT KẾ ≠ BẰNG CHỨNG DÂN CHỦ", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Luật THDC ở cơ sở 2022: Điều 3 (nguyên tắc), Chương II Mục 1–4 (Điều 11, 15, 25, 30); sửa đổi bởi Luật 47/2024/QH15 và Luật 97/2025/QH15, không đánh số lại điều.",
            "Ma trận và phép thử bốn câu hỏi là khung phân tích của nhóm, không phải phân loại của Feenberg hay của luật.",
        ],
    },
    {
        "title": "TỪ TRIẾT HỌC ĐẾN CÔNG NGHỆ: QUYỀN LỰC CÔNG TRONG HỆ THỐNG KỸ THUẬT",
        "goal": "Xây cầu nối triết học → dân chủ → công nghệ dựa trên một thực tế: quyền lực công được thực hiện một phần qua hệ thống kỹ thuật. "
        "Định nghĩa công nghệ, thiết kế công nghệ, quản trị công nghệ, giá trị công nghệ; nêu hai chiều quan hệ dân chủ – công nghệ.",
        "type": "Diễn giải của Nhóm 14; một câu của Feenberg (Inquiry 1992, tr. 301) làm điểm tựa.",
        "paras": [
            ("N14", "Vậy vì sao môn triết học lại hỏi về dân chủ trong công nghệ? [PAUSE 0.3] "
             "Bởi triết học luôn hỏi: ai là chủ thể; quyền lực được chính danh bằng cách nào; giá trị nào đáng được bảo vệ; "
             "và ai chịu trách nhiệm. Dân chủ biến những câu hỏi ấy thành quyền, thiết chế và quy trình cụ thể. [PAUSE 0.5]"),
            ("N14", "Cầu nối từ định nghĩa dân chủ sang công nghệ không nằm ở sự giống nhau của câu chữ, mà ở một thực tế: "
             "ngày nay, quyền lực công được thực hiện một phần qua chính các hệ thống kỹ thuật. [PAUSE 0.3] "
             "Khi cơ quan nhà nước xác thực danh tính, cấp giấy tờ, xét điều kiện hưởng chính sách hay xử lý dữ liệu công dân "
             "qua phần mềm, thì một trường dữ liệu bắt buộc, một tiêu chí phân loại, một mức phân quyền đều quyết định "
             "ai được phục vụ, ai bị từ chối, ai được xem dữ liệu, và ai có thể khiếu nại. "
             "Những quy tắc kỹ thuật ấy tác động như một quyết định quản lý. [PAUSE 0.5]"),
            ("FB", "Feenberg cũng mở đầu một bài viết năm 1992 bằng nhận định: công nghệ là một trong những nguồn quyền lực công "
             "chủ yếu của xã hội hiện đại. [PAUSE 0.3] "
             "Từ đó, nhóm em lập luận: nếu dân chủ là quyền ngang nhau của công dân trong việc quản lý nhà nước, "
             "thì quyền ấy phải vươn tới cả những hệ thống kỹ thuật mà qua đó quyền lực công được thực hiện. [PAUSE 0.5]"),
            ("KN", "Ở đây cần định nghĩa ba khái niệm. Công nghệ không chỉ là thiết bị; đó là hệ thống xã hội – kỹ thuật "
             "gồm máy móc, phần mềm, dữ liệu, tiêu chuẩn, quy trình, con người và thiết chế. "
             "Thiết kế công nghệ là lựa chọn cấu trúc, chức năng, dữ liệu, tiêu chuẩn và quyền truy cập, "
             "không chỉ là trang trí giao diện. Quản trị công nghệ là phân bổ quyền quyết định, trách nhiệm, giám sát, "
             "đánh giá, sửa đổi và kháng nghị trong suốt vòng đời của hệ thống. Còn giá trị công nghệ là những ưu tiên "
             "như hiệu quả, an toàn, công bằng, riêng tư hay phẩm giá, được cụ thể hóa thành lựa chọn kỹ thuật và quản trị. [PAUSE 0.5]"),
            ("N14", "Từ đây, dân chủ và công nghệ gặp nhau theo hai chiều. Chiều thứ nhất: ứng dụng công nghệ để thực hiện dân chủ "
             "trong quản trị xã hội, giúp người dân được biết thông tin, gửi kiến nghị, giám sát và khiếu nại thuận tiện hơn. [PAUSE 0.3] "
             "Chiều thứ hai: dân chủ hóa chính công nghệ, tức là những người chịu tác động được tham gia vào việc thiết kế "
             "và quản trị các hệ thống ấy. [PAUSE 0.3] Hai chiều gắn với nhau: một nền tảng số chỉ thật sự phục vụ dân chủ "
             "khi người dùng nó có tiếng nói trong cách nó được làm ra và vận hành. [PAUSE 0.5]"),
            ("N14", "Từ đó rút ra một phân biệt then chốt: một người có thể sử dụng một hệ thống mỗi ngày, "
             "mà không hề có tiếng nói trong việc thiết kế hay quản trị hệ thống ấy. "
             "Đây chính là chỗ Andrew Feenberg bước vào. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S16", [0], "Sơ đồ chuỗi bắt buộc dựng dần: TRIẾT HỌC (chủ thể, quyền lực, giá trị, trách nhiệm) → NỘI HÀM DÂN CHỦ; mỗi mũi tên có nhãn.",
             "CHỦ THỂ · CHÍNH DANH · GIÁ TRỊ · TRÁCH NHIỆM", "—"),
            ("V13-S17", [1], "Footage người thật làm thủ tục và kỹ sư bên màn hình; đồ họa “quyền lực công → hệ thống kỹ thuật”: bốn hoạt động (xác thực, cấp giấy tờ, xét điều kiện, xử lý dữ liệu) đi qua bốn quy tắc (trường bắt buộc, tiêu chí phân loại, mức phân quyền, kênh khiếu nại) và ra bốn hệ quả (được phục vụ, bị từ chối, được xem dữ liệu, được khiếu nại).",
             "QUY TẮC KỸ THUẬT TÁC ĐỘNG NHƯ MỘT QUYẾT ĐỊNH QUẢN LÝ", "Ambience văn phòng rất nhẹ."),
            ("V13-S18", [2], "Thẻ trích dẫn Feenberg (1992, tr. 301) và mũi tên lập luận của nhóm: QUYỀN NGANG NHAU TRONG QUẢN LÝ NHÀ NƯỚC → VƯƠN TỚI HỆ THỐNG KỸ THUẬT.",
             "FEENBERG (1992), INQUIRY 35, TR. 301 · LẬP LUẬN CỦA NHÓM 14", "—"),
            ("V13-S19", [3], "Ba thẻ định nghĩa: CÔNG NGHỆ · THIẾT KẾ · QUẢN TRỊ; sơ đồ chuỗi đi tiếp tới QUYỀN LỰC CÔNG → THIẾT KẾ → QUẢN TRỊ.",
             "BA ĐỊNH NGHĨA LÀM VIỆC", "—"),
            ("V13-S20", [4], "Hai thẻ CHIỀU 1 và CHIỀU 2, hai mũi tên ngược chiều nối nhau.",
             "HAI CHIỀU · CHIỀU 1 CHỈ CÓ HIỆU LỰC KHI CHIỀU 2 ĐƯỢC BẢO ĐẢM", "—"),
            ("V13-S21", [5], "Footage người dùng điện thoại; sơ đồ chuỗi hoàn chỉnh với chú thích “sử dụng chưa phải là tham gia”.",
             "SỬ DỤNG ≠ THAM GIA THIẾT KẾ VÀ QUẢN TRỊ", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Cầu nối dựa trên việc hệ thống kỹ thuật tham gia thực hiện quyền lực công, không dựa trên sự tương đồng giữa chữ “cơ cấu” và chữ “thiết kế”.",
            "Câu Feenberg: “Technology is one of the major sources of public power in modern societies” (Inquiry 35, 1992, tr. 301). Feenberg không dẫn Lênin; bước nối với định nghĩa Lênin là lập luận của nhóm, đọc tách riêng.",
        ],
    },
    {
        "title": "ANDREW FEENBERG VÀ LÝ THUYẾT PHÊ PHÁN VỀ CÔNG NGHỆ",
        "goal": "Giới thiệu Feenberg vừa đủ; trình bày đúng: hai trục và bốn lập trường; tính bất định tương đối; mã kỹ thuật; "
        "năng lực hành động của người dùng; hợp lý hóa dân chủ; lợi ích của người tham gia và ba con đường can thiệp dân chủ; "
        "mở rộng dân chủ vào lĩnh vực được công nghệ trung giới; sáng kiến và tham gia thay vì bầu cử giữa các thiết bị.",
        "type": "Dữ kiện tiểu sử tối thiểu và phân tích theo Feenberg (S01, S03 và các bài đã kiểm chứng).",
        "paras": [
            ("DK", "Andrew Feenberg là nhà triết học công nghệ người Mỹ, giáo sư danh dự tại Đại học Simon Fraser, Canada, "
             "gắn với lý thuyết phê phán về công nghệ. [PAUSE 0.3]"),
            ("FB", "Feenberg xếp các quan niệm về công nghệ theo hai trục: trung tính hay mang giá trị; tự trị hay do con người kiểm soát. "
             "Thuyết công cụ coi công nghệ là phương tiện trung tính; thuyết tất định coi công nghệ tự vận động và định hình xã hội. "
             "Lý thuyết phê phán cho rằng công nghệ vừa mang giá trị, vừa có thể được con người định hướng. "
             "Theo ông, vấn đề là ta chưa có những thiết chế phù hợp để kiểm soát công nghệ, "
             "và công nghệ có thể được đưa vào một quá trình thiết kế, phát triển dân chủ hơn. [PAUSE 0.5]"),
            ("FB", "Ý thứ nhất là tính bất định tương đối của thiết kế. Trong cùng ràng buộc kỹ thuật, thường có nhiều phương án khả thi. "
             "Nhưng “tương đối” nghĩa là không phải muốn thiết kế thế nào cũng được. [PAUSE 0.3]"),
            ("FB", "Ý thứ hai là mã kỹ thuật, hay “technical code”. Đây không phải mã nguồn phần mềm. "
             "Mã kỹ thuật là cách những quan hệ xã hội, lợi ích và một chân trời văn hóa lắng đọng vào các tham số thiết kế. "
             "Khi đã ổn định, kết quả của những lựa chọn và xung đột xã hội lại hiện ra như thể đó là “tất yếu kỹ thuật”. [PAUSE 0.3]"),
            ("FB", "Ý thứ ba là năng lực hành động của người dùng. Feenberg nêu ví dụ: thư điện tử trên Internet do những người dùng thành thạo "
             "đưa vào, vốn không có trong kế hoạch ban đầu của nhà thiết kế; vậy mà trong bài giảng năm 2003, ông nhận xét "
             "đó đã là chức năng được dùng nhiều nhất của Internet. "
             "Năng lực ấy có thật, nhưng có điều kiện, không phải toàn quyền kiểm soát. [PAUSE 0.3]"),
            ("FB", "Ý thứ tư là hợp lý hóa dân chủ: mở rộng tính hợp lý kỹ thuật để tính đến bối cảnh, chi phí và kinh nghiệm "
             "từng bị gạt ra ngoài, thông qua sáng kiến, phản kháng và tham gia của người chịu tác động, "
             "có thể dẫn tới thay đổi thực hành hoặc thiết kế. "
             "Nó không phủ nhận hiệu quả; nó hỏi thêm: hiệu quả cho ai, và chi phí do ai gánh. [PAUSE 0.5]"),
            ("FB", "Feenberg gọi những gì người chịu tác động đòi hỏi là “lợi ích của người tham gia”: ai bị cuốn vào một hệ thống "
             "kỹ thuật đều có những lợi ích nảy sinh từ chính vị trí ấy. [PAUSE 0.3] "
             "Các lợi ích ấy đi vào công nghệ qua ba con đường: tranh luận công khai về công nghệ, buộc thiết kế phải thay đổi; "
             "đối thoại giữa chuyên gia và người dùng, như trong thiết kế có sự tham gia; "
             "và chiếm dụng sáng tạo, khi người dùng tạo ra chức năng mới cho công nghệ sẵn có. [PAUSE 0.5]"),
            ("FB", "Vậy Feenberg hiểu dân chủ trong công nghệ thế nào? Trong các văn bản nhóm sử dụng, ông không đưa ra định nghĩa "
             "dân chủ tổng quát, mà đặt vấn đề mở rộng dân chủ. Feenberg nhắc lại lập luận của Mác: dân chủ phải được mở rộng "
             "từ lĩnh vực chính trị sang thế giới lao động. Còn ông lập luận: nếu dân chủ không vươn tới những lĩnh vực đời sống "
             "được công nghệ trung giới, giá trị sử dụng của nó sẽ suy giảm và sự tham gia sẽ tàn lụi. [PAUSE 0.3]"),
            ("FB", "Feenberg cũng nói rõ: tổ chức bầu cử giữa các thiết bị hay các bản thiết kế là điều không hợp lý. "
             "Theo ông, dân chủ hóa công nghệ trước hết không phải vấn đề quyền pháp lý, mà là vấn đề sáng kiến và tham gia. "
             "Hình thức pháp lý sẽ trống rỗng nếu không xuất phát từ kinh nghiệm và nhu cầu của những cá nhân "
             "đang kháng cự một bá quyền mang tính kỹ thuật. [PAUSE 0.3]"),
            ("N14", "Đặt vào bối cảnh Việt Nam, nhóm em đọc ý này như sau: quy định pháp luật về quyền tham gia là khung cần thiết, "
             "nhưng chỉ có ý nghĩa khi người dân thực sự sử dụng được nó, và khi tiếng nói của họ có đường đi tới quyết định thiết kế. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S22", [0], "Ảnh thật Andrew Feenberg có nguồn (Wikimedia Commons, Beatrice Murch, CC BY-SA 3.0), pan rất nhẹ; thẻ danh tính tối giản.",
             "ANDREW FEENBERG · GIÁO SƯ DANH DỰ, ĐẠI HỌC SIMON FRASER · ghi nguồn ảnh", "—"),
            ("V13-S23", [1], "Ma trận 2×2 (trung tính/mang giá trị × tự trị/con người kiểm soát) dựng dần; ô “Lý thuyết phê phán” sáng lên; câu về thiết chế (S01 tr. 9).",
             "THUYẾT CÔNG CỤ · THUYẾT TẤT ĐỊNH · THUYẾT THỰC CHẤT · LÝ THUYẾT PHÊ PHÁN", "—"),
            ("V13-S24", [2], "Đồ họa: ba phương án khả thi trong khung ràng buộc kỹ thuật.",
             "BẤT ĐỊNH TƯƠNG ĐỐI ≠ TÙY Ý", "—"),
            ("V13-S25", [3], "Đồ họa lắng đọng: các lớp quan hệ xã hội – lợi ích – chân trời văn hóa đông lại thành tham số thiết kế.",
             "MÃ KỸ THUẬT ≠ MÃ NGUỒN", "—"),
            ("V13-S26", [4], "Minh họa tái dựng phòng máy tính thập niên 1990 (nhãn MINH HỌA BẰNG AI); thẻ trích ý S01 tr. 10 về email.",
             "NĂNG LỰC HÀNH ĐỘNG CỦA NGƯỜI DÙNG · S01, TR. 10", "—"),
            ("V13-S27", [5], "Đồ họa: vòng “tính hợp lý kỹ thuật” mở rộng bao lấy bối cảnh, chi phí, kinh nghiệm, người chịu tác động.",
             "HỢP LÝ HÓA DÂN CHỦ — FEENBERG 1992 GỌI LÀ “SUBVERSIVE RATIONALIZATION” (TR. 320)", "—"),
            ("V13-S28", [6], "Đồ họa: “lợi ích của người tham gia” ở trung tâm, ba con đường tỏa ra: TRANH LUẬN CÔNG KHAI · ĐỐI THOẠI CHUYÊN GIA – NGƯỜI DÙNG · CHIẾM DỤNG SÁNG TẠO, mỗi con đường dẫn tới “thiết kế thay đổi”.",
             "FEENBERG 1992 (PHILOSOPHICAL FORUM, TR. 217–218); BAKARDJIEVA & FEENBERG 2002, TR. 187", "—"),
            ("V13-S29", [7], "Thẻ trích ý S03 tr. 301–302: Mác và việc mở rộng dân chủ; dân chủ vào “các lĩnh vực được công nghệ trung giới”.",
             "FEENBERG (1992), INQUIRY 35, TR. 301–302", "—"),
            ("V13-S30", [8, 9], "Hai cột: KHÔNG PHẢI bầu cử giữa thiết bị / MÀ LÀ sáng kiến và tham gia (S01 tr. 10; S03 tr. 318); chuyển sang footage người thật cùng thảo luận.",
             "KHÔNG PHẢI BẦU CỬ GIỮA CÁC THIẾT BỊ · SÁNG KIẾN VÀ THAM GIA", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Không tạo chân dung Feenberg bằng AI; ảnh có nguồn và giấy phép CC BY-SA 3.0.",
            "Câu về Mác là Feenberg thuật lại lập luận của Mác (S03 tr. 301), không phải trích dẫn trực tiếp tác phẩm của Mác.",
            "Ví dụ email: nguồn viết “today” trong bài giảng tháng 6/2003; lời thoại nói “trong bài giảng năm 2003, ông nhận xét”.",
            "“Hợp lý hóa dân chủ”: bài Inquiry 1992 dùng thuật ngữ “subversive rationalization”; tên “democratic rationalization” xuất hiện ở các bản sau.",
            "Ba con đường can thiệp lấy theo Bakardjieva & Feenberg (2002), tr. 187.",
        ],
    },
    {
        "title": "MỘT TÌNH HUỐNG: PHẢN HỒI LÀM THAY ĐỔI THIẾT KẾ",
        "goal": "Dùng một tình huống có thật, do chính Feenberg phân tích, để cho thấy phản hồi của người chịu tác động dẫn đến sửa thiết kế "
        "như thế nào: thiết kế ban đầu → kinh nghiệm bị gạt ra → kênh lên tiếng → thay đổi thể chế có ngày tháng → giới hạn còn lại; "
        "sau đó đặt tình huống vào phép thử bốn câu hỏi của Chương 3.",
        "type": "Dữ kiện lịch sử đã kiểm chứng (FDA, Federal Register), phân tích của Feenberg, và diễn giải của Nhóm 14.",
        "paras": [
            ("FB", "Hãy xem một tình huống chính Feenberg đã phân tích: người bệnh AIDS ở Mỹ cuối thập niên 1980. [PAUSE 0.3] "
             "Khi đó, thuốc mới chủ yếu chỉ đến được với người bệnh qua các thử nghiệm lâm sàng có đối chứng. "
             "Số chỗ rất ít, điều kiện tham gia rất chặt, và một phần người tham gia nhận giả dược. [PAUSE 0.3] "
             "Theo Feenberg, thiết kế ấy coi người bệnh là đối tượng thụ động; mong muốn được tham gia nghiên cứu "
             "của họ bị xem là không hợp lý. [PAUSE 0.5]"),
            ("DK", "Nhưng người bệnh đã lên tiếng tập thể. Họ tự học về thuốc và về quy trình thử nghiệm, đưa ra những yêu cầu cụ thể "
             "tới cơ quan quản lý, và biểu tình, như cuộc tập trung của hơn một nghìn người trước trụ sở "
             "Cục Quản lý Thực phẩm và Dược phẩm Hoa Kỳ vào tháng 10 năm 1988. [PAUSE 0.3] "
             "Dưới sức ép ấy, thể chế thay đổi từng bước. Năm 1987, một quy định cho phép dùng thuốc đang thử nghiệm "
             "để điều trị ngoài thử nghiệm chính thức. Năm 1992, chính sách “đường song song” cho người không vào được thử nghiệm "
             "vẫn được dùng thuốc, cùng cơ chế phê duyệt nhanh. [PAUSE 0.5]"),
            ("FB", "Feenberg tóm lại: vì không thể có được sự hợp tác của người bệnh theo quy trình cũ, người bệnh cuối cùng đã buộc "
             "thiết kế thử nghiệm phải thay đổi, thêm mục tiêu chăm sóc số đông người bệnh vào mục đích khoa học. "
             "Ông coi đó là thay đổi mang tính dân chủ và tiến bộ. [PAUSE 0.3] "
             "Nhưng đó không phải chiến thắng trọn vẹn: giới nghiên cứu lo dữ liệu kém tin cậy hơn, và tranh luận "
             "giữa tiếp cận nhanh với kiểm chứng khoa học vẫn tiếp diễn. [PAUSE 0.5]"),
            ("N14", "Đặt tình huống này vào bốn câu hỏi ở trên, ta thấy vì sao đây là dân chủ hóa, chứ không chỉ là một thay đổi thiết kế. "
             "Thay đổi xuất phát từ kinh nghiệm của chính người chịu tác động; đi qua tranh luận công khai và đối thoại với chuyên gia; "
             "phục vụ lợi ích của số đông người bệnh mà không bỏ yêu cầu kiểm chứng khoa học; "
             "và được thể chế hóa thành quy định có cơ quan chịu trách nhiệm. [PAUSE 0.3] "
             "Đó là con đường từ phản hồi đến sửa thiết kế. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S31", [0], "Đồ họa “thiết kế ban đầu”: sơ đồ thử nghiệm có đối chứng (ít chỗ · điều kiện chặt · nhóm giả dược), người bệnh đứng ngoài hàng rào; nhãn “đối tượng thụ động”.",
             "MỸ, CUỐI THẬP NIÊN 1980 · TÌNH HUỐNG DO FEENBERG PHÂN TÍCH (1992; 2008)", "—"),
            ("V13-S32", [1], "Dòng thời gian có ngày tháng: kinh nghiệm → tự học → yêu cầu cụ thể → biểu tình (10/1988) → quy định 1987 (treatment IND) → 1992: đường song song, phê duyệt nhanh. Không dùng ảnh tái dựng bằng AI cho sự kiện lịch sử.",
             "1987 · 1988 · 1992 — NGUỒN: FDA; FEDERAL REGISTER 52 FR 19466, 57 FR 13250, 57 FR 58942", "—"),
            ("V13-S33", [2], "Thẻ trích ý Feenberg (2008, tr. 25): “buộc thiết kế thử nghiệm thay đổi… thêm mục tiêu chăm sóc”; cột giới hạn: dữ liệu kém tin cậy, tranh luận tiếp diễn.",
             "FEENBERG (2008), SOCIAL EPISTEMOLOGY 22(1), TR. 25", "—"),
            ("V13-S34", [3], "Phép thử bốn câu hỏi của Chương 3, lần lượt được đánh dấu bằng câu trả lời của tình huống; sợi chỉ đỏ đi từ PHẢN HỒI đến SỬA THIẾT KẾ.",
             "TỪ PHẢN HỒI ĐẾN SỬA THIẾT KẾ", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Không nói biểu tình năm 1988 dẫn tới quy định năm 1987; dùng cách nói của Feenberg: dưới sức ép chính trị trong những năm 1987–1989.",
            "Không nói giả dược bị bãi bỏ: “đường song song” chạy song song với thử nghiệm có đối chứng.",
            "Không dùng hình ảnh AI tái dựng sự kiện lịch sử; tình huống được trình bày bằng đồ họa và nguồn.",
        ],
    },
    {
        "title": "VÍ DỤ PHÂN TÍCH: VNeID VÀ QUẢN TRỊ DỮ LIỆU CÔNG DÂN",
        "goal": "Kiểm tra khung lý thuyết trên một hệ thống có thật, theo bốn lớp: dữ kiện – câu hỏi dân chủ – phân tích theo Feenberg – giới hạn. "
        "Trả lời: dân chủ vào giai đoạn nào, ai quyết định; và chỉ ra rằng quản lý hiệu quả và bảo vệ quyền người dân không luôn đối lập.",
        "type": "Dữ kiện pháp lý đã kiểm chứng; câu hỏi phân tích và đề xuất của Nhóm 14; phân tích theo Feenberg. "
        "Nhóm không khẳng định VNeID đang có hay thiếu cơ chế nào khi chưa có nguồn.",
        "paras": [
            ("DK", "Nhóm em chọn một ví dụ gần gũi: VNeID, ứng dụng định danh quốc gia. Luật Căn cước định nghĩa đây là ứng dụng "
             "trên thiết bị số để phục vụ định danh điện tử và xác thực điện tử trong giải quyết thủ tục hành chính, "
             "dịch vụ công và các giao dịch khác trên môi trường điện tử. [PAUSE 0.3]"),
            ("N14", "Đây là ví dụ phân tích về quản trị dữ liệu công dân. "
             "Nhóm không kết luận VNeID “là dân chủ” hay “không dân chủ”, và một ứng dụng cũng không đại diện "
             "cho toàn bộ nền dân chủ Việt Nam. [PAUSE 0.5]"),
            ("N14", "Đặt ma trận vào hệ thống này, ta hỏi: người dân được biết dữ liệu nào được thu thập, để làm gì, ai được truy cập? "
             "Họ tham gia từ khi xác định nhu cầu, hay chỉ sau khi hệ thống đã vận hành? "
             "Khi dữ liệu sai, có đường kháng nghị không, và ai kiểm tra người vận hành? [PAUSE 0.5]"),
            ("DK", "Pháp luật hiện hành đã đặt nền cho một số câu trả lời. Hiến pháp bảo đảm quyền bất khả xâm phạm về đời sống riêng tư "
             "và bí mật cá nhân. Luật Bảo vệ dữ liệu cá nhân năm 2025 quy định quyền được biết về việc xử lý dữ liệu, đồng ý hoặc rút lại đồng ý, "
             "xem và yêu cầu chỉnh sửa, khiếu nại và khởi kiện. Đồng thời, luật cho phép xử lý dữ liệu không cần sự đồng ý "
             "trong một số trường hợp, trong đó có phục vụ hoạt động quản lý nhà nước theo quy định của pháp luật, "
             "và khi đó phải có cơ chế giám sát. [PAUSE 0.5]"),
            ("FB", "Đọc theo Feenberg, những lựa chọn tưởng như thuần kỹ thuật, như trường dữ liệu bắt buộc, phương thức xác thực, "
             "phân quyền xem, thời hạn lưu nhật ký, đều là nơi các ưu tiên có thể lắng đọng thành mã kỹ thuật. "
             "Một thiết kế tối ưu cho người có điện thoại thông minh và kỹ năng số có thể vô tình đẩy người cao tuổi, người khuyết tật "
             "hay người không có thiết bị ra ngoài lề. Câu hỏi là: kinh nghiệm của ai được tính đến khi thiết kế. [PAUSE 0.5]"),
            ("N14", "Vậy đưa dân chủ vào giai đoạn nào? Theo nhóm: vào mọi giai đoạn, bằng cơ chế khác nhau. "
             "Xác định nhu cầu: lập bản đồ người chịu tác động. Thiết kế: công khai mục đích, dữ liệu, tiêu chí. "
             "Thử nghiệm: thử với nhóm dễ bị bỏ sót. Vận hành: kênh hỗ trợ, chỉnh sửa, khiếu nại. "
             "Giám sát: kiểm tra độc lập. Tái thiết kế: phản hồi phải có khả năng làm đổi quy tắc. [PAUSE 0.3]"),
            ("N14", "Người quyết định cuối cùng vẫn là cơ quan có thẩm quyền; kỹ sư vẫn chịu trách nhiệm chuyên môn. "
             "Dân chủ hóa không trao toàn quyền mọi chi tiết, càng không cho ai đọc dữ liệu của người khác. "
             "Nó đòi hỏi tiếng nói của người chịu tác động có đường đi tới quyết định, và quyết định phải có lý do. [PAUSE 0.5]"),
            ("N14", "Người ta thường nghĩ quản lý hiệu quả và bảo vệ quyền người dân là hai đầu của một cán cân. "
             "Thực tế không luôn như vậy: thiết kế tốt có thể cải thiện cả hai. [PAUSE 0.3] "
             "Luật đã yêu cầu chỉ thu thập dữ liệu đúng phạm vi, đúng mục đích cụ thể, rõ ràng: thu ít hơn thì lộ ít hơn, "
             "và tốn ít chi phí lưu trữ hơn. Nhật ký truy cập vừa giúp người dân biết ai đã xem hồ sơ của mình, "
             "vừa giúp người quản lý phát hiện việc tra cứu trái phép. Một kênh sửa dữ liệu sai dễ dùng vừa bảo vệ quyền, "
             "vừa làm cơ sở dữ liệu chính xác hơn, vì người dân thường là người phát hiện lỗi sớm nhất. [PAUSE 0.3] "
             "Còn khi có xung đột thật, Hiến pháp chỉ cho phép hạn chế quyền theo quy định của luật, và chỉ khi thật cần thiết. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S35", [0], "Bản tóm tắt định nghĩa trong Luật Căn cước (khoản 18 Điều 3); không dựng giao diện VNeID; ghi rõ “hình minh họa, không phải giao diện thật”.",
             "LUẬT CĂN CƯỚC 2023 (SĐ, BS 2025), ĐIỀU 3 KHOẢN 18", "—"),
            ("V13-S36", [1], "Thẻ phạm vi trên nền ivory, khung viền cobalt.",
             "VÍ DỤ PHÂN TÍCH — KHÔNG PHẢI KẾT LUẬN VỀ TOÀN BỘ NỀN DÂN CHỦ", "—"),
            ("V13-S37", [2], "Bốn câu hỏi xếp thành cột, gắn với các hàng của ma trận ở Chương 3.",
             "BIẾT GÌ? · THAM GIA Ở ĐÂU? · KHÁNG NGHỊ? · AI KIỂM TRA NGƯỜI VẬN HÀNH?", "—"),
            ("V13-S38", [3], "Bản tóm tắt Hiến pháp 2013 Điều 21; Luật Bảo vệ dữ liệu cá nhân 2025 Điều 4 khoản 1 và Điều 19.",
             "HIẾN PHÁP 2013, ĐIỀU 21 · LUẬT BVDLCN 2025, ĐIỀU 4, ĐIỀU 19", "—"),
            ("V13-S39", [4], "Footage người thật: người cao tuổi với thiết bị số; đồ họa các tham số thiết kế “đông lại”.",
             "KINH NGHIỆM CỦA AI ĐƯỢC TÍNH ĐẾN?", "Ambience nhẹ."),
            ("V13-S40", [5, 6], "Đồ họa vòng đời sáu giai đoạn với cơ chế tham gia tương ứng; ba vai trò: cơ quan có thẩm quyền – kỹ sư – người chịu tác động.",
             "DÂN CHỦ ĐI VÀO TOÀN BỘ VÒNG ĐỜI — MÔ HÌNH CỦA NHÓM 14", "—"),
            ("V13-S41", [7], "Đồ họa “cùng thắng”: ba lựa chọn thiết kế (thu dữ liệu tối thiểu · nhật ký truy cập · kênh sửa dữ liệu sai), mỗi lựa chọn nối tới hai lợi ích: QUẢN LÝ HIỆU QUẢ và BẢO VỆ QUYỀN; chân khung: Hiến pháp Điều 14 khoản 2 cho trường hợp xung đột thật.",
             "QUẢN LÝ HIỆU QUẢ VÀ BẢO VỆ QUYỀN: KHÔNG LUÔN ĐỐI LẬP", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Định nghĩa VNeID theo nguyên văn khoản 18 Điều 3 Luật Căn cước (Luật 118/2025 chỉ bổ sung chữ “(VNeID)”).",
            "Không dựng giao diện VNeID bằng AI; không nêu số người dùng, sự cố hay chính sách chưa kiểm chứng.",
            "Câu “thu thập đúng phạm vi, mục đích cụ thể, rõ ràng” dựa trên Luật 91/2025, Điều 3 khoản 2; ba ví dụ “cùng thắng” là diễn giải của nhóm.",
            "Bảng vòng đời là mô hình đề xuất của nhóm, không mô tả quy trình thực tế của VNeID.",
        ],
    },
    {
        "title": "BẢO MẬT, GÓP Ý VÀ QUYỀN ĐƯỢC PHẢN HỒI",
        "goal": "Phân biệt bốn khái niệm hay bị dùng lẫn; dùng mô hình A/B của nhóm để tách quyền gửi ý kiến khỏi khả năng ý kiến tác động tới quyết định; "
        "nhìn kiểm duyệt một cách có điều kiện.",
        "type": "Khái niệm và mô hình minh họa của Nhóm 14 (không phải ảnh chụp hay tình trạng của một hệ thống có thật).",
        "paras": [
            ("KN", "Có bốn khái niệm hay bị dùng lẫn: quyền riêng tư là quyền con người; bảo vệ dữ liệu cá nhân là quy tắc xử lý dữ liệu; "
             "an toàn thông tin là biện pháp chống truy cập trái phép; phân quyền là quyết định ai được xem gì. "
             "Một hệ thống rất an toàn vẫn có thể phân quyền quá rộng. [PAUSE 0.5]"),
            ("MH", "Giờ hãy xét một mô hình minh họa do nhóm tự dựng. Phương án A: một ô “gửi ý kiến”. "
             "Người dân gửi đi, rồi không biết ý kiến đi đâu. [PAUSE 0.3] "
             "Phương án B: vẫn ô ấy, nhưng có tiêu chí xử lý được công bố, có mã theo dõi không lộ danh tính, "
             "có phản hồi kèm lý do, có bản tổng hợp đã khử nhận dạng, có kênh yêu cầu xem xét lại, "
             "và có nhật ký những thay đổi được thực hiện sau góp ý. [PAUSE 0.3] "
             "Cả hai đều cho phép “góp ý”. Nhưng chỉ phương án B tạo ra con đường để ý kiến chạm tới quyết định. [PAUSE 0.5]"),
            ("N14", "Kiểm duyệt cũng không phải lúc nào cũng xấu: lọc thư rác hay chặn nội dung xâm phạm người khác là cần thiết. "
             "Vấn đề là tiêu chí lọc có được công bố, và người bị lọc có được biết lý do, đề nghị xem xét lại hay không. "
             "Thiếu những điều ấy, “được góp ý” chỉ còn là tham gia hình thức. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S42", [0], "Bốn thẻ khái niệm xếp hàng.",
             "RIÊNG TƯ · BẢO VỆ DỮ LIỆU CÁ NHÂN · AN TOÀN THÔNG TIN · PHÂN QUYỀN TRUY CẬP", "—"),
            ("V13-S43", [1], "So sánh A/B dựng bằng vector: A là một ô và mũi tên vào hộp đen; B có sáu thành phần nối thành đường tới “QUYẾT ĐỊNH”.",
             "MÔ HÌNH MINH HỌA CỦA NHÓM 14 — KHÔNG PHẢI HỆ THỐNG CÓ THẬT", "—"),
            ("V13-S45", [2], "Đồ họa phễu lọc: phần bị lọc có thẻ “lý do” và “đề nghị xem xét lại”.",
             "KIỂM DUYỆT CÓ TIÊU CHÍ + GIẢI TRÌNH + KHÁNG NGHỊ", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "A/B luôn mang nhãn “Mô hình minh họa của Nhóm 14”, không gắn tên VNeID hay cổng dịch vụ công.",
            "Không quy kết mọi hoạt động kiểm duyệt là tiêu cực.",
        ],
    },
    {
        "title": "SỞ HỮU TRÍ TUỆ: BẢO VỆ QUYỀN CÓ PHẢI LÀ DÂN CHỦ HÓA?",
        "goal": "Trình bày hai mặt: bảo hộ sở hữu trí tuệ là một biểu hiện của dân chủ (bình đẳng quyền trước pháp luật; chống xâm phạm là bảo vệ quyền) "
        "và là nền tảng; bước tiếp theo là sự tham gia vào quyết định thiết kế. Nhánh phụ, khoảng một phút.",
        "type": "Dữ kiện pháp lý đã kiểm chứng (Luật Sở hữu trí tuệ, Luật 131/2025/QH15) và diễn giải của Nhóm 14.",
        "paras": [
            ("DN", "Một câu hỏi thường gặp: đăng ký bằng sáng chế, bảo hộ quyền tác giả, kể cả với sản phẩm có dùng trí tuệ nhân tạo, "
             "có phải là dân chủ hóa công nghệ? [PAUSE 0.5]"),
            ("DK", "Theo Luật Sở hữu trí tuệ Việt Nam, quyền tác giả phát sinh từ khi tác phẩm được sáng tạo và thể hiện dưới một hình thức vật chất nhất định, "
             "không phụ thuộc vào việc đã đăng ký hay chưa; còn quyền đối với sáng chế được xác lập trên cơ sở văn bằng bảo hộ do cơ quan nhà nước cấp. "
             "Đây là cơ chế pháp lý bảo vệ quyền và giải quyết tranh chấp. [PAUSE 0.3]"),
            ("N14", "Ở một nghĩa, đây là biểu hiện của dân chủ: pháp luật bảo vệ bình đẳng quyền của người sáng tạo, "
             "và chống xâm phạm bản quyền chính là bảo vệ quyền ấy. [PAUSE 0.3] Nhưng để góp phần dân chủ hóa công nghệ, "
             "cần thêm điều kiện: thủ tục phải tiếp cận được với cả người ít nguồn lực, và tri thức không bị tập trung "
             "vào số ít chủ thể. Bảo vệ quyền sở hữu là nền tảng; sự tham gia của người chịu tác động vào quyết định thiết kế "
             "là bước tiếp theo. [PAUSE 0.3]"),
            ("N14", "Với trí tuệ nhân tạo, luật sửa đổi năm 2025 giao Chính phủ quy định riêng cho sản phẩm có sử dụng AI; "
             "nhóm không đưa ra kết luận chung cho mọi trường hợp. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S46", [0, 1], "Bản tóm tắt Luật Sở hữu trí tuệ Điều 6 khoản 1 và khoản 3 điểm a (bản sửa đổi 2019).",
             "LUẬT SỞ HỮU TRÍ TUỆ, ĐIỀU 6", "—"),
            ("V13-S47", [2], "Hai cột: BẢO VỆ QUYỀN SỞ HỮU (nền tảng) + THAM GIA VÀO QUYẾT ĐỊNH THIẾT KẾ (bước tiếp theo).",
             "BẢO VỆ QUYỀN LÀ NỀN TẢNG · THAM GIA THIẾT KẾ LÀ BƯỚC TIẾP THEO", "—"),
            ("V13-S48", [3], "Footage người thật vẽ trên máy tính bảng; bản tóm tắt Luật 131/2025/QH15 (khoản 5 Điều 6).",
             "AI: CHÍNH PHỦ QUY ĐỊNH RIÊNG", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Không nói quyền tác giả chỉ phát sinh khi đăng ký; không khẳng định mọi sản phẩm AI được hoặc không được bảo hộ.",
            "Khoản 3 điểm a Điều 6 theo bản sửa đổi năm 2019 (Luật 42/2019/QH14).",
        ],
    },
    {
        "title": "LẬP TRƯỜNG CỦA NHÓM 14: NÊN, KHÔNG NÊN VÀ ĐỀ XUẤT",
        "goal": "Nêu rõ luận điểm của Nhóm 14 (không gán cho Feenberg); nên/không nên; trở ngại; làm rõ ai giám sát, ai có quyền yêu cầu sửa đổi, "
        "ai chịu trách nhiệm khắc phục (theo pháp luật hiện hành), rồi đề xuất bổ sung đo được.",
        "type": "Luận điểm và đề xuất của Nhóm 14; dữ kiện pháp lý đã kiểm chứng cho bản đồ trách nhiệm.",
        "paras": [
            ("LD", "Đây là luận điểm của Nhóm 14, không phải trích dẫn Feenberg. [PAUSE 0.3] "
             "Dân chủ hóa công nghệ không dừng ở mở rộng quyền truy cập hay cho phép gửi ý kiến. Nó đòi hỏi những người chịu tác động "
             "có kênh tham gia có ý nghĩa vào việc xác định vấn đề, tiêu chí thiết kế, cơ chế dữ liệu, kiểm soát quyền lực, bảo mật, "
             "giám sát và kháng nghị; và sự tham gia ấy phải tạo ra phản hồi có thể kiểm chứng, trong giới hạn kỹ thuật, pháp lý và an toàn. [PAUSE 0.5]"),
            ("LD", "Vì vậy, nên: xác định người chịu tác động trước khi thiết kế; công khai mục đích, dữ liệu và trách nhiệm "
             "trong mức không xâm phạm riêng tư; tham vấn sớm và trả lời có lý do; "
             "phân quyền tối thiểu, có nhật ký truy cập và đường kháng nghị; đánh giá tác động trước và sau triển khai. [PAUSE 0.3]"),
            ("LD", "Không nên: đồng nhất tải ứng dụng với dân chủ hóa; góp ý tượng trưng; nhân danh hiệu quả để đóng kênh kiểm tra; "
             "nhân danh minh bạch để công khai dữ liệu cá nhân; hay lấy biểu quyết thay cho kiểm chứng kỹ thuật. [PAUSE 0.5]"),
            ("N14", "Vậy có làm được không? Được, nhưng không dễ. [PAUSE 0.3] Trở ngại thứ nhất là chi phí và thời gian để tham vấn. "
             "Thứ hai là khoảng cách số: người cao tuổi, người thiếu thiết bị hay kỹ năng dễ bị bỏ lại. "
             "Thứ ba là an toàn hệ thống: càng mở kênh tham gia, càng phải bảo vệ dữ liệu chặt hơn. "
             "Thứ tư là bất cân xứng thông tin giữa chuyên gia và người dân, cùng những giới hạn pháp lý về bí mật và an ninh. [PAUSE 0.3] "
             "Vì vậy, dân chủ hóa cần đi từng bước, có lộ trình và có người chịu trách nhiệm. [PAUSE 0.5]"),
            ("DK", "Giải pháp phải trả lời ba câu hỏi: ai giám sát, ai có quyền yêu cầu sửa đổi, và ai chịu trách nhiệm khắc phục. [PAUSE 0.3] "
             "Với một hệ thống như VNeID, pháp luật hiện hành đã có câu trả lời. Giám sát: Quốc hội, Hội đồng nhân dân, "
             "Mặt trận Tổ quốc, cơ quan chuyên trách bảo vệ dữ liệu cá nhân, và ở cấp xã có Ban Thanh tra nhân dân. "
             "Yêu cầu sửa đổi: chính người dân, qua quyền yêu cầu điều chỉnh thông tin theo Luật Căn cước, "
             "quyền yêu cầu chỉnh sửa dữ liệu cá nhân, quyền khiếu nại và kiến nghị. "
             "Khắc phục: cơ quan quản lý căn cước và bên kiểm soát dữ liệu phải sửa sai; người giải quyết khiếu nại phải trả lời "
             "trong thời hạn luật định; và khi hành vi trái pháp luật gây thiệt hại, có cơ chế bồi thường của Nhà nước. [PAUSE 0.5]"),
            ("LD", "Trên nền đó, nhóm em đề xuất bổ sung: kiểm toán kỹ thuật độc lập định kỳ, có công bố bản tóm tắt; "
             "nhật ký thay đổi công khai cho mỗi phiên bản; tính năng cho người dân biết ai đã xem dữ liệu của mình; "
             "và bộ chỉ số như tỷ lệ phản hồi có lý do, thời gian xử lý kháng nghị, "
             "số thay đổi thiết kế sau phản hồi. [PAUSE 0.3] "
             "Các đề xuất này không xóa được mọi xung đột, nhưng làm cho xung đột được nhìn thấy, được tranh luận "
             "và có người chịu trách nhiệm. [PAUSE 0.5]"),
        ],
        "scenes": [
            ("V13-S49", [0], "Thẻ luận điểm toàn màn hình, nhãn “LUẬN ĐIỂM CỦA NHÓM 14”; các cụm then chốt được highlight dần.",
             "LUẬN ĐIỂM CỦA NHÓM 14", "Nhạc hạ thấp nhất để nhấn lời."),
            ("V13-S50", [1], "Footage người thật trong buổi làm việc nhóm; checklist NÊN.", "NÊN", "Ambience nhẹ."),
            ("V13-S51", [2], "Checklist KHÔNG NÊN, dấu gạch vermilion.", "KHÔNG NÊN", "—"),
            ("V13-S52", [3], "Bốn thẻ trở ngại đánh số.", "LÀM ĐƯỢC KHÔNG? · BỐN TRỞ NGẠI", "—"),
            ("V13-S53", [4], "Bản đồ trách nhiệm ba cột: AI GIÁM SÁT · AI CÓ QUYỀN YÊU CẦU SỬA ĐỔI · AI CHỊU TRÁCH NHIỆM KHẮC PHỤC; mỗi mục ghi căn cứ pháp lý ngắn.",
             "BẢN ĐỒ TRÁCH NHIỆM — THEO PHÁP LUẬT HIỆN HÀNH", "—"),
            ("V13-S54", [5], "Bốn thẻ đề xuất của nhóm (nhãn “ĐỀ XUẤT CỦA NHÓM 14 — CHƯA PHẢI QUY ĐỊNH HIỆN HÀNH”); chân khung: trade-off được nhìn thấy và có người chịu trách nhiệm.",
             "ĐỀ XUẤT BỔ SUNG CỦA NHÓM 14", "Nhạc nhô nhẹ ở khoảng nghỉ cuối chương."),
        ],
        "checks": [
            "Bản đồ trách nhiệm: Hiến pháp Đ.9, 28, 30, 69; Luật 91/2025 Đ.4, 33, 37; NĐ 356/2025; Luật Căn cước Đ.5, 41; NĐ 69/2024 Đ.3; Luật THDC cơ sở Đ.38, 40; Luật Khiếu nại 2011 (sđ 2025) Đ.28; Luật TNBTCNN 2017 Đ.7, 17 (xem qa/v13/accountability_legal.md).",
            "Ban Thanh tra nhân dân chỉ giám sát chính quyền cấp xã; lời thoại nói “ở cấp xã”.",
            "Năm đề xuất bổ sung là đề xuất của nhóm, không phải quy định hiện hành; bảng chỉ số không có số liệu bịa.",
        ],
    },
    {
        "title": "KẾT LUẬN VÀ LỜI CẢM ƠN",
        "goal": "Trả lời câu hỏi trung tâm có điều kiện, bằng ngôn ngữ của ma trận quyền và bản đồ trách nhiệm; nêu giá trị dân chủ trong phạm vi Việt Nam; "
        "chốt ý nghĩa phương pháp luận; cảm ơn thầy và người xem; nối mềm sang credit.",
        "type": "Kết luận của Nhóm 14 dựa trên phân tích ở các chương trước.",
        "paras": [
            ("N14", "Quay lại câu hỏi ban đầu: dân chủ nằm ở đâu trong một hệ thống công nghệ? [PAUSE 0.5] "
             "Nó không nằm ở việc được dùng, và cũng không chỉ nằm ở một ô góp ý. Nó nằm ở chỗ người chịu tác động được biết, "
             "được tham vấn có trả lời, được tham gia quyết định trong phạm vi phù hợp, được giám sát và yêu cầu sửa đổi; "
             "và ở chỗ có người chịu trách nhiệm khắc phục khi hệ thống sai. [PAUSE 0.5]"),
            ("N14", "Trong phạm vi Việt Nam, giá trị dân chủ ấy đã có điểm tựa. Hiến pháp khẳng định quyền lực nhà nước thuộc về "
             "Nhân dân, công dân được tham gia quản lý và được phản hồi kiến nghị; phương châm dân biết, dân bàn, dân làm, "
             "dân kiểm tra, dân giám sát, dân thụ hưởng là định hướng. [PAUSE 0.3] Thách thức là đưa những nguyên tắc ấy "
             "vào chính thiết kế và quản trị các hệ thống số mà người dân dùng hằng ngày. [PAUSE 0.5]"),
            ("N14", "Về phương pháp luận, Feenberg giúp chúng em tránh hai sai lầm: coi công nghệ là công cụ trung tính, "
             "và coi công nghệ là định mệnh. Công nghệ mang giá trị, nhưng có thể được định hướng. "
             "Và ai được tham gia định hướng nó, chính là một câu hỏi của dân chủ. [PAUSE 0.5]"),
            ("DN", "Nhóm 14 xin chân thành cảm ơn thầy Nguyễn Hữu Sơn đã hướng dẫn nhóm trong suốt học phần. "
             "Cảm ơn các bạn đã theo dõi. [PAUSE 1.0]"),
        ],
        "scenes": [
            ("V13-S55", [0], "Montage người thật; checklist câu trả lời theo các hàng của ma trận.",
             "BIẾT · THAM VẤN CÓ TRẢ LỜI · THAM GIA QUYẾT ĐỊNH · GIÁM SÁT, YÊU CẦU SỬA · CÓ NGƯỜI KHẮC PHỤC", "Nhạc dâng dần."),
            ("V13-S56", [1], "Sáu chữ “dân” hiện lần lượt.",
             "DÂN BIẾT · DÂN BÀN · DÂN LÀM · DÂN KIỂM TRA · DÂN GIÁM SÁT · DÂN THỤ HƯỞNG", "—"),
            ("V13-S57", [2], "Sơ đồ chuỗi hiện lại toàn bộ, khép thành vòng tái thiết kế.",
             "CÔNG NGHỆ MANG GIÁ TRỊ — NHƯNG CÓ THỂ ĐƯỢC ĐỊNH HƯỚNG", "—"),
            ("V13-S58", [3], "Thẻ cảm ơn; crossfade hình và âm thanh 0,8 giây sang credit gốc.",
             "CẢM ƠN TS NGUYỄN HỮU SƠN", "Nhạc nội dung hạ dần, nhạc credit nâng dần."),
        ],
        "checks": [
            "Câu kết trả lời đúng câu hỏi mở đầu, có điều kiện, không tuyệt đối hóa.",
            "Văn kiện Đại hội XIII, t. I, tr. 27–28: phương châm “dân biết, dân bàn, dân làm, dân kiểm tra, dân giám sát, dân thụ hưởng”.",
        ],
    },
]

CREDIT = {
    "title": "END CREDITS",
    "duration": 54.1,
    "crossfade": 0.8,
    "desc": "Giữ nguyên credit gốc của nhóm (dài 54,1 giây, đủ danh sách thành viên và lời cảm ơn); "
    "không dựng lại, không thêm chữ hay phụ đề lên credit.",
}
