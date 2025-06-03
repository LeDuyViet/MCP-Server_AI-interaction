from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json
import os
from datetime import datetime

class FileSystemModel(QtWidgets.QFileSystemModel):
    """
    Mô hình hệ thống tệp tùy chỉnh cho cây thư mục
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_files = set()
        self.setReadOnly(True)
    
    def isSelected(self, index):
        """Kiểm tra xem file có được chọn không"""
        return self.filePath(index) in self._selected_files
    
    def setSelected(self, index, selected=True):
        """Đặt trạng thái chọn cho file"""
        file_path = self.filePath(index)
        if selected:
            self._selected_files.add(file_path)
        elif file_path in self._selected_files:
            self._selected_files.remove(file_path)
    
    def selectedFiles(self):
        """Trả về danh sách các file đã chọn"""
        return list(self._selected_files)
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self._selected_files.clear()

class FileTreeView(QtWidgets.QTreeView):
    """
    Widget hiển thị cây thư mục với khả năng chọn nhiều file
    """
    fileSelected = QtCore.pyqtSignal(str, bool)  # Tín hiệu khi file được chọn/bỏ chọn
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FileSystemModel(self)
        self.setModel(self.model)
        
        # Thiết lập các thuộc tính hiển thị
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAnimated(True)
        self.setSortingEnabled(True)
        
        # Ẩn các cột không cần thiết
        self.hideColumn(1)  # Cột kích thước
        self.hideColumn(2)  # Cột loại
        self.hideColumn(3)  # Cột ngày sửa đổi
        
        # Thiết lập xử lý click
        self.clicked.connect(self.onItemClicked)
    
    def setRootPath(self, path):
        """Thiết lập đường dẫn gốc cho cây thư mục"""
        index = self.model.setRootPath(path)
        self.setRootIndex(index)
        self.expandToDepth(0)  # Mở rộng thư mục gốc
    
    def onItemClicked(self, index):
        """Xử lý khi một mục được click"""
        # Chỉ cho phép chọn file, không phải thư mục
        if not self.model.isDir(index):
            file_path = self.model.filePath(index)
            is_selected = self.model.isSelected(index)
            
            # Đảo trạng thái chọn
            self.model.setSelected(index, not is_selected)
            
            # Phát tín hiệu file đã được chọn/bỏ chọn
            self.fileSelected.emit(file_path, not is_selected)
            
            # Vẽ lại item
            self.update(index)
    
    def getSelectedFiles(self):
        """Lấy danh sách các file đã chọn"""
        return self.model.selectedFiles()
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self.model.clearSelection()
        self.viewport().update()

class FileTreeDelegate(QtWidgets.QStyledItemDelegate):
    """
    Delegate tùy chỉnh để vẽ mục trong cây thư mục
    """
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Tùy chỉnh cách vẽ mục trong cây thư mục"""
        # Lấy mô hình từ index
        model = index.model()
        
        # Vẽ nền cho mục được chọn
        if model.isSelected(index):
            painter.fillRect(option.rect, QtGui.QColor(45, 45, 60))
        
        # Gọi phương thức vẽ mặc định
        super().paint(painter, option, index)
        
        # Nếu mục đã được chọn, vẽ biểu tượng tick
        if model.isSelected(index) and not model.isDir(index):
            check_rect = QtCore.QRect(option.rect)
            check_rect.setLeft(option.rect.right() - 20)
            
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor(137, 180, 250), 2))
            painter.drawLine(check_rect.left() + 4, check_rect.center().y(), 
                            check_rect.center().x(), check_rect.bottom() - 4)
            painter.drawLine(check_rect.center().x(), check_rect.bottom() - 4, 
                            check_rect.right() - 4, check_rect.top() + 4)
            painter.restore()
            
class FileAttachDialog(QtWidgets.QDialog):
    """
    Hộp thoại cho phép duyệt và chọn file để đính kèm
    """
    def __init__(self, parent=None, language="en", translations=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations or {}
        
        self.setWindowTitle(self.get_translation("file_dialog_title"))
        self.setMinimumSize(600, 400)
        
        # Khởi tạo UI
        self.init_ui()
        
        # Danh sách file đã chọn
        self.selected_files = []
        
    def get_translation(self, key):
        """Lấy bản dịch cho key dựa trên ngôn ngữ hiện tại"""
        lang_dict = self.translations.get(self.language, {})
        return lang_dict.get(key, key)
    
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Ô nhập đường dẫn và nút duyệt
        path_layout = QtWidgets.QHBoxLayout()
        
        self.path_input = QtWidgets.QLineEdit(self)
        self.path_input.setPlaceholderText(self.get_translation("path_placeholder"))
        
        self.browse_btn = QtWidgets.QPushButton(self.get_translation("browse_btn"), self)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        self.go_btn = QtWidgets.QPushButton(self.get_translation("go_btn"), self)
        self.go_btn.clicked.connect(self.navigate_to_path)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.go_btn)
        
        layout.addLayout(path_layout)
        
        # Cây thư mục
        self.file_tree = FileTreeView(self)
        self.file_tree.setItemDelegate(FileTreeDelegate(self))
        self.file_tree.fileSelected.connect(self.update_selected_files)
        
        # Thiết lập đường dẫn mặc định
        default_path = os.path.expanduser("~")
        self.file_tree.setRootPath(default_path)
        self.path_input.setText(default_path)
        
        layout.addWidget(self.file_tree)
        
        # Danh sách file đã chọn
        selected_group = QtWidgets.QGroupBox(self.get_translation("selected_files"))
        selected_layout = QtWidgets.QVBoxLayout()
        
        self.selected_list = QtWidgets.QListWidget(self)
        self.selected_list.setAlternatingRowColors(True)
        self.selected_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(self.show_selected_context_menu)
        
        selected_layout.addWidget(self.selected_list)
        selected_group.setLayout(selected_layout)
        
        layout.addWidget(selected_group)
        
        # Nút ở dưới cùng
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.clear_btn = QtWidgets.QPushButton(self.get_translation("clear_btn"), self)
        self.clear_btn.clicked.connect(self.clear_selection)
        
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QtWidgets.QPushButton(self.get_translation("cancel_btn"), self)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.attach_btn)
        
        layout.addLayout(buttons_layout)
        
        # Áp dụng stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
                background-color: #282a36;
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QTreeView, QListWidget {
                background-color: #282a36;
                alternate-background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                color: #cdd6f4;
                outline: none;
            }
            QTreeView::item:hover, QListWidget::item:hover {
                background-color: #313244;
            }
            QTreeView::item:selected, QListWidget::item:selected {
                background-color: #45475a;
            }
        """)
    
    def browse_folder(self):
        """Mở hộp thoại chọn thư mục"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            self.get_translation("select_folder"),
            self.path_input.text()
        )
        
        if folder:
            self.path_input.setText(folder)
            self.file_tree.setRootPath(folder)
    
    def navigate_to_path(self):
        """Di chuyển đến đường dẫn đã nhập"""
        path = self.path_input.text()
        if os.path.exists(path):
            self.file_tree.setRootPath(path)
        else:
            QtWidgets.QMessageBox.warning(
                self,
                self.get_translation("error"),
                self.get_translation("path_not_exist")
            )
    
    def update_selected_files(self, file_path, selected):
        """Cập nhật danh sách file đã chọn khi có thay đổi"""
        if selected:
            # Thêm file vào danh sách đã chọn
            self.selected_files.append(file_path)
            self.selected_list.addItem(os.path.basename(file_path))
        else:
            # Xóa file khỏi danh sách đã chọn
            if file_path in self.selected_files:
                index = self.selected_files.index(file_path)
                self.selected_files.pop(index)
                item = self.selected_list.takeItem(index)
                del item
    
    def show_selected_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho danh sách file đã chọn"""
        menu = QtWidgets.QMenu(self)
        remove_action = menu.addAction(self.get_translation("remove_file"))
        
        if not self.selected_list.count():
            return
            
        action = menu.exec_(self.selected_list.mapToGlobal(position))
        
        if action == remove_action:
            current_row = self.selected_list.currentRow()
            if current_row >= 0:
                # Xóa file khỏi danh sách và cập nhật mô hình
                file_path = self.selected_files[current_row]
                self.selected_files.pop(current_row)
                self.selected_list.takeItem(current_row)
                
                # Cập nhật trạng thái chọn trong cây thư mục
                for i in range(self.file_tree.model.rowCount()):
                    index = self.file_tree.model.index(i, 0, self.file_tree.rootIndex())
                    if self.file_tree.model.filePath(index) == file_path:
                        self.file_tree.model.setSelected(index, False)
                        self.file_tree.update(index)
                        break
    
    def clear_selection(self):
        """Xóa tất cả các lựa chọn"""
        self.selected_files.clear()
        self.selected_list.clear()
        self.file_tree.clearSelection()
    
    def get_selected_files(self):
        """Trả về danh sách các file đã chọn"""
        return self.selected_files

class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 500)  # Tăng kích thước cửa sổ
        
        # Đường dẫn file cấu hình
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        # Khởi tạo danh sách lưu đường dẫn file đính kèm
        self.attached_files = []
        
        # Thiết lập ngôn ngữ mặc định và tải cấu hình
        self.load_config()
        
        # Từ điển cho đa ngôn ngữ
        self.translations = {
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
                
                # Thuộc tính mới cho hộp thoại chọn file
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
                
                # Thuộc tính mới cho hộp thoại chọn file
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
        
        # Cập nhật tiêu đề cửa sổ theo ngôn ngữ đã chọn
        self.setWindowTitle(self.get_translation("window_title"))
        
        # Thiết lập stylesheet với giao diện hiện đại hơn
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                border-radius: 10px;
                border: 1px solid #313244;
            }
            QTextEdit {
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px;
                background-color: #282a36;
                color: #cdd6f4;
                font-size: 13px;
                selection-background-color: #7f849c;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton#closeBtn {
                background-color: #f38ba8;
            }
            QPushButton#closeBtn:hover {
                background-color: #f5c2e7;
            }
            QPushButton#attachBtn {
                background-color: #a6e3a1;
                color: #1e1e2e;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton#attachBtn:hover {
                background-color: #94e2d5;
            }
            QCheckBox {
                font-size: 13px;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLabel#titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #89b4fa;
            }
            QLabel#infoLabel {
                color: #a6adc8;
                font-style: italic;
                font-size: 12px;
            }
            QLabel#warningLabel {
                color: #f38ba8;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #6c7086;
                border-radius: 4px;
                background-color: #282a36;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #89b4fa;
                border-radius: 4px;
                background-color: #89b4fa;
                image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#1e1e2e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
            }
            QListWidget {
                background-color: #282a36;
                border: 1px solid #45475a;
                border-radius: 6px;
                color: #cdd6f4;
                padding: 5px;
            }
            QListWidget::item {
                border-radius: 3px;
                padding: 3px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #45475a;
            }
            QComboBox {
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 5px 10px;
                background-color: #282a36;
                color: #cdd6f4;
                min-width: 100px;
                selection-background-color: #45475a;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#cdd6f4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>');
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #45475a;
                background-color: #282a36;
                color: #cdd6f4;
                selection-background-color: #45475a;
                outline: none;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:on {
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }
            QComboBox::item {
                padding: 5px;
                min-height: 25px;
            }
            QComboBox::item:selected {
                background-color: #45475a;
                border: none;
            }
        """)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Thêm chọn ngôn ngữ
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
        
        # Thêm tiêu đề
        self.title_label = QtWidgets.QLabel(self.get_translation("title_label"), self)
        self.title_label.setObjectName("titleLabel")
        self.layout.addWidget(self.title_label)
        
        # Thêm hướng dẫn
        self.info_label = QtWidgets.QLabel(self.get_translation("info_label"), self)
        self.info_label.setObjectName("infoLabel")
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)
        
        # Thay thế QLineEdit bằng QTextEdit
        self.input = QtWidgets.QTextEdit(self)
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
        self.input.setMinimumHeight(200)  # Tăng chiều cao của ô input
        self.layout.addWidget(self.input)
        
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
        self.file_list.setMaximumHeight(80)
        self.file_list.setVisible(False)
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.file_list)
        
        # Thêm checkbox tiếp tục trò chuyện
        self.continue_checkbox = QtWidgets.QCheckBox(self.get_translation("continue_checkbox"), self)
        self.continue_checkbox.setChecked(True)
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
        self.setLayout(self.layout)
        
        # Thiết lập focus cho input khi mở dialog
        self.input.setFocus()
        
        # Thiết lập drop shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        self.result_text = None
        self.result_continue = False
        self.result_ready = False
    
    def load_config(self):
        """
        Tải cấu hình từ file config.json nếu tồn tại
        """
        self.current_language = "en"  # Mặc định là tiếng Anh
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'language' in config:
                        self.current_language = config['language']
        except Exception as e:
            print(f"Lỗi khi tải cấu hình: {str(e)}", file=sys.stderr)
    
    def save_config(self):
        """
        Lưu cấu hình vào file config.json
        """
        try:
            config = {'language': self.current_language}
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {str(e)}", file=sys.stderr)
    
    def get_translation(self, key):
        """
        Lấy bản dịch cho khóa ngôn ngữ dựa trên ngôn ngữ hiện tại
        """
        return self.translations.get(self.current_language, {}).get(key, key)
    
    def change_language(self, index):
        """
        Thay đổi ngôn ngữ hiện tại và cập nhật giao diện
        """
        self.current_language = self.language_combo.itemData(index)
        
        # Lưu cấu hình khi thay đổi ngôn ngữ
        self.save_config()
        
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
                # Kiểm tra xem file có tồn tại không
                if os.path.exists(file_path):
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
                        self.get_translation("error_file_not_exists_message")
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
                "language": self.current_language  # Thêm thông tin ngôn ngữ hiện tại
            }
            
            # Thêm thông tin về file đính kèm nếu có
            if self.attached_files:
                result_dict["attached_files"] = []
                for file_info in self.attached_files:
                    try:
                        file_path = file_info["path"]
                        file_name = file_info["name"]
                        
                        # Đọc nội dung file
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_content = f.read()
                        
                        # Thêm thông tin file vào kết quả
                        result_dict["attached_files"].append({
                            "path": file_path,
                            "name": file_name,
                            "content": file_content
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

def run_ui(*args, **kwargs):
    """
    Hàm chính để chạy giao diện người dùng và trả về kết quả.
    """
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Thiết lập font mặc định cho toàn ứng dụng
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)
    
    text, continue_chat, ok = InputDialog.getText()
    
    # Chuẩn bị chuỗi metadata
    metadata_str = f"[AI_INTERACTION_TOOL] METADATA: {{'continue_chat': {str(continue_chat).lower()}}}"
    
    # Không in metadata ra stderr nữa
    # print(metadata_str, file=sys.stderr)

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
                
                # In thông báo đến stderr để debug (có thể giữ lại nếu cần thiết cho việc khác)
                # print("[AI_INTERACTION_TOOL] Đã xử lý các file đính kèm", file=sys.stderr)
            
            # Log về trạng thái continue_chat có thể vẫn hữu ích cho debug phía agent, nên giữ lại
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
        full_response_text = f"{metadata_str}\n\n{metadata_str}" # Trả về metadata với text rỗng ở giữa
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

class FileSystemModel(QtWidgets.QFileSystemModel):
    """
    Mô hình hệ thống tệp tùy chỉnh cho cây thư mục
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_files = set()
        self.setReadOnly(True)
    
    def isSelected(self, index):
        """Kiểm tra xem file có được chọn không"""
        return self.filePath(index) in self._selected_files
    
    def setSelected(self, index, selected=True):
        """Đặt trạng thái chọn cho file"""
        file_path = self.filePath(index)
        if selected:
            self._selected_files.add(file_path)
        elif file_path in self._selected_files:
            self._selected_files.remove(file_path)
    
    def selectedFiles(self):
        """Trả về danh sách các file đã chọn"""
        return list(self._selected_files)
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self._selected_files.clear()

class FileTreeView(QtWidgets.QTreeView):
    """
    Widget hiển thị cây thư mục với khả năng chọn nhiều file
    """
    fileSelected = QtCore.pyqtSignal(str, bool)  # Tín hiệu khi file được chọn/bỏ chọn
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FileSystemModel(self)
        self.setModel(self.model)
        
        # Thiết lập các thuộc tính hiển thị
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAnimated(True)
        self.setSortingEnabled(True)
        
        # Ẩn các cột không cần thiết
        self.hideColumn(1)  # Cột kích thước
        self.hideColumn(2)  # Cột loại
        self.hideColumn(3)  # Cột ngày sửa đổi
        
        # Thiết lập xử lý click
        self.clicked.connect(self.onItemClicked)
    
    def setRootPath(self, path):
        """Thiết lập đường dẫn gốc cho cây thư mục"""
        index = self.model.setRootPath(path)
        self.setRootIndex(index)
        self.expandToDepth(0)  # Mở rộng thư mục gốc
    
    def onItemClicked(self, index):
        """Xử lý khi một mục được click"""
        # Chỉ cho phép chọn file, không phải thư mục
        if not self.model.isDir(index):
            file_path = self.model.filePath(index)
            is_selected = self.model.isSelected(index)
            
            # Đảo trạng thái chọn
            self.model.setSelected(index, not is_selected)
            
            # Phát tín hiệu file đã được chọn/bỏ chọn
            self.fileSelected.emit(file_path, not is_selected)
            
            # Vẽ lại item
            self.update(index)
    
    def getSelectedFiles(self):
        """Lấy danh sách các file đã chọn"""
        return self.model.selectedFiles()
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self.model.clearSelection()
        self.viewport().update()

class FileTreeDelegate(QtWidgets.QStyledItemDelegate):
    """
    Delegate tùy chỉnh để vẽ mục trong cây thư mục
    """
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Tùy chỉnh cách vẽ mục trong cây thư mục"""
        # Lấy mô hình từ index
        model = index.model()
        
        # Vẽ nền cho mục được chọn
        if model.isSelected(index):
            painter.fillRect(option.rect, QtGui.QColor(45, 45, 60))
        
        # Gọi phương thức vẽ mặc định
        super().paint(painter, option, index)
        
        # Nếu mục đã được chọn, vẽ biểu tượng tick
        if model.isSelected(index) and not model.isDir(index):
            check_rect = QtCore.QRect(option.rect)
            check_rect.setLeft(option.rect.right() - 20)
            
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor(137, 180, 250), 2))
            painter.drawLine(check_rect.left() + 4, check_rect.center().y(), 
                            check_rect.center().x(), check_rect.bottom() - 4)
            painter.drawLine(check_rect.center().x(), check_rect.bottom() - 4, 
                            check_rect.right() - 4, check_rect.top() + 4)
            painter.restore()
            
class FileAttachDialog(QtWidgets.QDialog):
    """
    Hộp thoại cho phép duyệt và chọn file để đính kèm
    """
    def __init__(self, parent=None, language="en", translations=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations or {}
        
        self.setWindowTitle(self.get_translation("file_dialog_title"))
        self.setMinimumSize(600, 400)
        
        # Khởi tạo UI
        self.init_ui()
        
        # Danh sách file đã chọn
        self.selected_files = []
        
    def get_translation(self, key):
        """Lấy bản dịch cho key dựa trên ngôn ngữ hiện tại"""
        lang_dict = self.translations.get(self.language, {})
        return lang_dict.get(key, key)
    
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Ô nhập đường dẫn và nút duyệt
        path_layout = QtWidgets.QHBoxLayout()
        
        self.path_input = QtWidgets.QLineEdit(self)
        self.path_input.setPlaceholderText(self.get_translation("path_placeholder"))
        
        self.browse_btn = QtWidgets.QPushButton(self.get_translation("browse_btn"), self)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        self.go_btn = QtWidgets.QPushButton(self.get_translation("go_btn"), self)
        self.go_btn.clicked.connect(self.navigate_to_path)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.go_btn)
        
        layout.addLayout(path_layout)
        
        # Cây thư mục
        self.file_tree = FileTreeView(self)
        self.file_tree.setItemDelegate(FileTreeDelegate(self))
        self.file_tree.fileSelected.connect(self.update_selected_files)
        
        # Thiết lập đường dẫn mặc định
        default_path = os.path.expanduser("~")
        self.file_tree.setRootPath(default_path)
        self.path_input.setText(default_path)
        
        layout.addWidget(self.file_tree)
        
        # Danh sách file đã chọn
        selected_group = QtWidgets.QGroupBox(self.get_translation("selected_files"))
        selected_layout = QtWidgets.QVBoxLayout()
        
        self.selected_list = QtWidgets.QListWidget(self)
        self.selected_list.setAlternatingRowColors(True)
        self.selected_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(self.show_selected_context_menu)
        
        selected_layout.addWidget(self.selected_list)
        selected_group.setLayout(selected_layout)
        
        layout.addWidget(selected_group)
        
        # Nút ở dưới cùng
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.clear_btn = QtWidgets.QPushButton(self.get_translation("clear_btn"), self)
        self.clear_btn.clicked.connect(self.clear_selection)
        
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QtWidgets.QPushButton(self.get_translation("cancel_btn"), self)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.attach_btn)
        
        layout.addLayout(buttons_layout)
        
        # Áp dụng stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
                background-color: #282a36;
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QTreeView, QListWidget {
                background-color: #282a36;
                alternate-background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                color: #cdd6f4;
                outline: none;
            }
            QTreeView::item:hover, QListWidget::item:hover {
                background-color: #313244;
            }
            QTreeView::item:selected, QListWidget::item:selected {
                background-color: #45475a;
            }
        """)
    
    def browse_folder(self):
        """Mở hộp thoại chọn thư mục"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            self.get_translation("select_folder"),
            self.path_input.text()
        )
        
        if folder:
            self.path_input.setText(folder)
            self.file_tree.setRootPath(folder)
    
    def navigate_to_path(self):
        """Di chuyển đến đường dẫn đã nhập"""
        path = self.path_input.text()
        if os.path.exists(path):
            self.file_tree.setRootPath(path)
        else:
            QtWidgets.QMessageBox.warning(
                self,
                self.get_translation("error"),
                self.get_translation("path_not_exist")
            )
    
    def update_selected_files(self, file_path, selected):
        """Cập nhật danh sách file đã chọn khi có thay đổi"""
        if selected:
            # Thêm file vào danh sách đã chọn
            self.selected_files.append(file_path)
            self.selected_list.addItem(os.path.basename(file_path))
        else:
            # Xóa file khỏi danh sách đã chọn
            if file_path in self.selected_files:
                index = self.selected_files.index(file_path)
                self.selected_files.pop(index)
                item = self.selected_list.takeItem(index)
                del item
    
    def show_selected_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho danh sách file đã chọn"""
        menu = QtWidgets.QMenu(self)
        remove_action = menu.addAction(self.get_translation("remove_file"))
        
        if not self.selected_list.count():
            return
            
        action = menu.exec_(self.selected_list.mapToGlobal(position))
        
        if action == remove_action:
            current_row = self.selected_list.currentRow()
            if current_row >= 0:
                # Xóa file khỏi danh sách và cập nhật mô hình
                file_path = self.selected_files[current_row]
                self.selected_files.pop(current_row)
                self.selected_list.takeItem(current_row)
                
                # Cập nhật trạng thái chọn trong cây thư mục
                for i in range(self.file_tree.model.rowCount()):
                    index = self.file_tree.model.index(i, 0, self.file_tree.rootIndex())
                    if self.file_tree.model.filePath(index) == file_path:
                        self.file_tree.model.setSelected(index, False)
                        self.file_tree.update(index)
                        break
    
    def clear_selection(self):
        """Xóa tất cả các lựa chọn"""
        self.selected_files.clear()
        self.selected_list.clear()
        self.file_tree.clearSelection()
    
    def get_selected_files(self):
        """Trả về danh sách các file đã chọn"""
        return self.selected_files

