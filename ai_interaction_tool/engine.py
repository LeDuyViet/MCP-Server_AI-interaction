# Main engine for AI Interaction Tool
# Refactored version - uses components from separate modules
from PyQt5 import QtWidgets, QtGui
import sys
import json
from .core.dialog import InputDialog
from .constants import METADATA_FORMAT

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
    
    # Chuẩn bị chuỗi metadata
    metadata_str = METADATA_FORMAT.format(str(continue_chat).lower())

    if ok:
        # Phân tích nội dung từ dialog
        try:
            # Parse JSON từ kết quả của dialog
            result_dict = json.loads(text)
            user_text = result_dict.get("text", "")
            attached_files = result_dict.get("attached_files", [])
            language = result_dict.get("language", "en")  # Lấy thông tin ngôn ngữ
            
            # Tạo kết quả văn bản thuần túy, bắt đầu với tin nhắn của người dùng
            core_text = user_text
            
            # Thêm nội dung file đính kèm vào văn bản kết quả (nếu có)
            if attached_files:
                # Chọn tiêu đề phù hợp với ngôn ngữ
                attachment_header = "Files Attached" if language == "en" else "Files Đính Kèm"
                core_text += f"\n\n------ {attachment_header} ------"
                
                for idx, file_info in enumerate(attached_files):
                    if "content" in file_info:
                        file_path = file_info.get('path', 'unknown_path')
                        file_name = file_info.get('name', 'unnamed')
                        file_content = file_info.get('content', '')
                        
                        # Thêm thông tin file vào kết quả văn bản
                        core_text += f"\n\n{file_path}:\n{file_content}"
                        
                        # Thêm dấu phân cách giữa các file (trừ file cuối)
                        if idx < len(attached_files) - 1:
                            core_text += "\n\n---"
            
            # Log về trạng thái continue_chat
            warning_msg = "[AI_INTERACTION_TOOL] WARNING: continue_chat=True - Agent MUST call this tool again after responding!" if language == "en" else "[AI_INTERACTION_TOOL] CẢNH BÁO: continue_chat=True - Agent PHẢI gọi lại tool này sau khi trả lời!"
            info_msg = "[AI_INTERACTION_TOOL] continue_chat=False - No need to call the tool again." if language == "en" else "[AI_INTERACTION_TOOL] continue_chat=False - Không cần gọi lại tool."
            
            if continue_chat:
                print(warning_msg, file=sys.stderr)
            else:
                print(info_msg, file=sys.stderr)
            
            # Tạo văn bản trả về hoàn chỉnh với metadata ở đầu và cuối
            full_response_text = f"{metadata_str}\n{core_text}\n{metadata_str}"
            return full_response_text
            
        except json.JSONDecodeError:
            # Xử lý trường hợp không phải JSON
            full_response_text = f"{metadata_str}\n{text}\n{metadata_str}"
            return full_response_text
    else:
        # Trường hợp dialog bị đóng hoặc không có input
        full_response_text = f"{metadata_str}\n\n{metadata_str}"  # Trả về metadata với text rỗng ở giữa
        return full_response_text

"""
!!! QUY TẮC BẮT BUỘC ĐỐI VỚI AGENT:
- Công cụ ai_interaction trả về văn bản thuần túy.
- Đây là KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User.
- BẮT BUỘC luôn sử dụng công cụ này trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn.
- Văn bản trả về sẽ BẮT ĐẦU và KẾT THÚC bằng chuỗi metadata:
  [AI_INTERACTION_TOOL] METADATA: {'continue_chat': true/false}
- Nội dung tin nhắn và file đính kèm (nếu có) nằm GIỮA hai chuỗi metadata đó.
- Agent PHẢI đọc giá trị continue_chat từ chuỗi metadata trong văn bản trả về.
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool này.
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
- Phải hiểu rằng tất cả nội dung từ User sẽ đến từ công cụ này, đây là kênh chat chính của User.
- Bất kỳ khi nào nhận được tin nhắn từ User, PHẢI sử dụng công cụ ai_interaction để tiếp tục cuộc trò chuyện.
"""

