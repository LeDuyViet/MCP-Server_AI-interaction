# Translation utilities for AI Interaction Tool

def get_translations():
    """
    Trả về từ điển các bản dịch cho tất cả ngôn ngữ được hỗ trợ
    """
    return {
        "en": {
            "window_title": "AI Interaction Tool",
            "title_label": "Enter your message",
            "info_label": "Type your message and press 'Send' or Ctrl+Enter to send. You can also attach files.",
            "input_placeholder": "Type your message...",
            "attach_btn": "Attach file",
            "attached_files_label": "Attached files:",
            "continue_checkbox": "Continue conversation",
            "warning_label": "NOTE: If continue conversation is checked, Agent MUST call this tool again!",
            "submit_btn": "Send",
            "close_btn": "Close",
            "language_label": "Language:",
            "error_file_exists": "Error",
            "error_file_exists_message": "This file is already attached!",
            "error_file_not_exists": "Error",
            "error_file_not_exists_message": "File does not exist!",
            "remove_file": "Remove this file",
            
            # File dialog translations
            "file_dialog_title": "Select Files",
            "path_placeholder": "Enter path to folder",
            "browse_btn": "Browse",
            "go_btn": "Go",
            "clear_btn": "Clear All",
            "cancel_btn": "Cancel",
            "select_folder": "Select Folder",
            "error": "Error",
            "path_not_exist": "The specified path does not exist!",
            "selected_files": "Selected Files",
            "path_input_label": "Path:",
            "or_text": "OR",
            "paste_path_label": "Paste a path:"
        },
        "vi": {
            "window_title": "Công Cụ Tương Tác AI",
            "title_label": "Nhập nội dung của bạn",
            "info_label": "Nhập nội dung tin nhắn và nhấn 'Gửi' hoặc Ctrl+Enter để gửi. Bạn cũng có thể đính kèm file.",
            "input_placeholder": "Nhập nội dung...",
            "attach_btn": "Đính kèm file",
            "attached_files_label": "File đính kèm:",
            "continue_checkbox": "Tiếp tục trò chuyện",
            "warning_label": "CHÚ Ý: Nếu tiếp tục trò chuyện được chọn, Agent PHẢI gọi lại công cụ này!",
            "submit_btn": "Gửi",
            "close_btn": "Đóng",
            "language_label": "Ngôn ngữ:",
            "error_file_exists": "Lỗi",
            "error_file_exists_message": "File này đã được đính kèm!",
            "error_file_not_exists": "Lỗi",
            "error_file_not_exists_message": "File không tồn tại!",
            "remove_file": "Xóa file này",
            
            # File dialog translations
            "file_dialog_title": "Chọn File",
            "path_placeholder": "Nhập đường dẫn thư mục",
            "browse_btn": "Duyệt",
            "go_btn": "Đi đến",
            "clear_btn": "Xóa tất cả",
            "cancel_btn": "Hủy",
            "select_folder": "Chọn Thư Mục",
            "error": "Lỗi",
            "path_not_exist": "Đường dẫn không tồn tại!",
            "selected_files": "File Đã Chọn",
            "path_input_label": "Đường dẫn:",
            "or_text": "HOẶC",
            "paste_path_label": "Dán đường dẫn:"
        }
    }

def get_translation(language, key):
    """
    Lấy bản dịch cho key theo ngôn ngữ chỉ định
    
    Args:
        language (str): Mã ngôn ngữ (en, vi)
        key (str): Key của text cần dịch
        
    Returns:
        str: Text đã dịch hoặc key nếu không tìm thấy
    """
    translations = get_translations()
    lang_dict = translations.get(language, {})
    return lang_dict.get(key, key) 