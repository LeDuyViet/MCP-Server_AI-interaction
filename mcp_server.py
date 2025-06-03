from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, List, Any, Optional
# Import công cụ từ package đã tái cấu trúc
from ai_interaction_tool import ai_interaction

ai_interaction_description = """
!!! QUAN TRỌNG: Công cụ ai_interaction
- Tạo UI popup cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Cho phép đính kèm file code và hiển thị nội dung file đó.
- Kết quả: Văn bản thuần túy. Văn bản này sẽ BẮT ĐẦU và KẾT THÚC bằng chuỗi metadata:
  [AI_INTERACTION_TOOL] METADATA: {'continue_chat': true/false}
- Nội dung tin nhắn và file đính kèm (nếu có) nằm GIỮA hai chuỗi metadata đó.
- Agent PHẢI đọc giá trị continue_chat từ chuỗi metadata trong văn bản trả về.

!!! QUY TẮC BẮT BUỘC TUÂN THỦ:
- Nếu continue_chat là true (đọc từ metadata trong văn bản trả về): Agent PHẢI tự động gọi lại tool.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.
"""

# Tạo MCP server
mcp = FastMCP("AI Interaction")

# Đăng ký công cụ đã import với mô tả chi tiết
mcp.add_tool(ai_interaction, description=ai_interaction_description)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")