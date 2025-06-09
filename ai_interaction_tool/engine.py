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
            language = result_dict.get("language", "vi")  # Mặc định tiếng Việt
            enable_thinking = result_dict.get("enable_thinking", "false")  # Có thể là "false", "normal", hoặc "high"
            max_reasoning = result_dict.get("max_reasoning", False)  # Maximum reasoning protocol
            
            # Log về trạng thái continue_chat
            warning_msg = "[AI_INTERACTION_TOOL] CẢNH BÁO: continue_chat=true - Agent PHẢI gọi lại tool này sau khi trả lời!"
            info_msg = "[AI_INTERACTION_TOOL] continue_chat=false - Không cần gọi lại tool."
            
            if continue_chat:
                print(warning_msg, file=sys.stderr)
            else:
                print(info_msg, file=sys.stderr)
            
            # Tạo pseudo-object format với separate fields (best of both worlds)
            full_response_text = "{\n"
            
            # Bổ sung logic nhắc nhở về quy tắc quan trọng
            enhanced_content = user_text
            enhanced_content = "Nhớ áp dụng rule về continue_chat, enable_thinking và max_reasoning, cả quy tắc về 2 thinking block nữa. " + enhanced_content

            full_response_text += f"  content: {enhanced_content}\n"
            
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
            full_response_text += f"  enable_thinking: {enable_thinking}\n"
            full_response_text += f"  max_reasoning: {str(max_reasoning).lower()}\n"
            full_response_text += "}"
            return full_response_text
            
        except json.JSONDecodeError:
            # Xử lý trường hợp không phải JSON
            enhanced_text = text
            if continue_chat:
                enhanced_text += "\n\n"
                enhanced_text += "🚨 NHẮC NHỞ QUAN TRỌNG: continue_chat=true → Agent PHẢI gọi lại tool này sau khi trả lời!"
            
            return f"""{{
  content: {enhanced_text}
  continue_chat: {str(continue_chat).lower()}
  enable_thinking: false
  max_reasoning: false
}}"""
    else:
        # Trường hợp dialog bị đóng hoặc không có input
        return """{
  content: 
  continue_chat: false
  enable_thinking: false
  max_reasoning: false
}"""