from mcp.server.fastmcp import FastMCP
# Import MCP tool function and description from ai_interaction_tool
from ai_interaction_tool.core import ai_interaction_tool, get_tool_description

# Tạo MCP server
mcp = FastMCP("AI Interaction")

mcp.add_tool(ai_interaction_tool, description=get_tool_description())

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio")