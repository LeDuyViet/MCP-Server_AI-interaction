from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, List, Any, Optional
# Import công cụ từ package đã tái cấu trúc
from ai_interaction_tool import ai_interaction

ai_interaction_description = """
!!! QUAN TRỌNG: Công cụ ai_interaction
- Tạo UI popup cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Kết quả: {"text": <nội dung>, "continue_chat": <true/false>}

!!! QUY TẮC BẮT BUỘC TUÂN THỦ:
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool (KHÔNG ĐƯỢC BỎ QUA TRONG BẤT KỲ TRƯỜNG HỢP NÀO).
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
"""

# Tạo MCP server
mcp = FastMCP("AI Interaction")

# Đăng ký công cụ đã import với mô tả chi tiết
mcp.add_tool(ai_interaction, description=ai_interaction_description)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")