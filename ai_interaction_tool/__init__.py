# AI Interaction Tool Package
# Refactored for better maintainability and organization

from .core.dialog import InputDialog
from .core.config import ConfigManager
from .ui.file_dialog import FileAttachDialog
from .ui.file_tree import FileTreeView, FileSystemModel, FileTreeDelegate
from .ui.styles import get_main_stylesheet, get_file_dialog_stylesheet
from .utils.translations import get_translations, get_translation
from .utils.file_utils import read_file_content, validate_file_path

# Legacy compatibility - main entry point
from .engine import run_ui

__version__ = "2.0.0"
__author__ = "AI Interaction Tool Team"
__all__ = [
    # Core components
    'InputDialog',
    'ConfigManager',
    
    # UI components
    'FileAttachDialog',
    'FileTreeView',
    'FileSystemModel', 
    'FileTreeDelegate',
    'get_main_stylesheet',
    'get_file_dialog_stylesheet',
    
    # Utilities
    'get_translations',
    'get_translation',
    'read_file_content',
    'validate_file_path',
    
    # Main entry point
    'run_ui'
]

def ai_interaction(*args, **kwargs):
    return run_ui(*args, **kwargs)

"""
!!! QUAN TRỌNG: Công cụ ai_interaction với Workspace Support
- Tạo UI cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Hỗ trợ đính kèm file/folder với workspace-relative paths.
- Trả về: Pseudo-object format với separate fields (dễ đọc, không escape newlines):
  
  {
    content: <nội dung chat từ user với xuống dòng tự nhiên>
    attached_files: [
      {path: "workspace/path/to/file.js", type: "file"},
      {path: "workspace/path/to/folder", type: "folder"}
    ]
    workspace: workspace_name
    continue_chat: true/false
    language: en/vi
  }

- Field "attached_files" và "workspace" chỉ xuất hiện khi có file/folder đính kèm.
- Đường dẫn trong "attached_files" là relative từ workspace root.
- Content field giữ formatting tự nhiên, không escape \n.
- Agent PHẢI đọc giá trị continue_chat từ pseudo-object.

!!! QUY TẮC BẮT BUỘC:
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool này.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.

!!! WORKSPACE & PATH HANDLING:
- User chọn workspace directory trước khi đính kèm file/folder.
- Tất cả paths trả về là relative từ workspace (ví dụ: "ProjectName/src/file.js").
- Hỗ trợ Unicode, special characters, và edge cases trong tên file/folder.
- Cross-platform compatible với forward slash paths.
"""
