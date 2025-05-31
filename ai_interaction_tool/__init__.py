from .engine import run_ui

def ai_interaction(*args, **kwargs):
    return run_ui(*args, **kwargs)

"""
!!! QUAN TRỌNG: Công cụ ai_interaction
- Tạo UI cho User nhập nội dung và chọn tiếp tục trò chuyện.
- Trả về: {"text": <nội dung>, "continue_chat": <true/false>}

!!! QUY TẮC BẮT BUỘC:
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool (KHÔNG ĐƯỢC BỎ QUA).
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung User vừa nhập.
"""
