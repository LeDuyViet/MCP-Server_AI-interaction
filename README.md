# AI Interaction Tool - MCP Server

**Công cụ tương tác AI với giao diện hiện đại và nhiều tính năng mạnh mẽ cho Model Context Protocol (MCP)**

## 🚀 Tính năng chính

### 🎯 Core Features
- **UI Popup** cho nhập nội dung và chọn tiếp tục trò chuyện
- **File/Folder Attachment** từ workspace với validation và preview
- **Multi-language Support** (English/Vietnamese)
- **Thinking Modes**: Disabled/Normal/High transparency levels
- **Maximum Cognitive Power** activation for peak performance
- **Tag-based Output Format** tích hợp với system prompt rules
- **Workspace-aware Path Processing** cho cross-project compatibility

### 🔧 New in v2.1.0
- **🔗 Connection Test Tool**: Package độc lập để kiểm tra kết nối MCP server
  - Tool name: `test_mcp_connection`
  - Output: `"đã connect thành công MCP Server AI_interaction!!!"`
- **Enhanced UI/UX** với PyQt5 modern interface
- **Structured Tag-based Output** cho perfect integration với AI agents

## 📋 Hướng dẫn Cài đặt và Sử dụng

### 📥 Bước 1: Clone Repository
```bash
git clone https://github.com/your-username/AI-interaction.git
cd AI-interaction
```

### 🐍 Bước 2: Cài đặt Python
- **Yêu cầu**: Python 3.8+ 
- Download từ [python.org](https://www.python.org/downloads/)
- Hoặc sử dụng package manager:
  ```bash
  # Windows với Chocolatey
  choco install python
  
  # macOS với Homebrew
  brew install python
  
  # Ubuntu/Debian
  sudo apt update && sudo apt install python3 python3-pip
  ```

### 📦 Bước 3: Cài đặt Dependencies
```bash
# Sử dụng pip
pip install -r requirements.txt

# Hoặc sử dụng uv (recommended cho performance)
pip install uv
uv pip install -r requirements.txt
```

### ⚙️ Bước 4: Cấu hình MCP Server trong Claude Desktop

Thêm configuration sau vào file cấu hình Claude Desktop:

**Đường dẫn file cấu hình:**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Nội dung cấu hình:**
```json
{
  "mcpServers": {
    "AI_interaction": {
      "command": "python",
      "args": ["E:/MCP-servers-github/AI-interaction/mcp_server.py"],
      "stdio": true,
      "enabled": true
    }
  }
}
```

**⚠️ Lưu ý**: Thay đổi đường dẫn `E:/MCP-servers-github/AI-interaction/mcp_server.py` thành đường dẫn tuyệt đối đến file `mcp_server.py` trên hệ thống của bạn.

### 🚀 Bước 5: Khởi động và Kiểm tra

1. **Restart Claude Desktop** sau khi cấu hình MCP server
2. **Kiểm tra kết nối** bằng cách gọi tool `test_mcp_connection`
3. **Sử dụng** tool `ai_interaction` để bắt đầu tương tác

## 📦 Cấu trúc Package

```
AI-interaction/
├── ai_interaction_tool/       # Main interaction tool package
│   ├── core/                 # Dialog chính và cấu hình
│   │   ├── dialog.py         # InputDialog với PyQt5 UI
│   │   └── config.py         # Configuration management
│   ├── ui/                   # Giao diện và styling
│   │   ├── file_dialog.py    # File attachment dialogs
│   │   ├── file_tree.py      # File system tree view
│   │   └── styles.py         # Modern UI styling
│   ├── utils/                # Tiện ích và đa ngôn ngữ
│   │   ├── translations.py   # Multi-language support
│   │   └── file_utils.py     # File operation utilities
│   ├── engine.py             # Entry point chính
│   ├── description.py        # Mô tả chi tiết tool
│   └── __init__.py           # Package exports
├── main.py                   # Legacy entry point
├── mcp_server.py             # MCP server implementation
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## 🎮 Cách sử dụng

### Available Tools in MCP Server

#### 1. **ai_interaction**: Main Interactive Tool
- **Chức năng**: Tạo UI popup cho user input với file attachment
- **Output**: Structured tag-based format
- **Tích hợp**: Perfect integration với system prompt rules
- **Use cases**: 
  - Nhập nội dung phức tạp với formatting
  - Attach files/folders từ workspace
  - Control AI thinking modes và reasoning levels

#### 2. **test_mcp_connection**: Connection Test Tool
- **Chức năng**: Kiểm tra kết nối MCP server
- **Parameters**: Không cần parameters
- **Output**: `"đã connect thành công MCP Server AI_interaction!!!"`
- **Use case**: Validation MCP server setup

### Basic Usage Examples

```python
# Programmatic usage
from ai_interaction_tool import ai_interaction

# Khởi động giao diện interactive
result = ai_interaction()
print(result)  # Structured output với tags
```

### Output Format
AI Interaction Tool sử dụng clean tag-based format:

```
User message content với natural line breaks

<AI_INTERACTION_ATTACHED_FILES>
FOLDERS:
- workspace_name/relative/path/to/folder

FILES:
- workspace_name/relative/path/to/file.js
</AI_INTERACTION_ATTACHED_FILES>

<AI_INTERACTION_WORKSPACE>workspace_name</AI_INTERACTION_WORKSPACE>
<AI_INTERACTION_CONTINUE_CHAT>true/false</AI_INTERACTION_CONTINUE_CHAT>
<AI_INTERACTION_MAX_REASONING>true/false</AI_INTERACTION_MAX_REASONING>
```

## 🔧 Troubleshooting

### Common Issues

1. **"Command not found" error**
   - Kiểm tra Python đã được cài đặt và trong PATH
   - Verify đường dẫn tuyệt đối trong MCP config

2. **"Module not found" error**
   - Chạy `pip install -r requirements.txt`
   - Kiểm tra virtual environment nếu đang sử dụng

3. **UI không hiển thị**
   - Đảm bảo PyQt5 đã được cài đặt correctly
   - Kiểm tra display settings và desktop environment

4. **File attachment không hoạt động**
   - Verify file permissions và access rights
   - Kiểm tra workspace path configuration

### Debug Mode
Để debug issues, chạy server trực tiếp:
```bash
python mcp_server.py
```

## 🔄 Version History

- **v2.1.0**: Thêm MCP Connection Test Tool, Enhanced UI/UX
- **v2.0.0**: Refactored architecture với modern PyQt5 UI
- **v1.x**: Core functionality và basic features

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/AI-interaction/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/AI-interaction/discussions)
- **Email**: your-email@example.com

---

**🚀 Enhanced AI Interaction Tool - Breakthrough in MCP Architecture!**
