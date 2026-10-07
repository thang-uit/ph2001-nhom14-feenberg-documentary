"""Reference tables and prose blocks for the V13 review script DOCX (data only).

V13 applies the lecturer's review of the V12 script and the source audit in docs/research/."""

from __future__ import annotations

VERIFIED = "ĐÃ KIỂM CHỨNG"
TO_CHECK = "CẦN ĐỐI CHIẾU"
GROUP = "DIỄN GIẢI NHÓM"


def info_rows(content: str, total: str) -> list[list[str]]:
    return [
        ["Tên đề tài", "Dân chủ hóa thiết kế và quản trị công nghệ theo Andrew Feenberg"],
        ["Môn học", "Triết học"],
        ["Lớp", "PH2001.26.1.CH.02"],
        ["Giảng viên", "TS Nguyễn Hữu Sơn"],
        ["Nhóm", "Nhóm 14 (7 thành viên)"],
        ["Hình thức", "Phim tài liệu học thuật: thuyết minh một giọng đọc, phụ đề tiếng Việt, footage người thật, "
         "đồ họa giải thích và crop văn bản nguồn. Không dùng người ảo đứng thuyết trình."],
        ["Thời lượng", f"{total} (nội dung {content}, cộng credit gốc 54,1 giây), đo trên bản thu giọng cuối — trong khung 15–20 phút."],
        ["Phiên bản", "V13 — bản sửa theo góp ý của thầy về kịch bản V12: cầu nối quyền lực công, ma trận quyền, bản đồ trách nhiệm, "
         "tình huống cụ thể, tăng phần Feenberg, rút dẫn nhập, rà soát lại nguồn. Video được thu giọng và dựng theo đúng bản này."],
    ]


FEEDBACK_ROWS = [
    ["Cầu nối từ Lênin sang công nghệ phải dựa vào việc hệ thống kỹ thuật tham gia thực hiện quyền lực công, không chỉ tương đồng giữa “cơ cấu” và “thiết kế”.",
     "Bỏ phép so sánh “cơ cấu ↔ thiết kế”. Chương 2 chỉ giữ ý: dân chủ gắn với quyền ngang nhau trong tổ chức và thực hiện quyền lực công. "
     "Chương 4 lập luận: quyền lực công được thực hiện một phần qua hệ thống kỹ thuật (xác thực, cấp giấy tờ, xét điều kiện, xử lý dữ liệu); "
     "quy tắc kỹ thuật tác động như một quyết định quản lý; điểm tựa là Feenberg (1992, tr. 301): công nghệ là một nguồn quyền lực công chủ yếu. "
     "Bước nối với định nghĩa Lênin là lập luận của nhóm, đọc tách riêng.", "Chương 2; Chương 4"],
    ["Thang bảy bậc nên chuyển thành ma trận quyền và mức độ tham gia: tham vấn có trả lời chưa đồng nghĩa với cùng quyết định.",
     "Thay thang bằng ma trận 4 quyền (được biết, được tham vấn, được cùng quyết định, được giám sát và yêu cầu sửa đổi) × 3 mức "
     "(chưa có, hình thức, có hiệu lực). Lời thoại nói rõ: tham vấn có trả lời là mức cao nhất của quyền được tham vấn, nhưng chưa phải cùng quyết định.",
     "Chương 3; mục III.3"],
    ["Thay đổi thiết kế cũng chưa tự chứng minh tính dân chủ.",
     "Thêm phép thử bốn câu hỏi: thay đổi xuất phát từ kinh nghiệm của ai, qua quy trình nào, vì lợi ích của ai, ai giải trình. "
     "Phép thử được áp dụng lại cho tình huống ở Chương 6.", "Chương 3; Chương 6"],
    ["Phần giải pháp cần làm rõ ai giám sát, ai có quyền yêu cầu sửa đổi và ai chịu trách nhiệm khắc phục.",
     "Bản đồ trách nhiệm theo pháp luật hiện hành, có căn cứ từng mục; sau đó là đề xuất bổ sung của nhóm, ghi rõ không phải quy định hiện hành.",
     "Chương 10; mục III.8"],
    ["Quản lý hiệu quả và bảo vệ quyền người dân không luôn đối lập; thiết kế tốt có thể cải thiện cả hai.",
     "Bỏ cách đặt vấn đề “cán cân”. Nêu ba lựa chọn thiết kế có lợi cho cả hai phía: thu dữ liệu tối thiểu, nhật ký truy cập, kênh sửa dữ liệu sai. "
     "Xung đột thật vẫn theo tiêu chí Hiến pháp 2013 Điều 14 khoản 2.", "Chương 7 (đoạn cuối); mục III.6"],
    ["Rút phần dẫn nhập.", "Chương 1 còn ba đoạn (trước đây năm đoạn); vào thẳng câu hỏi trung tâm và hai định nghĩa.", "Chương 1"],
    ["Tăng dung lượng cho Feenberg.",
     "Chương 4 thêm nhận định của Feenberg về công nghệ như nguồn quyền lực công; Chương 5 thêm “lợi ích của người tham gia” và ba con đường "
     "can thiệp dân chủ; Chương 6 là tình huống do chính Feenberg phân tích.", "Chương 4, 5, 6"],
    ["Dùng một tình huống cụ thể cho thấy phản hồi dẫn đến sửa thiết kế như thế nào.",
     "Chương 6 mới: người bệnh AIDS ở Mỹ và việc thiết kế lại cơ chế thử nghiệm, tiếp cận thuốc (1987–1992), theo phân tích của Feenberg "
     "(1992; 2008) và văn bản của FDA; có nêu giới hạn của thay đổi.", "Chương 6; mục III.9"],
    ["Rà lại nguồn trích dẫn.",
     "Đối chiếu lại toàn bộ (mục VII): câu Lênin dùng đúng bản dịch Toàn tập; định nghĩa VNeID theo khoản 18 Điều 3 Luật Căn cước; "
     "sửa ba câu Feenberg (ví dụ email, câu về Mác, câu tr. 318); ghi đúng thuật ngữ “subversive rationalization” của bài 1992; "
     "bỏ Điều 6 khỏi chú thích Hiến pháp vì lời thoại không nói tới.", "Toàn bộ; mục VII"],
    ["Thống nhất thời lượng với bản thu cuối.",
     "Mọi mốc thời gian trong tài liệu được đo trên bản thu giọng cuối dùng cho video, gồm cả các khoảng nghỉ.", "Mục I, IV, V"],
]

PROBLEM = (
    "Công nghệ ngày nay không chỉ là công cụ mà là nơi nhiều quyết định chung được đưa ra: dữ liệu nào được thu thập, "
    "ai được phục vụ, ai được xem, ai có thể khiếu nại. Nếu dân chủ là quyền lực thuộc về nhân dân, thì câu hỏi triết học đặt ra là: "
    "quyền lực được thực hiện qua hệ thống kỹ thuật có thuộc phạm vi của dân chủ không, và nếu có, người chịu tác động "
    "tham gia vào nó ở đâu, bằng cách nào, với giới hạn nào."
)

CENTRAL_QUESTION = (
    "Khi một hệ thống công nghệ vừa giúp quản lý xã hội vừa thu thập, phân loại và kiểm soát dữ liệu, dân chủ nằm ở đâu: "
    "ở quyền được sử dụng, ở quyền được góp ý, hay ở khả năng thật sự tham gia và làm thay đổi cách hệ thống được thiết kế và quản trị?"
)

THESIS = (
    "Theo cách đọc của Nhóm 14, dân chủ hóa công nghệ không dừng ở việc mở rộng quyền truy cập hay cho phép gửi ý kiến. "
    "Nó đòi hỏi những người chịu tác động có kênh tham gia có ý nghĩa vào việc xác định vấn đề, tiêu chí thiết kế, cơ chế dữ liệu, "
    "kiểm soát quyền lực, bảo mật, giám sát và kháng nghị; sự tham gia phải có khả năng tạo phản hồi có thể kiểm chứng "
    "trong giới hạn kỹ thuật, pháp lý và an toàn."
)

SCOPE = [
    "Video phân tích dân chủ hóa thiết kế và quản trị công nghệ; không đánh giá toàn bộ nền dân chủ Việt Nam hay một chính sách cụ thể.",
    "VNeID là ví dụ phân tích về quản trị dữ liệu công dân; nhóm chỉ dùng dữ kiện từ văn bản pháp luật và nguồn chính thức, "
    "không khẳng định ứng dụng đang có hay thiếu cơ chế nào khi chưa có nguồn.",
    "Mô hình góp ý A/B, bảng vòng đời, ma trận quyền, phép thử bốn câu hỏi và phần đề xuất trong bản đồ trách nhiệm là khung phân tích của nhóm, "
    "không phải mô tả hệ thống có thật.",
    "Tình huống người bệnh AIDS là dữ kiện lịch sử ở Mỹ do Feenberg phân tích; được trình bày bằng đồ họa và nguồn, không dựng hình ảnh tái hiện.",
    "Mọi mệnh đề của Feenberg lấy từ văn bản gốc do thầy cung cấp hoặc từ trang học thuật của tác giả; không bịa trích dẫn.",
    "Sở hữu trí tuệ là nhánh phụ ngắn để trả lời góp ý; không thay thế chủ đề Feenberg.",
]

LABEL_ROWS = [
    ["[KHÁI NIỆM – CÓ NGUỒN]", "Định nghĩa lấy từ giáo trình, kinh điển hoặc văn bản pháp luật; có nguồn trong mục VII."],
    ["[DỮ KIỆN ĐÃ KIỂM CHỨNG]", "Thông tin thực tế (văn bản pháp luật, tiểu sử, chức năng hệ thống) đã đối chiếu nguồn."],
    ["[PHÂN TÍCH THEO FEENBERG]", "Trình bày sát văn bản của Feenberg. Khi vận dụng khái niệm của ông vào ví dụ Việt Nam, câu mở đầu bằng “Đọc theo Feenberg” để người xem biết đây là cách nhóm áp dụng, không phải kết luận của Feenberg về ví dụ đó."],
    ["[DIỄN GIẢI CỦA NHÓM 14]", "Cách nhóm vận dụng, tổng hợp hoặc định nghĩa làm việc; không gán cho Feenberg hay cho luật."],
    ["[LUẬN ĐIỂM CỦA NHÓM 14]", "Lập trường, khuyến nghị và đề xuất của nhóm."],
    ["[MINH HỌA CỦA NHÓM]", "Tình huống hoặc mô hình giả định để giải thích, không phải sự kiện có thật."],
    ["[DẪN NHẬP / CHUYỂN Ý]", "Lời chào, câu hỏi và câu nối giữa các phần."],
]

DEMOCRACY_ROWS = [
    ["Từ nguyên", "Tiếng Hy Lạp: demos (nhân dân) + kratos (cai trị) → “nhân dân cai trị”, về sau hiểu là quyền lực thuộc về nhân dân.",
     "Điểm xuất phát của định nghĩa."],
    ["Giáo trình Chủ nghĩa xã hội khoa học (Bộ GD&ĐT, 2021), chương IV",
     "Dân chủ là một giá trị xã hội phản ánh những quyền cơ bản của con người. Ba phương diện: (1) quyền lực — dân chủ là quyền lực "
     "thuộc về nhân dân, nhân dân là chủ nhân của nhà nước; (2) chế độ xã hội, chính trị — dân chủ là một hình thức hay hình thái nhà nước; "
     "(3) tổ chức và quản lý xã hội — dân chủ là một nguyên tắc (nguyên tắc dân chủ). Dân chủ có quá trình ra đời, phát triển cùng lịch sử xã hội.",
     "Định nghĩa theo quan điểm Mác – Lênin. Phương diện (3) là cầu nối tự nhiên sang quản trị công nghệ."],
    ["V.I. Lênin, “Nhà nước và cách mạng” (1917), chương V, mục 4",
     "“Chế độ dân chủ là một hình thức nhà nước, một trong những hình thái của nhà nước. […] Nhưng mặt khác, chế độ dân chủ có nghĩa là "
     "chính thức thừa nhận quyền bình đẳng giữa những công dân, thừa nhận cho mọi người được quyền ngang nhau trong việc xác định cơ cấu "
     "nhà nước và quản lý nhà nước.” (Toàn tập, t. 33, tr. 123–124)",
     "Nhóm giữ lại: dân chủ gắn với quyền ngang nhau trong tổ chức và thực hiện quyền lực công. Cầu nối sang công nghệ (Chương 4) dựa trên "
     "việc quyền lực công được thực hiện qua hệ thống kỹ thuật, không dựa trên sự giống nhau của câu chữ."],
    ["Hồ Chí Minh, “Dân vận” (báo Sự thật, số 120, 15/10/1949)",
     "“Nước ta là nước dân chủ. Bao nhiêu lợi ích đều vì dân. Bao nhiêu quyền hạn đều của dân… Nói tóm lại, quyền hành và lực lượng đều ở nơi dân.”",
     "Quan niệm dân là chủ trong bối cảnh Việt Nam."],
    ["Hiến pháp 2013 (sửa đổi, bổ sung 2025): Điều 2, 6, 25, 28, 30",
     "Tất cả quyền lực nhà nước thuộc về Nhân dân (Đ.2); Nhân dân thực hiện quyền lực nhà nước bằng dân chủ trực tiếp, bằng dân chủ đại diện (Đ.6); "
     "quyền tiếp cận thông tin (Đ.25); quyền tham gia quản lý nhà nước và xã hội, thảo luận, kiến nghị; Nhà nước công khai, minh bạch trong "
     "tiếp nhận, phản hồi ý kiến, kiến nghị (Đ.28); quyền khiếu nại, tố cáo, nghiêm cấm trả thù người khiếu nại, tố cáo (Đ.30).",
     "Khung pháp lý hiện hành; các điều này không bị sửa năm 2025 (Nghị quyết 203/2025/QH15 chỉ sửa Đ.9, Đ.10, khoản 1 Đ.84, Đ.110, Đ.111)."],
    ["Luật Thực hiện dân chủ ở cơ sở 2022 (số 10/2022/QH15, sửa đổi, bổ sung bởi Luật 47/2024/QH15 và Luật 97/2025/QH15)",
     "Điều 3: bảo đảm quyền được biết, tham gia ý kiến, quyết định và kiểm tra, giám sát. Chương II tách bốn nhóm: công khai thông tin (Đ.11); "
     "Nhân dân bàn và quyết định (Đ.15); Nhân dân tham gia ý kiến trước khi cơ quan có thẩm quyền quyết định (Đ.25); kiểm tra, giám sát (Đ.30).",
     "Cho thấy các nấc khác nhau của tham gia: được biết ≠ góp ý ≠ quyết định."],
    ["Văn kiện Đại hội XIII của Đảng (2021)",
     "Phương châm “Dân biết, dân bàn, dân làm, dân kiểm tra, dân giám sát, dân thụ hưởng” (t. I, tr. 27–28); Đại hội XIII bổ sung “dân thụ hưởng”.",
     "Đọc ở Chương 11 (đoạn 2), cảnh V13-S56."],
    ["A. Feenberg (1992; 2003)",
     "Công nghệ là một trong những nguồn quyền lực công chủ yếu (1992, tr. 301); dân chủ cần được mở rộng vào các lĩnh vực đời sống được công nghệ trung giới; "
     "dân chủ hóa công nghệ trước hết là vấn đề sáng kiến và tham gia; không phải bầu cử giữa các thiết bị.",
     "Điểm tựa cho cầu nối ở Chương 4 và nội dung Chương 5. Feenberg không dẫn Lênin và không thay thế định nghĩa dân chủ ở trên."],
]

DEMOCRACY_WORKING_DEF = (
    "Định nghĩa làm việc của Nhóm 14 (tổng hợp từ các nguồn trên, dùng làm khung phân tích): dân chủ là nguyên tắc và chế độ, "
    "theo đó quyền quyết định những vấn đề chung thuộc về nhân dân, được tổ chức thành các quyền, thiết chế và quy trình "
    "(được biết, tham gia, đại diện, giám sát, giải trình, kiểm soát quyền lực), nhằm thực hiện các giá trị bình đẳng, phẩm giá, "
    "bảo vệ quyền con người và khả năng phản biện. Hình thức thực hiện mang tính lịch sử – cụ thể ở mỗi quốc gia; nhưng ở đâu "
    "cũng có thể kiểm tra bằng câu hỏi: người dân có được biết, được bàn, được quyết định, được giám sát và được bảo vệ hay không. "
    "Dân chủ không chỉ là đa số biểu quyết, và một biểu mẫu góp ý chưa phải là dân chủ."
)

DEMOCRATIZATION_DEF = (
    "Dân chủ hóa (diễn giải của Nhóm 14): quá trình mở rộng, trong một cấu trúc cụ thể, quyền được biết, quyền tham gia có hiệu lực, "
    "quyền phản biện, quyền yêu cầu giải trình và năng lực tác động đến quyết định của những người chịu tác động. "
    "Tham gia chỉ có hiệu lực khi có đủ: thông tin đủ để hiểu; kênh tiếp cận cho cả người yếu thế; được phát biểu không sợ "
    "trả đũa (Hiến pháp Điều 30 nghiêm cấm trả thù người khiếu nại, tố cáo); phản hồi có lý do; cơ chế kháng nghị; trách nhiệm của người quyết định; và khả năng sửa quy tắc hoặc thiết kế khi có "
    "bằng chứng về tác động bất công. Dân chủ hóa KHÔNG đồng nghĩa với:"
)

NOT_DEMOCRATIZATION = [
    "ai cũng được dùng một ứng dụng;",
    "ai cũng được gửi ý kiến;",
    "số lượng người dùng tăng;",
    "chuyển một quy trình giấy sang màn hình (đó là số hóa);",
    "thay chuyên môn bằng biểu quyết;",
    "công khai toàn bộ dữ liệu cá nhân.",
]

MATRIX_ROWS = [
    ["Được biết", "Không công bố mục đích, dữ liệu, tiêu chí", "Công bố khó hiểu, khó tìm",
     "Thông tin đủ để hiểu: dữ liệu nào, để làm gì, ai xem, ai chịu trách nhiệm"],
    ["Được tham vấn", "Không hỏi ý kiến", "Hỏi nhưng không trả lời", "Tham vấn sớm, trả lời công khai có lý do"],
    ["Được cùng quyết định", "Không có tiếng nói", "Biểu quyết sau khi phương án đã chốt",
     "Ý kiến có sức nặng trong phạm vi được trao (ví dụ: tiêu chí ưu tiên, kênh thay thế)"],
    ["Được giám sát, yêu cầu sửa đổi", "Không có kênh", "Có kênh nhưng không có hạn trả lời",
     "Có hạn trả lời; kết quả giám sát buộc phải khắc phục"],
]

MATRIX_NOTE = (
    "Ma trận là khung phân tích của Nhóm 14. Mỗi hàng là một quyền riêng, không phải một bậc của cùng một chiếc thang: một hệ thống có thể "
    "có hiệu lực ở hàng này nhưng chỉ hình thức ở hàng khác. Tham vấn có trả lời (ô cao nhất của hàng “được tham vấn”) vẫn chưa phải là "
    "cùng quyết định. Một thay đổi thiết kế cũng chưa tự chứng minh tính dân chủ; phải qua phép thử bốn câu hỏi: (1) thay đổi xuất phát "
    "từ kinh nghiệm của ai; (2) đi qua quy trình nào; (3) phục vụ lợi ích của ai; (4) ai chịu trách nhiệm giải trình về nó."
)

TECH_ROWS = [
    ["Công nghệ", "Hệ thống xã hội – kỹ thuật gồm thiết bị, phần mềm, dữ liệu, tiêu chuẩn, quy trình, con người và thiết chế.",
     "Chỉ là máy móc hay phần mềm."],
    ["Thiết kế công nghệ", "Lựa chọn cấu trúc, chức năng, giao diện, dữ liệu, tiêu chuẩn, quyền truy cập và cách tích hợp; "
     "nơi nhiều phương án khả thi hiện thực hóa các giá trị khác nhau.", "Trang trí giao diện; cách dùng sau khi sản phẩm hoàn tất."],
    ["Quản trị công nghệ", "Phân bổ quyền quyết định, trách nhiệm, giám sát, đánh giá, sửa đổi và kháng nghị trong toàn bộ vòng đời.",
     "Vận hành kỹ thuật; kiểm duyệt đơn thuần."],
    ["Giá trị công nghệ", "Các ưu tiên như hiệu quả, an toàn, công bằng, riêng tư, phẩm giá, bao trùm, trách nhiệm được cụ thể hóa "
     "trong lựa chọn kỹ thuật hoặc quản trị.", "Khẩu hiệu đạo đức gắn bên ngoài."],
    ["Phân biệt then chốt", "Người dân có thể sử dụng một hệ thống mà không có quyền tham gia vào thiết kế hay quản trị hệ thống đó.", "—"],
]

FEENBERG_ROWS = [
    ["Lý thuyết phê phán về công nghệ", "Công nghệ vừa mang giá trị vừa có thể được con người định hướng; vấn đề là thiếu thiết chế "
     "phù hợp để kiểm soát; công nghệ có thể đi vào một quá trình thiết kế và phát triển dân chủ hơn.", "S01, tr. 9",
     "Chống công nghệ; thuyết công cụ."],
    ["Phê phán thuyết công cụ và thuyết tất định", "Thuyết công cụ coi công nghệ trung tính; thuyết tất định coi công nghệ tự trị, "
     "định hình xã hội. Feenberg bác bỏ cả hai.", "S01, tr. 5–6; S03, tr. 302", "Coi Feenberg phủ nhận ràng buộc kỹ thuật."],
    ["Công nghệ như nguồn quyền lực công", "“Technology is one of the major sources of public power in modern societies.”", "S03, tr. 301",
     "Đồng nhất với định nghĩa dân chủ của Lênin (Feenberg không dẫn Lênin)."],
    ["Tính bất định tương đối", "Thiết kế bị bất định tương đối bởi tiêu chí kỹ thuật: thường có nhiều phương án khả thi.",
     "S03, tr. 305", "Muốn thiết kế sao cũng được."],
    ["Mã kỹ thuật (technical code)", "Cách chân trời văn hóa – xã hội và lợi ích được cụ thể hóa ở cấp thiết kế; khi ổn định, "
     "dễ bị nhìn như tất yếu kỹ thuật.", "S03, tr. 313–315; S02, tr. 26", "Mã nguồn phần mềm."],
    ["Năng lực hành động của người dùng (user agency)", "Khả năng chiếm dụng, diễn giải lại, phản hồi, tổ chức để ảnh hưởng tới "
     "công nghệ; ví dụ email do người dùng đưa vào Internet.", "S01, tr. 10; S02, tr. 10–12, 16 (trang bản thảo PDF)", "Toàn quyền kiểm soát."],
    ["Hợp lý hóa dân chủ (democratic rationalization)", "Mở rộng tính hợp lý kỹ thuật để nội tại hóa bối cảnh, chi phí, kinh nghiệm "
     "bị gạt ra ngoài, thông qua sáng kiến, phản kháng, tham gia.",
     "S03, tr. 318–320 (bài 1992 dùng thuật ngữ “subversive rationalization”); tên “democratic rationalization” ở bản 2003 [20]",
     "Bỏ phiếu chọn thiết bị; phủ nhận hiệu quả."],
    ["Mở rộng dân chủ vào lĩnh vực được công nghệ trung giới", "Nếu dân chủ không vươn tới các lĩnh vực ấy, giá trị sử dụng của nó "
     "suy giảm, sự tham gia tàn lụi; Feenberg thuật lại lập luận của Mác: dân chủ phải được mở rộng vào thế giới lao động.",
     "S03, tr. 301–302", "Gán định nghĩa dân chủ Mác – Lênin cho Feenberg."],
    ["Dân chủ hóa công nghệ", "Trước hết không phải vấn đề quyền pháp lý mà là sáng kiến và tham gia; hình thức pháp lý sẽ trống rỗng "
     "nếu không xuất phát từ kinh nghiệm và nhu cầu của những cá nhân đang kháng cự một bá quyền mang tính kỹ thuật; không phải bầu cử giữa các thiết bị.",
     "S03, tr. 318; S01, tr. 10", "Phổ cập quyền truy cập; khảo sát hình thức."],
    ["Lợi ích của người tham gia (participant interests)", "Ai bị cuốn vào một hệ thống kỹ thuật đều có những lợi ích nảy sinh từ chính vị trí ấy.",
     "Feenberg (1992b), tr. 217–218 [17]", "Lợi ích của người tiêu dùng nói chung."],
    ["Ba con đường can thiệp dân chủ", "Tranh luận công khai về công nghệ; đối thoại giữa chuyên gia và người dùng (thiết kế có sự tham gia); "
     "chiếm dụng sáng tạo.", "Bakardjieva & Feenberg (2002), tr. 187 [18]", "Chỉ có biểu tình; chỉ có bỏ phiếu."],
    ["Tình huống người bệnh AIDS", "Người bệnh buộc thiết kế thử nghiệm thay đổi, thêm mục tiêu chăm sóc số đông vào mục đích khoa học; "
     "“những thay đổi như vậy mang tính dân chủ và tiến bộ”.", "Feenberg (2008), tr. 25 [19]; (1992b), tr. 214–219; Dusek (2006), tr. 103",
     "Coi đó là bỏ giả dược hoặc bỏ kiểm chứng khoa học."],
]

PRIVACY_ROWS = [
    ["Quyền riêng tư", "Quyền con người về đời sống riêng tư, bí mật cá nhân, bí mật gia đình.", "Hiến pháp 2013, Điều 21."],
    ["Bảo vệ dữ liệu cá nhân", "Các quy tắc về mục đích, căn cứ, phạm vi thu thập, sử dụng, chia sẻ, lưu trữ dữ liệu và quyền của chủ thể dữ liệu.",
     "Luật 91/2025/QH15 (Điều 4: quyền chủ thể; Điều 19: xử lý không cần đồng ý, phải có cơ chế giám sát); Nghị định 356/2025/NĐ-CP."],
    ["An toàn, an ninh thông tin", "Biện pháp kỹ thuật và tổ chức chống truy cập, sửa đổi, rò rỉ trái phép.", "An toàn ≠ tham gia."],
    ["Phân quyền truy cập", "Quyết định ai được xem, sửa, chia sẻ dữ liệu nào, trong vai trò nào.",
     "Hệ thống an toàn vẫn có thể phân quyền quá rộng."],
]

MANAGEMENT_AND_RIGHTS = (
    "Quản lý hiệu quả và bảo vệ quyền người dân (diễn giải của Nhóm 14): hai mục tiêu này không luôn đối lập; thiết kế tốt có thể cải thiện cả hai. "
    "(1) Thu thập dữ liệu đúng phạm vi, mục đích cụ thể, rõ ràng (Luật 91/2025/QH15, Điều 3 khoản 2): ít dữ liệu hơn thì ít rủi ro lộ lọt và ít chi phí lưu trữ. "
    "(2) Nhật ký truy cập: người dân biết ai đã xem hồ sơ của mình; người quản lý phát hiện tra cứu trái phép. "
    "(3) Kênh sửa dữ liệu sai dễ dùng: bảo vệ quyền yêu cầu chỉnh sửa và làm cơ sở dữ liệu chính xác hơn (Luật Căn cước yêu cầu thông tin "
    "đầy đủ, chính xác, kịp thời). Khi có xung đột thật, tiêu chí là Hiến pháp 2013 Điều 14 khoản 2: quyền con người, quyền công dân chỉ "
    "có thể bị hạn chế theo quy định của luật trong trường hợp cần thiết vì lý do quốc phòng, an ninh quốc gia, trật tự, an toàn xã hội, "
    "đạo đức xã hội, sức khỏe của cộng đồng."
)

LIFECYCLE_ROWS = [
    ["Xác định nhu cầu", "Vấn đề cần giải quyết; phạm vi dữ liệu", "Cơ quan chủ quản có thẩm quyền", "Người dân, nhóm yếu thế, cán bộ tiếp nhận",
     "Khảo sát, tham vấn, bản đồ người chịu tác động", "Công bố tóm tắt ý kiến và lý do chọn phạm vi", "Xác định mục đích; tối thiểu hóa dữ liệu",
     "Thẩm quyền pháp lý, ngân sách"],
    ["Thiết kế", "Trường dữ liệu, tiêu chí, luồng xử lý, phân quyền, giao diện", "Cơ quan chủ quản và đội kỹ sư", "Người dùng, người vận hành",
     "Công bố mục đích, dữ liệu, tiêu chí ở mức phù hợp; thử phương án", "Giải trình vì sao chọn phương án", "Bảo vệ dữ liệu từ khâu thiết kế; quyền truy cập tối thiểu",
     "An ninh, tiêu chuẩn kỹ thuật"],
    ["Thử nghiệm", "Phương án nào được giữ, sửa, bỏ", "Đội kỹ sư, đơn vị kiểm thử", "Nhóm dễ bị bỏ sót (cao tuổi, khuyết tật, vùng khó khăn)",
     "Thử nghiệm với người dùng thật", "Báo cáo lỗi theo nhóm người dùng", "Dữ liệu thử đã khử nhận dạng", "Thời gian, chi phí"],
    ["Vận hành", "Xử lý yêu cầu, sửa dữ liệu, cấp quyền", "Người vận hành, cán bộ", "Người dùng",
     "Kênh chỉnh sửa dữ liệu, khiếu nại", "Lý do bằng văn bản; đường kháng nghị", "Nhật ký truy cập; kiểm soát nội bộ", "Khối lượng công việc"],
    ["Giám sát", "Đánh giá tác động, kiểm tra tuân thủ", "Cơ quan giám sát theo luật định; kiểm tra độc lập", "Công chúng",
     "Báo cáo công khai, bộ chỉ số", "Kiến nghị sửa đổi", "Kiểm tra an toàn thông tin", "Bí mật nhà nước, dữ liệu nhạy cảm"],
    ["Tái thiết kế", "Sửa quy tắc, dữ liệu, giao diện, quy trình", "Cơ quan chủ quản và đội kỹ sư", "Người đã phản hồi; nhóm bị ảnh hưởng",
     "Công bố thay đổi; tham vấn lại", "Nhật ký thay đổi sau phản hồi", "Đánh giá lại rủi ro", "Tương thích hệ thống, chi phí"],
]

ACCOUNTABILITY_ROWS = [
    ["Ai giám sát?", "Quốc hội, Hội đồng nhân dân (giám sát tối cao; giám sát ở địa phương)", "Hiến pháp Đ.69; Luật số 121/2025/QH15"],
    ["", "Mặt trận Tổ quốc Việt Nam (giám sát, phản biện xã hội)", "Hiến pháp Đ.9 (sửa đổi 2025); Luật MTTQ Việt Nam"],
    ["", "Cơ quan chuyên trách bảo vệ dữ liệu cá nhân (đơn vị thuộc Bộ Công an)", "Luật 91/2025/QH15 Đ.33; NĐ 356/2025/NĐ-CP Đ.39"],
    ["", "Ban Thanh tra nhân dân (giám sát chính quyền cấp xã)", "Luật Thực hiện dân chủ ở cơ sở Đ.38"],
    ["Ai có quyền yêu cầu sửa đổi?", "Công dân: yêu cầu điều chỉnh thông tin trong cơ sở dữ liệu", "Luật Căn cước Đ.5 khoản 1"],
    ["", "Chủ thể dữ liệu: xem, chỉnh sửa, yêu cầu chỉnh sửa dữ liệu cá nhân", "Luật 91/2025/QH15 Đ.4 khoản 1; NĐ 356/2025 Đ.5 (thời hạn)"],
    ["", "Công dân: khiếu nại quyết định, hành vi hành chính; kiến nghị", "Hiến pháp Đ.28, Đ.30; Luật Khiếu nại 2011 (sửa đổi 2025)"],
    ["Ai chịu trách nhiệm khắc phục?", "Cơ quan quản lý căn cước: cập nhật, điều chỉnh thông tin đầy đủ, chính xác, kịp thời", "Luật Căn cước Đ.4, Đ.41"],
    ["", "Bên kiểm soát dữ liệu: biện pháp bảo vệ dữ liệu, chịu trách nhiệm về thiệt hại", "Luật 91/2025/QH15 Đ.37"],
    ["", "Người giải quyết khiếu nại: giải quyết trong thời hạn luật định", "Luật Khiếu nại Đ.28"],
    ["", "Nhà nước bồi thường khi có hành vi trái pháp luật của người thi hành công vụ gây thiệt hại", "Hiến pháp Đ.30 khoản 2; Luật TNBTCNN 2017 Đ.7, Đ.17"],
]

PROPOSALS_NOTE = (
    "Đề xuất bổ sung của Nhóm 14 (không phải quy định hiện hành): kiểm toán kỹ thuật độc lập định kỳ, công bố bản tóm tắt; nhật ký thay đổi "
    "công khai cho mỗi phiên bản; tính năng cho người dân biết ai đã xem dữ liệu của mình; bộ chỉ số theo dõi (tỷ lệ phản hồi có lý do, "
    "thời gian xử lý kháng nghị, số thay đổi thiết kế sau phản hồi). Lý do của đề xuất kiểm toán độc lập: hiện cơ quan vận hành hệ thống "
    "định danh và cơ quan chuyên trách bảo vệ dữ liệu cá nhân cùng thuộc một bộ."
)

CASE_ROWS = [
    ["Cuối thập niên 1980", "Thuốc mới chủ yếu đến người bệnh qua thử nghiệm có đối chứng: ít chỗ, điều kiện chặt, có nhóm giả dược. "
     "Feenberg: người bệnh bị coi là đối tượng thụ động; mong muốn tham gia bị xem là không hợp lý.", "Feenberg (1992b), tr. 214–216"],
    ["22/5/1987", "Quy định “treatment IND”: cho dùng thuốc đang thử nghiệm để điều trị ngoài thử nghiệm chính thức.", "52 FR 19466; FDA (Junod)"],
    ["11/10/1988", "Hơn một nghìn người tập trung trước trụ sở FDA.", "ACT UP Oral History Project; FDA HIV/AIDS Time Line"],
    ["1987–1989", "Feenberg: thay đổi diễn ra dưới sức ép chính trị mạnh mẽ.", "Feenberg (1992b), tr. 215"],
    ["15/4/1992", "Chính sách “đường song song” (parallel track): người không vào được thử nghiệm vẫn được dùng thuốc; chạy song song, "
     "không thay thế thử nghiệm có đối chứng.", "57 FR 13250"],
    ["11/12/1992", "Quy chế phê duyệt nhanh (accelerated approval).", "57 FR 58942"],
    ["Đánh giá", "Người bệnh buộc thiết kế thử nghiệm thay đổi, thêm mục tiêu chăm sóc số đông; “những thay đổi như vậy mang tính dân chủ "
     "và tiến bộ”. Giới hạn: lo ngại dữ liệu kém tin cậy; tranh luận tiếp cận nhanh – kiểm chứng khoa học vẫn tiếp diễn.", "Feenberg (2008), tr. 25"],
]

PRODUCTION_RULES = [
    "Hình ảnh chỉ dùng khi giúp hiểu đúng câu thoại đang phát; không dùng cảnh đẹp nhưng không liên quan lập luận.",
    "Footage người thật, ánh sáng ban ngày, màu da thật; cảnh minh họa dựng bằng AI có nhãn nhỏ “MINH HỌA BẰNG AI”; "
    "không người ảo đứng nói, không CGI, không nhân vật da sáp/nhựa.",
    "Ảnh Andrew Feenberg là ảnh thật có nguồn và giấy phép (Wikimedia Commons, Beatrice Murch, CC BY-SA 3.0); không tạo chân dung bằng AI.",
    "Không dựng giao diện VNeID bằng AI; không hiển thị dữ liệu cá nhân thật; mọi màn hình minh họa ghi rõ là minh họa.",
    "Văn bản nguồn (giáo trình, Hiến pháp, luật, bài của Feenberg) được crop đúng đoạn và highlight đúng câu được đọc.",
    "Sơ đồ, chữ và bảng dựng bằng vector ở hậu kỳ; mũi tên có nhãn, không chạy xuyên chữ, nằm trong vùng an toàn khung hình.",
    "Một giọng thuyết minh duy nhất, rõ, tốc độ vừa; khoảng nghỉ 4 giây giữa các chương và một nhịp ngắn sau mỗi đoạn.",
    "Tình huống lịch sử (người bệnh AIDS) chỉ dùng đồ họa và nguồn; không dựng hình ảnh tái hiện sự kiện.",
    "Đồ họa, phụ đề và dựng hình bằng Remotion (React), một họ chữ Avenir Next xuyên suốt; xuất bản 1920×1080, 30 khung hình/giây, "
    "H.264 High, Rec.709, âm thanh AAC-LC 48 kHz, sẵn sàng tải lên YouTube.",
    "Nhạc nền nhẹ, luôn thấp hơn lời thoại; không dùng hiệu ứng âm thanh trang trí.",
    "Phụ đề sinh trực tiếp từ lời thoại cuối, tiếng Việt Unicode chuẩn, tối đa hai dòng.",
    "Credit cuối giữ nguyên bản gốc của nhóm, nối mềm bằng crossfade hình và âm thanh.",
]

CLAIM_ROWS = [
    ["V13-C01", "Từ nguyên demos + kratos: nhân dân cai trị → quyền lực thuộc về nhân dân.", "Khái niệm",
     "Giáo trình CNXHKH (2021), ch. IV; nhiều tài liệu thứ cấp thống nhất", VERIFIED],
    ["V13-C02", "Dân chủ là giá trị xã hội phản ánh quyền cơ bản của con người; ba phương diện: quyền lực, hình thái nhà nước, nguyên tắc tổ chức và quản lý xã hội.",
     "Khái niệm", "Giáo trình CNXHKH (2021), ch. IV, mục I.1 (khoảng tr. 125–128; cần đối chiếu bản in để ghi số trang). Lời thoại dùng đúng cụm “về chế độ xã hội và trong lĩnh vực chính trị”",
     TO_CHECK],
    ["V13-C03", "“Chế độ dân chủ là một hình thức nhà nước, một trong những hình thái của nhà nước.”", "Khái niệm",
     "Lênin, Nhà nước và cách mạng, ch. V mục 4; V.I. Lênin Toàn tập, t. 33, Nxb Tiến bộ, Mátxcơva, tr. 123", VERIFIED],
    ["V13-C04", "“Nhưng mặt khác, chế độ dân chủ có nghĩa là chính thức thừa nhận quyền bình đẳng giữa những công dân, thừa nhận cho mọi người "
     "được quyền ngang nhau trong việc xác định cơ cấu nhà nước và quản lý nhà nước.”",
     "Khái niệm", "Lênin Toàn tập, t. 33 (bản dịch tiếng Việt), tr. 123–124; Collected Works, vol. 25, p. 477. Nội dung đã đối chiếu; số trang cần xem bản in", TO_CHECK],
    ["V13-C05", "Hồ Chí Minh: “Nước ta là nước dân chủ. Bao nhiêu lợi ích đều vì dân. Bao nhiêu quyền hạn đều của dân.”",
     "Khái niệm", "“Dân vận”, báo Sự thật số 120, 15/10/1949; Hồ Chí Minh Toàn tập, Nxb CTQG, 2011, t. 6, tr. 232", VERIFIED],
    ["V13-C06", "Tất cả quyền lực nhà nước thuộc về Nhân dân.", "Dữ kiện", "Hiến pháp 2013 (sđ, bs 2025), Điều 2 khoản 2", VERIFIED],
    ["V13-C08", "Quyền tham gia quản lý nhà nước và xã hội, thảo luận, kiến nghị; Nhà nước công khai, minh bạch trong tiếp nhận, phản hồi.",
     "Dữ kiện", "Hiến pháp 2013, Điều 28 khoản 1, 2", VERIFIED],
    ["V13-C09", "Nhóm nội dung: công khai để dân biết; dân bàn và quyết định; dân tham gia ý kiến trước khi cơ quan có thẩm quyền quyết định; kiểm tra, giám sát.",
     "Dữ kiện", "Luật 10/2022/QH15, Điều 3, Điều 11, 15, 25, 30; sửa đổi bởi Luật 97/2025/QH15", VERIFIED],
    ["V13-C10", "Định nghĩa làm việc ba lớp về dân chủ; định nghĩa dân chủ hóa; ma trận quyền × mức độ; phép thử bốn câu hỏi.", "Diễn giải", "Nhóm 14", GROUP],
    ["V13-C11", "Feenberg là nhà triết học công nghệ người Mỹ, giáo sư danh dự tại Đại học Simon Fraser (Canada); gắn với lý thuyết phê phán về công nghệ.", "Dữ kiện",
     "sfu.ca/humanities-institute/about/profiles/a-feenberg.html (Professor Emeritus); S01", VERIFIED],
    ["V13-C12", "Ma trận hai trục và bốn lập trường; lý thuyết phê phán: công nghệ mang giá trị nhưng có thể được kiểm soát.", "Feenberg",
     "S01, tr. 5–9", VERIFIED],
    ["V13-C13", "Vấn đề là thiếu thiết chế phù hợp; có thể thiết kế, phát triển dân chủ hơn.", "Feenberg", "S01, tr. 9", VERIFIED],
    ["V13-C14", "Thiết kế bất định tương đối; nhiều phương án khả thi.", "Feenberg", "S03, tr. 305", VERIFIED],
    ["V13-C15", "Mã kỹ thuật và hiệu ứng “tất yếu kỹ thuật”.", "Feenberg", "S03, tr. 313–315; S02, tr. 26", VERIFIED],
    ["V13-C16", "Email do người dùng thành thạo đưa vào, không có trong kế hoạch ban đầu; trong bài giảng tháng 6/2003 ông viết “today” email là chức năng được dùng nhiều nhất của Internet.",
     "Feenberg", "S01, tr. 10", VERIFIED],
    ["V13-C17", "Hợp lý hóa dân chủ; bài 1992 dùng thuật ngữ “subversive rationalization”.", "Feenberg", "S03, tr. 318–320; bản 2003 “Democratic Rationalization”, Scharff & Dusek (eds.), tr. 652–665 [20]", VERIFIED],
    ["V13-C18", "Feenberg thuật lại lập luận của Mác: dân chủ phải được mở rộng từ lĩnh vực chính trị sang thế giới lao động.", "Feenberg", "S03, tr. 301", VERIFIED],
    ["V13-C19", "Nếu dân chủ không vươn tới lĩnh vực được công nghệ trung giới, giá trị sử dụng suy giảm, tham gia tàn lụi.", "Feenberg",
     "S03, tr. 302", VERIFIED],
    ["V13-C20", "Không hợp lý khi bầu cử giữa các thiết bị hay bản thiết kế.", "Feenberg", "S01, tr. 10", VERIFIED],
    ["V13-C21", "Dân chủ hóa công nghệ trước hết là sáng kiến và tham gia, không chủ yếu là quyền pháp lý; hình thức pháp lý trống rỗng nếu không xuất phát từ kinh nghiệm, nhu cầu của những cá nhân đang kháng cự một bá quyền mang tính kỹ thuật.", "Feenberg", "S03, tr. 318", VERIFIED],
    ["V13-C22", "Luật Căn cước định nghĩa Ứng dụng định danh quốc gia (VNeID) là ứng dụng trên thiết bị số để phục vụ định danh điện tử và xác thực "
     "điện tử trong giải quyết thủ tục hành chính, dịch vụ công và các giao dịch khác trên môi trường điện tử.", "Dữ kiện",
     "Luật Căn cước 26/2023/QH15, Điều 3 khoản 18 (Luật 118/2025/QH15 bổ sung chữ “(VNeID)”); VBHN 09/VBHN-VPQH (2026); NĐ 69/2024 Điều 3 khoản 4 (sửa bởi NĐ 169/2025)", VERIFIED],
    ["V13-C24", "Quyền bất khả xâm phạm về đời sống riêng tư, bí mật cá nhân.", "Dữ kiện", "Hiến pháp 2013, Điều 21 khoản 1", VERIFIED],
    ["V13-C25", "Quyền của chủ thể dữ liệu: được biết; đồng ý, rút lại đồng ý; xem, chỉnh sửa; yêu cầu xóa, hạn chế, phản đối; khiếu nại, khởi kiện.",
     "Dữ kiện", "Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (hiệu lực 01/01/2026), Điều 4 khoản 1", VERIFIED],
    ["V13-C26", "Xử lý không cần đồng ý khi phục vụ hoạt động của cơ quan nhà nước, quản lý nhà nước theo luật; phải có cơ chế giám sát.",
     "Dữ kiện", "Luật 91/2025/QH15, Điều 19 khoản 1 điểm c, khoản 2", VERIFIED],
    ["V13-C27", "Hạn chế quyền chỉ theo luật, khi cần thiết vì quốc phòng, an ninh quốc gia, trật tự, an toàn xã hội…", "Dữ kiện",
     "Hiến pháp 2013, Điều 14 khoản 2", VERIFIED],
    ["V13-C28", "Quyền tác giả phát sinh khi tác phẩm được sáng tạo, thể hiện dưới hình thức vật chất, không phân biệt đã đăng ký hay chưa; "
     "quyền đối với sáng chế xác lập trên cơ sở quyết định cấp văn bằng bảo hộ.", "Dữ kiện",
     "Luật Sở hữu trí tuệ, Điều 6 khoản 1; khoản 3 điểm a sửa đổi bởi Luật 42/2019/QH14", VERIFIED],
    ["V13-C29", "Chính phủ quy định việc phát sinh, xác lập quyền khi đối tượng được tạo ra có sử dụng AI; cho phép dùng văn bản, dữ liệu đã được công bố hợp pháp "
     "và công chúng được phép tiếp cận để nghiên cứu khoa học, thử nghiệm, huấn luyện AI (dữ liệu có quyền tác giả, quyền liên quan theo quy định của Chính phủ).", "Dữ kiện",
     "Luật 131/2025/QH15 (hiệu lực 01/4/2026): khoản 5 Điều 6, khoản 5 Điều 7 Luật SHTT", VERIFIED],
    ["V13-C30", "Mô hình A/B, bảng vòng đời, luận điểm, nên/không nên, đề xuất bổ sung.", "Diễn giải", "Nhóm 14", GROUP],
    ["V13-C31", "Phương châm “dân biết, dân bàn, dân làm, dân kiểm tra, dân giám sát, dân thụ hưởng”.", "Dữ kiện",
     "Văn kiện Đại hội đại biểu toàn quốc lần thứ XIII (2021), tập I, tr. 27–28 [15]", VERIFIED],
    ["V13-C32", "Công nghệ là một trong những nguồn quyền lực công chủ yếu của xã hội hiện đại.", "Feenberg", "S03, tr. 301", VERIFIED],
    ["V13-C33", "Lợi ích của người tham gia: nảy sinh từ vị trí trong hệ thống kỹ thuật.", "Feenberg", "Feenberg (1992b), tr. 217–218 [17]", VERIFIED],
    ["V13-C34", "Ba con đường can thiệp dân chủ: tranh luận công khai; đối thoại chuyên gia – người dùng; chiếm dụng sáng tạo.", "Feenberg",
     "Bakardjieva & Feenberg (2002), tr. 187 [18]", VERIFIED],
    ["V13-C35", "Treatment IND (1987); tập trung trước trụ sở FDA (10/1988); đường song song và phê duyệt nhanh (1992).", "Dữ kiện",
     "52 FR 19466; 57 FR 13250; 57 FR 58942; FDA (Junod); ACT UP Oral History Project [21][22]", VERIFIED],
    ["V13-C36", "Người bệnh buộc thiết kế thử nghiệm thay đổi, thêm mục tiêu chăm sóc số đông; thay đổi mang tính dân chủ và tiến bộ.", "Feenberg",
     "Feenberg (2008), tr. 25 [19]", VERIFIED],
    ["V13-C37", "Dữ liệu cá nhân chỉ được thu thập đúng phạm vi, mục đích cụ thể, rõ ràng.", "Dữ kiện", "Luật 91/2025/QH15, Điều 3 khoản 2", VERIFIED],
    ["V13-C38", "Bản đồ trách nhiệm: ai giám sát, ai có quyền yêu cầu sửa đổi, ai chịu trách nhiệm khắc phục.", "Dữ kiện", "Mục III.8 (từng căn cứ)", VERIFIED],
    ["V13-C39", "Ba ví dụ quản lý hiệu quả và bảo vệ quyền cùng có lợi; đề xuất bổ sung.", "Diễn giải", "Nhóm 14", GROUP],
]

QUESTIONS_FOR_LECTURER = [
    "Cầu nối Lênin → công nghệ: nhóm đặt trên việc quyền lực công được thực hiện qua hệ thống kỹ thuật, với điểm tựa Feenberg (1992, tr. 301). "
    "Thầy thấy lập luận này đã đúng ý chưa?",
    "Ma trận quyền × mức độ và phép thử bốn câu hỏi là khung của nhóm. Thầy có muốn bổ sung hàng quyền nào, ví dụ quyền được bảo vệ khỏi bị trả thù?",
    "Tình huống cụ thể là người bệnh AIDS và việc thiết kế lại thử nghiệm thuốc (do Feenberg phân tích). Nếu thầy muốn một tình huống gần "
    "Việt Nam hơn, nhóm có thể bổ sung một mô hình minh họa.",
]

REFERENCES = [
    "[1] Feenberg, A. (2003). What Is Philosophy of Technology? Bài giảng cho sinh viên Komaba, tháng 6/2003. (Học liệu giảng viên cung cấp.)",
    "[2] Feenberg, A. (2000). From Essentialism to Constructivism: Philosophy of Technology at the Crossroads. Trong Higgs, E., Light, A. & "
    "Strong, D. (eds.), Technology and the Good Life? University of Chicago Press, tr. 294–315. (Học liệu giảng viên cung cấp; số trang trong tài liệu này dẫn theo bản thảo PDF, đánh số 1–32.)",
    "[3] Feenberg, A. (1992). Subversive Rationalization: Technology, Power, and Democracy. Inquiry, 35(3–4), 301–322. "
    "DOI: 10.1080/00201749208602296.",
    "[4] Dusek, V. (2006). Philosophy of Technology: An Introduction. Blackwell Publishing. (Học liệu giảng viên cung cấp.)",
    "[5] Đề cương Triết học trong lĩnh vực Khoa học và Công nghệ. (Học liệu giảng viên cung cấp.)",
    "[6] Bộ Giáo dục và Đào tạo (2021). Giáo trình Chủ nghĩa xã hội khoa học (dành cho bậc đại học hệ không chuyên lý luận chính trị). "
    "NXB Chính trị quốc gia Sự thật, Hà Nội, chương IV (khoảng tr. 125–128).",
    "[7] V.I. Lênin (1917). Nhà nước và cách mạng, chương V. Trong V.I. Lênin Toàn tập, tập 33. Nxb Tiến bộ, Mátxcơva, tr. 123–124.",
    "[8] Hồ Chí Minh (1949). Dân vận. Báo Sự thật, số 120, 15/10/1949. Trong Hồ Chí Minh Toàn tập, tập 6. NXB Chính trị quốc gia, Hà Nội, 2011, tr. 232.",
    "[9] Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam năm 2013, được sửa đổi, bổ sung theo Nghị quyết số 203/2025/QH15 ngày 16/6/2025.",
    "[10] Luật Thực hiện dân chủ ở cơ sở, số 10/2022/QH15 (hiệu lực 01/7/2023), được sửa đổi, bổ sung bởi Luật số 47/2024/QH15 và Luật số 97/2025/QH15.",
    "[11] Luật Căn cước, số 26/2023/QH15 (hiệu lực 01/7/2024), được sửa đổi bởi Luật số 118/2025/QH15; Văn bản hợp nhất số 09/VBHN-VPQH/2026.",
    "[12] Nghị định số 69/2024/NĐ-CP về định danh và xác thực điện tử, được sửa đổi bởi Nghị định số 169/2025/NĐ-CP và Nghị định số 320/2026/NĐ-CP.",
    "[13] Luật Bảo vệ dữ liệu cá nhân, số 91/2025/QH15 (hiệu lực 01/01/2026); Nghị định số 356/2025/NĐ-CP.",
    "[14] Luật Sở hữu trí tuệ, số 50/2005/QH11, sửa đổi, bổ sung năm 2009, 2019, 2022 và bởi Luật số 131/2025/QH15 (hiệu lực 01/4/2026).",
    "[15] Văn kiện Đại hội đại biểu toàn quốc lần thứ XIII (2021). NXB Chính trị quốc gia Sự thật, tập I, tr. 27–28.",
    "[16] Ảnh Andrew Feenberg: Beatrice Murch, Wikimedia Commons, giấy phép CC BY-SA 3.0. Tiểu sử: Simon Fraser University, "
    "Humanities Institute, hồ sơ A. Feenberg.",
    "[17] Feenberg, A. (1992b). On Being a Human Subject: Interest and Obligation in the Experimental Treatment of Incurable Disease. "
    "The Philosophical Forum, 23(3), 213–230.",
    "[18] Bakardjieva, M. & Feenberg, A. (2002). Community Technology and Democratic Rationalization. The Information Society, 18(3), 181–192.",
    "[19] Feenberg, A. (2008). From Critical Theory of Technology to the Rational Critique of Rationality. Social Epistemology, 22(1), 5–28.",
    "[20] Feenberg, A. (2003). Democratic Rationalization: Technology, Power, and Freedom. Trong Scharff, R. C. & Dusek, V. (eds.), "
    "Philosophy of Technology: The Technological Condition. Blackwell, tr. 652–665.",
    "[21] U.S. Food and Drug Administration: Federal Register 52 FR 19466 (1987, treatment IND); 57 FR 13250 (1992, parallel track); "
    "57 FR 58942 (1992, accelerated approval); Junod, S. W., FDA and Clinical Drug Trials: A Short History.",
    "[22] ACT UP Oral History Project, “Seize Control of the FDA” (11/10/1988).",
    "[23] Luật Hoạt động giám sát của Quốc hội và Hội đồng nhân dân, số 121/2025/QH15; Luật Mặt trận Tổ quốc Việt Nam (VBHN 89/VBHN-VPQH); "
    "Luật Khiếu nại 2011 (sửa đổi bởi Luật số 136/2025/QH15); Luật Trách nhiệm bồi thường của Nhà nước 2017.",
]
