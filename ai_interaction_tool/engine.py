# Main engine for AI Interaction Tool
# Refactored version - uses components from separate modules
from PyQt5 import QtWidgets, QtGui
import sys
import json
from .core.dialog import InputDialog

# Legacy classes for backward compatibility (now imported from separate modules)
from .ui.file_tree import FileSystemModel, FileTreeView, FileTreeDelegate
from .ui.file_dialog import FileAttachDialog

def run_ui(*args, **kwargs):
    """
    Hàm chính để chạy giao diện người dùng và trả về kết quả.
    Đây là entry point chính cho AI Interaction Tool.
    """
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Thiết lập font mặc định cho toàn ứng dụng
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)
    
    text, continue_chat, ok = InputDialog.getText()

    if ok:
        # Phân tích nội dung từ dialog
        try:
            # Parse JSON từ kết quả của dialog
            result_dict = json.loads(text)
            user_text = result_dict.get("text", "")
            attached_files = result_dict.get("attached_files", [])
            language = result_dict.get("language", "en")  # Lấy thông tin ngôn ngữ
            
            # Log về trạng thái continue_chat
            warning_msg = "[AI_INTERACTION_TOOL] WARNING: continue_chat=true - Agent MUST call this tool again after responding!" if language == "en" else "[AI_INTERACTION_TOOL] CẢNH BÁO: continue_chat=true - Agent PHẢI gọi lại tool này sau khi trả lời!"
            info_msg = "[AI_INTERACTION_TOOL] continue_chat=false - No need to call the tool again." if language == "en" else "[AI_INTERACTION_TOOL] continue_chat=false - Không cần gọi lại tool."
            
            if continue_chat:
                print(warning_msg, file=sys.stderr)
            else:
                print(info_msg, file=sys.stderr)
            
            # Tạo pseudo-object format với separate fields (best of both worlds)
            full_response_text = "{\n"
            full_response_text += f"  content: {user_text}\n"
            
            # Thêm attached files nếu có
            if attached_files:
                full_response_text += "  attached_files: [\n"
                workspace_name = None
                
                for i, file_info in enumerate(attached_files):
                    if "relative_path" in file_info:
                        relative_path = file_info.get('relative_path', 'unknown_path')
                        item_type = file_info.get('type', 'unknown')
                        workspace_name = file_info.get('workspace_name', '')
                        
                        comma = "," if i < len(attached_files) - 1 else ""
                        full_response_text += f'    {{path: "{relative_path}", type: "{item_type}"}}{comma}\n'
                    elif "error" in file_info:
                        comma = "," if i < len(attached_files) - 1 else ""
                        error_name = file_info.get('name', 'unknown')
                        error_msg = file_info.get('error', 'Unknown error')
                        full_response_text += f'    {{name: "{error_name}", error: "{error_msg}"}}{comma}\n'
                
                full_response_text += "  ]\n"
                
                # Thêm workspace info
                if workspace_name:
                    full_response_text += f"  workspace: {workspace_name}\n"
            
            full_response_text += f"  continue_chat: {str(continue_chat).lower()}\n"
            full_response_text += f"  language: {language}\n"
            full_response_text += "}"
            return full_response_text
            
        except json.JSONDecodeError:
            # Xử lý trường hợp không phải JSON
            return f"""{{
  content: {text}
  continue_chat: {str(continue_chat).lower()}
  language: en
}}"""
    else:
        # Trường hợp dialog bị đóng hoặc không có input
        return """{
  content: 
  continue_chat: false
  language: en
}"""

"""
!!! QUY TẮC BẮT BUỘC ĐỐI VỚI AGENT:
- Công cụ ai_interaction trả về pseudo-object format dễ đọc và dễ parse.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Format trả về (Pseudo-object với separate fields):
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
- Content field không bị escape newlines, giữ formatting tự nhiên.
- Agent PHẢI đọc giá trị continue_chat từ pseudo-object.
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool này.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.
"""

