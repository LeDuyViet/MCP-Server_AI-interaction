from mcp.server.fastmcp import FastMCP
import json
from typing import Dict, List, Any, Optional
# Import công cụ từ package đã tái cấu trúc
from reasoner_tools.mcts_tool import mcts_reasoning

# Tạo MCP server
mcp = FastMCP("Reasoner Thinking")

# Đăng ký công cụ đã import
mcp.add_tool(mcts_reasoning)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")