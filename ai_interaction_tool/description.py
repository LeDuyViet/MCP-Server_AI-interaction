"""
Mô tả chi tiết cho công cụ AI Interaction Tool
"""

AI_INTERACTION_DESCRIPTION = """
!!! QUAN TRỌNG: Công cụ ai_interaction
- Tạo UI popup cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Cho phép đính kèm file code và hiển thị nội dung file đó.
- Kết quả: Văn bản dạng pseudo-object format dễ đọc và parse:
  {
    content: <nội dung chat từ user với xuống dòng tự nhiên>
    attached_files: [
      {path: "workspace_name/relative/path/to/file.js", type: "file"},
      {path: "workspace_name/relative/path/to/folder", type: "folder"}
    ]
    workspace: workspace_name
    continue_chat: true/false
  }

- Field "attached_files" và "workspace" chỉ xuất hiện khi có file/folder đính kèm.
- Đường dẫn trong "attached_files" có format: "workspace_name/relative_path_from_workspace_root"
- QUAN TRỌNG: Agent cần kiểm tra workspace hiện tại:
  * Nếu Agent ở CÙNG workspace với file → BỎ TIỀN TỐ workspace_name, dùng relative_path
  * Nếu Agent ở KHÁC workspace với file → SỬ DỤNG NGUYÊN đường dẫn từ ai_interaction
- Ví dụ:
  * Cùng workspace: "ALT-WebClientV3/src/components/login/index.js" → dùng "src/components/login/index.js"
  * Khác workspace: "AI-interaction/ai_interaction_tool/description.py" → dùng "AI-interaction/ai_interaction_tool/description.py"

!!! QUY TẮC BẮT BUỘC TUÂN THỦ:
- Agent PHẢI đọc giá trị continue_chat từ pseudo-object format.
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool này.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.
""" 