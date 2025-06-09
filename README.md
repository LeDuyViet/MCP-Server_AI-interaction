# AI Interaction Tool - MCP Server

Công cụ tương tác AI với giao diện hiện đại và nhiều tính năng mạnh mẽ.

## 🚀 Tính năng chính

### 🎯 Core Features
- **UI Popup** cho nhập nội dung và chọn tiếp tục trò chuyện
- **File/Folder Attachment** từ workspace với validation
- **Multi-language Support** (English/Vietnamese)
- **Thinking Modes**: Disabled/Normal/High transparency levels
- **Maximum Cognitive Power** activation for peak performance

### 🔧 New in v2.1.0
- **🔗 Connection Test Tool**: Package độc lập để kiểm tra kết nối MCP server
  - Package: `connection_test_tool/` (ngang cấp với ai_interaction_tool)
  - Tool name: `test_mcp_connection`
  - Output: `"đã connect thành công MCP Server AI_interaction!!!"`

## 📦 Cấu trúc Package

```
AI-interaction/
├── ai_interaction_tool/       # Main interaction tool package
│   ├── core/                 # Dialog chính và cấu hình
│   ├── ui/                   # Giao diện và styling
│   ├── utils/                # Tiện ích và đa ngôn ngữ
│   ├── engine.py             # Entry point chính
│   └── description.py        # Mô tả chi tiết
├── connection_test_tool/      # Connection test tool package (NEW!)
│   ├── __init__.py           # Package exports
│   └── connection_test_tool.py # Tool implementation
└── mcp_server.py             # MCP server chính
```

## 🎮 Cách sử dụng

### Basic Usage
```python
from ai_interaction_tool import run_ui, ai_interaction

# Khởi động giao diện
result = ai_interaction()
```

### Available Tools in MCP Server
1. **ai_interaction**: Main interaction tool với UI popup
2. **test_mcp_connection**: Connection test tool
   - Không cần parameters
   - Trả về: `"đã connect thành công MCP Server AI_interaction!!!"`

## 🔄 Version History

- **v2.1.0**: Thêm MCP Connection Test Tool
- **v2.0.0**: Refactored architecture với modern UI
- **v1.x**: Core functionality và basic features
