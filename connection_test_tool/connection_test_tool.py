#!/usr/bin/env python3
"""
Connection Test Tool - Standalone MCP Tool
Tool độc lập để kiểm tra kết nối MCP Server AI_interaction
"""

def test_mcp_connection():
    """
    Tool đơn giản để test kết nối MCP Server AI_interaction
    
    Returns:
        str: Thông báo kết nối thành công
    """
    return "đã connect thành công MCP Server AI_interaction!!!"

# Tool description cho MCP server
CONNECTION_TEST_DESCRIPTION = """
Tool đơn giản để kiểm tra kết nối MCP Server AI_interaction.

Chức năng:
- Kiểm tra xem MCP server đã được kết nối thành công hay chưa
- Trả về thông báo xác nhận kết nối

Cách sử dụng:
- Không cần tham số đầu vào
- Gọi tool và nhận thông báo kết nối thành công

Output:
- "đã connect thành công MCP Server AI_interaction!!!"
""" 