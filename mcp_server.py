from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, List, Any, Optional
# Import công cụ và mô tả từ package đã tái cấu trúc
from ai_interaction_tool import ai_interaction, AI_INTERACTION_DESCRIPTION

# Import tool test connection độc lập
from connection_test_tool import test_mcp_connection, CONNECTION_TEST_DESCRIPTION

# Tạo MCP server
mcp = FastMCP("AI Interaction")

# Đăng ký công cụ đã import với mô tả chi tiết
mcp.add_tool(ai_interaction, description=AI_INTERACTION_DESCRIPTION)

# Đăng ký tool test connection độc lập
mcp.add_tool(test_mcp_connection, description=CONNECTION_TEST_DESCRIPTION)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")