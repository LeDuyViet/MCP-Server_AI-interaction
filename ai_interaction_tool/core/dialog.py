# Main input dialog for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json
import os
from .config import ConfigManager
from ..ui.file_dialog import FileAttachDialog
from ..ui.styles import get_main_stylesheet
from ..utils.translations import get_translations, get_translation
from ..utils.file_utils import read_file_content, validate_file_path
from ..constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, MIN_INPUT_HEIGHT, MAX_FILE_LIST_HEIGHT,
    SHADOW_BLUR_RADIUS, SHADOW_OFFSET, SHADOW_OPACITY
)

class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Khởi tạo config manager
        self.config_manager = ConfigManager()
        
        # Khởi tạo danh sách lưu đường dẫn file đính kèm
        self.attached_files = []
        
        # Thiết lập ngôn ngữ từ cấu hình
        self.current_language = self.config_manager.get_language()
        
        # Từ điển cho đa ngôn ngữ
        self.translations = get_translations()
        
        # Cập nhật tiêu đề cửa sổ theo ngôn ngữ đã chọn
        self.setWindowTitle(self.get_translation("window_title"))
        
        # Thiết lập stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Thêm chọn ngôn ngữ
        self._setup_language_selection()
        
        # Thêm tiêu đề và hướng dẫn
        self._setup_title_and_info()
        
        # Thêm input area
        self._setup_input_area()
        
        # Thêm file attachment area
        self._setup_file_attachment()
        
        # Thêm continue checkbox và warning
        self._setup_continue_options()
        
        # Thêm buttons
        self._setup_buttons()
        
        self.setLayout(self.layout)
        
        # Thiết lập focus cho input khi mở dialog
        self.input.setFocus()
        
        # Thiết lập drop shadow
        self._setup_shadow_effect()
        
        self.result_text = None
        self.result_continue = False
        self.result_ready = False
    
    def _setup_language_selection(self):
        """Thiết lập phần chọn ngôn ngữ"""
        language_layout = QtWidgets.QHBoxLayout()
        self.language_label = QtWidgets.QLabel(self.get_translation("language_label"), self)
        self.language_combo = QtWidgets.QComboBox(self)
        
        # Điều chỉnh thuộc tính cho QComboBox
        self.language_combo.setMaxVisibleItems(2)
        self.language_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.language_combo.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Tiếng Việt", "vi")
        
        # Thiết lập ngôn ngữ từ cấu hình đã lưu
        if self.current_language == "vi":
            self.language_combo.setCurrentIndex(1)
        else:
            self.language_combo.setCurrentIndex(0)
            
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        self.layout.addLayout(language_layout)
    
    def _setup_title_and_info(self):
        """Thiết lập tiêu đề và thông tin hướng dẫn"""
        # Thêm tiêu đề
        self.title_label = QtWidgets.QLabel(self.get_translation("title_label"), self)
        self.title_label.setObjectName("titleLabel")
        self.layout.addWidget(self.title_label)
        
        # Thêm hướng dẫn
        self.info_label = QtWidgets.QLabel(self.get_translation("info_label"), self)
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)
    
    def _setup_input_area(self):
        """Thiết lập khu vực nhập liệu"""
        # Thay thế QLineEdit bằng QTextEdit
        self.input = QtWidgets.QTextEdit(self)
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
        self.input.setMinimumHeight(MIN_INPUT_HEIGHT)
        self.layout.addWidget(self.input)
    
    def _setup_file_attachment(self):
        """Thiết lập khu vực đính kèm file"""
        # Thêm nút đính kèm file và danh sách file đính kèm
        attach_layout = QtWidgets.QHBoxLayout()
        
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.setObjectName("attachBtn")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.attached_files_label = QtWidgets.QLabel(self.get_translation("attached_files_label"), self)
        self.attached_files_label.setVisible(False)
        
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addWidget(self.attached_files_label)
        attach_layout.addStretch()
        
        self.layout.addLayout(attach_layout)
        
        # Danh sách file đính kèm
        self.file_list = QtWidgets.QListWidget(self)
        self.file_list.setMaximumHeight(MAX_FILE_LIST_HEIGHT)
        self.file_list.setVisible(False)
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.file_list)
    
    def _setup_continue_options(self):
        """Thiết lập các tùy chọn tiếp tục cuộc trò chuyện"""
        # Thêm checkbox tiếp tục trò chuyện
        continue_default = self.config_manager.get('ui_preferences.continue_chat_default', True)
        self.continue_checkbox = QtWidgets.QCheckBox(self.get_translation("continue_checkbox"), self)
        self.continue_checkbox.setChecked(continue_default)
        self.continue_checkbox.setToolTip("Khi chọn, Agent sẽ tự động hiển thị lại hộp thoại này sau khi trả lời")
        self.layout.addWidget(self.continue_checkbox)
        
        # Thêm nhãn cảnh báo về quy tắc gọi lại
        self.warning_label = QtWidgets.QLabel(
            self.get_translation("warning_label"), 
            self
        )
        self.warning_label.setObjectName("warningLabel")
        self.warning_label.setWordWrap(True)
        self.layout.addWidget(self.warning_label)
    
    def _setup_buttons(self):
        """Thiết lập các nút điều khiển"""
        # Tạo layout ngang cho các nút
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.submit_btn = QtWidgets.QPushButton(self.get_translation("submit_btn"), self)
        self.submit_btn.clicked.connect(self.submit_text)
        self.submit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.submit_btn.setToolTip("Gửi tin nhắn (Ctrl+Enter)")
        
        self.close_btn = QtWidgets.QPushButton(self.get_translation("close_btn"), self)
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.close_btn.setToolTip("Đóng hộp thoại và kết thúc cuộc trò chuyện")
        
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(button_layout)
    
    def _setup_shadow_effect(self):
        """Thiết lập hiệu ứng đổ bóng"""
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SHADOW_BLUR_RADIUS)
        shadow.setColor(QtGui.QColor(0, 0, 0, SHADOW_OPACITY))
        shadow.setOffset(*SHADOW_OFFSET)
        self.setGraphicsEffect(shadow)
    
    def get_translation(self, key):
        """
        Lấy bản dịch cho khóa ngôn ngữ dựa trên ngôn ngữ hiện tại
        """
        return get_translation(self.current_language, key)
    
    def change_language(self, index):
        """
        Thay đổi ngôn ngữ hiện tại và cập nhật giao diện
        """
        self.current_language = self.language_combo.itemData(index)
        
        # Lưu cấu hình khi thay đổi ngôn ngữ
        self.config_manager.set_language(self.current_language)
        
        # Cập nhật tiêu đề cửa sổ
        self.setWindowTitle(self.get_translation("window_title"))
        
        # Cập nhật các nhãn
        self.title_label.setText(self.get_translation("title_label"))
        self.info_label.setText(self.get_translation("info_label"))
        self.language_label.setText(self.get_translation("language_label"))
        self.attached_files_label.setText(self.get_translation("attached_files_label"))
        self.continue_checkbox.setText(self.get_translation("continue_checkbox"))
        self.warning_label.setText(self.get_translation("warning_label"))
        
        # Cập nhật các nút
        self.attach_btn.setText(self.get_translation("attach_btn"))
        self.submit_btn.setText(self.get_translation("submit_btn"))
        self.close_btn.setText(self.get_translation("close_btn"))
        
        # Cập nhật placeholder
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
    
    def attach_file(self):
        """
        Mở hộp thoại chọn file và thêm file được chọn vào danh sách đính kèm
        """
        # Sử dụng hộp thoại chọn file nâng cao với chế độ cây thư mục
        dialog = FileAttachDialog(self, self.current_language, self.translations)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_files = dialog.get_selected_files()
            
            for file_path in selected_files:
                # Validate file path
                validation = validate_file_path(file_path)
                
                if validation["valid"]:
                    # Kiểm tra xem file đã được đính kèm chưa
                    if file_path not in [file_info["path"] for file_info in self.attached_files]:
                        # Thêm vào danh sách đính kèm
                        file_info = {
                            "path": file_path,
                            "name": os.path.basename(file_path)
                        }
                        self.attached_files.append(file_info)
                        
                        # Hiển thị trong UI
                        self.file_list.addItem(file_info["name"])
                        
                        # Hiển thị danh sách file nếu chưa hiển thị
                        if not self.file_list.isVisible():
                            self.attached_files_label.setVisible(True)
                            self.file_list.setVisible(True)
                    else:
                        QtWidgets.QMessageBox.warning(
                            self, 
                            self.get_translation("error_file_exists"), 
                            self.get_translation("error_file_exists_message")
                        )
                else:
                    QtWidgets.QMessageBox.warning(
                        self, 
                        self.get_translation("error_file_not_exists"), 
                        validation["error"]
                    )
    
    def show_context_menu(self, position):
        """
        Hiển thị menu ngữ cảnh cho danh sách file đính kèm
        """
        menu = QtWidgets.QMenu()
        remove_action = menu.addAction(self.get_translation("remove_file"))
        
        current_item = self.file_list.itemAt(position)
        if current_item:
            action = menu.exec_(self.file_list.mapToGlobal(position))
            if action == remove_action:
                row = self.file_list.row(current_item)
                self.file_list.takeItem(row)
                self.attached_files.pop(row)
                
                # Ẩn danh sách nếu không còn file đính kèm
                if self.file_list.count() == 0:
                    self.attached_files_label.setVisible(False)
                    self.file_list.setVisible(False)

    def submit_text(self):
        """
        Phương thức xử lý khi người dùng nhấn nút Gửi.
        """
        text = self.input.toPlainText()
        if text.strip() or self.attached_files:
            result_dict = {
                "text": text,
                "language": self.current_language
            }
            
            # Thêm thông tin về file đính kèm nếu có
            if self.attached_files:
                result_dict["attached_files"] = []
                for file_info in self.attached_files:
                    try:
                        file_path = file_info["path"]
                        file_name = file_info["name"]
                        
                        # Đọc nội dung file sử dụng utility function
                        file_result = read_file_content(file_path)
                        
                        if file_result["success"]:
                            # Thêm thông tin file vào kết quả
                            result_dict["attached_files"].append({
                                "path": file_path,
                                "name": file_name,
                                "content": file_result["content"],
                                "encoding": file_result["encoding"]
                            })
                        else:
                            result_dict["attached_files"].append({
                                "path": file_path,
                                "name": file_name,
                                "error": file_result["error"]
                            })
                    except Exception as e:
                        result_dict["attached_files"].append({
                            "path": file_path,
                            "name": file_name,
                            "error": str(e)
                        })
            
            self.result_text = json.dumps(result_dict, ensure_ascii=False)
            self.result_continue = self.continue_checkbox.isChecked()
            self.result_ready = True
            self.input.clear()
            self.accept()
    
    # Cho phép gửi bằng phím Enter
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.submit_text()
        else:
            super().keyPressEvent(event)

    @staticmethod
    def getText():
        dialog = InputDialog()
        result = dialog.exec_()
        if dialog.result_ready:
            return dialog.result_text, dialog.result_continue, True
        else:
            return "", False, False 