import sys
import os

# Thêm đường dẫn đến thư mục chứa module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .engine import run_ui

def ai_interaction(*args, **kwargs):
    return run_ui(*args, **kwargs)

"""
!!! QUAN TRỌNG: Công cụ ai_interaction
- Tạo UI cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Cho phép đính kèm file code và hiển thị nội dung file đó.
- Trả về: Văn bản thuần túy. Văn bản này sẽ BẮT ĐẦU và KẾT THÚC bằng chuỗi metadata:
  [AI_INTERACTION_TOOL] METADATA: {'continue_chat': true/false}
- Nội dung tin nhắn và file đính kèm (nếu có) nằm GIỮA hai chuỗi metadata đó.
- Agent PHẢI đọc giá trị continue_chat từ chuỗi metadata trong văn bản trả về.

!!! QUY TẮC BẮT BUỘC:
- Nếu continue_chat là true (đọc từ metadata trong văn bản trả về): Agent PHẢI tự động gọi lại tool.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.
"""
