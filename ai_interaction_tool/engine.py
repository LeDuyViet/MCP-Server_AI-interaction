from PyQt5 import QtWidgets, QtCore
import sys
import json

class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Interaction Tool")
        self.setFixedSize(400, 200)
        self.layout = QtWidgets.QVBoxLayout()
        self.input = QtWidgets.QLineEdit(self)
        self.input.setPlaceholderText("Nhập nội dung...")
        self.continue_checkbox = QtWidgets.QCheckBox("Tiếp tục trò chuyện", self)
        self.continue_checkbox.setChecked(True)
        
        # Thêm nhãn cảnh báo về quy tắc gọi lại
        self.warning_label = QtWidgets.QLabel(
            "<b style='color:red'>CHÚ Ý: Nếu tiếp tục trò chuyện được chọn, Agent PHẢI gọi lại công cụ này!</b>", 
            self
        )
        self.warning_label.setWordWrap(True)
        
        self.submit_btn = QtWidgets.QPushButton("Gửi", self)
        self.submit_btn.clicked.connect(self.submit_text)
        self.close_btn = QtWidgets.QPushButton("Đóng", self)
        self.close_btn.clicked.connect(self.close)
        
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.continue_checkbox)
        self.layout.addWidget(self.warning_label)
        self.layout.addWidget(self.submit_btn)
        self.layout.addWidget(self.close_btn)
        self.setLayout(self.layout)
        self.result_text = None
        self.result_continue = False
        self.result_ready = False

    def submit_text(self):
        text = self.input.text()
        if text.strip():
            self.result_text = text
            self.result_continue = self.continue_checkbox.isChecked()
            self.result_ready = True
            self.input.clear()
            self.accept()

    @staticmethod
    def getText():
        dialog = InputDialog()
        result = dialog.exec_()
        if dialog.result_ready:
            return dialog.result_text, dialog.result_continue, True
        else:
            return "", False, False

def run_ui(*args, **kwargs):
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    text, continue_chat, ok = InputDialog.getText()
    if ok:
        result = {"text": json.dumps(text, ensure_ascii=False), "continue_chat": continue_chat}
        # Thêm log khi continue_chat là true để nhấn mạnh quy tắc
        if continue_chat:
            print("[AI_INTERACTION_TOOL] CẢNH BÁO: continue_chat=True - Agent PHẢI gọi lại công cụ này sau khi trả lời!", file=sys.stderr)
        return result
    else:
        return {"text": "", "continue_chat": False}

"""
!!! QUY TẮC BẮT BUỘC ĐỐI VỚI AGENT:
- Công cụ ai_interaction trả về {"text": <nội dung>, "continue_chat": <true/false>}
- Nếu continue_chat là true: Agent PHẢI tự động gọi lại tool này sau khi trả lời. 
  KHÔNG ĐƯỢC PHÉP BỎ QUA QUY TẮC NÀY TRONG BẤT KỲ TRƯỜNG HỢP NÀO.
- Nếu false: Dừng lại.
- Luôn trả lời User tại chat chính, không nhắc lại nội dung.
"""
