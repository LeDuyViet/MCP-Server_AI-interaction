# File attachment dialog for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore
import os
from .file_tree import FileTreeView, FileTreeDelegate
from .styles import get_file_dialog_stylesheet
from ..utils.translations import get_translation
from ..constants import DEFAULT_PATH

class FileAttachDialog(QtWidgets.QDialog):
    """
    Hộp thoại cho phép duyệt và chọn file để đính kèm
    """
    def __init__(self, parent=None, language="en", translations=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations or {}
        
        self.setWindowTitle(self._get_translation("file_dialog_title"))
        self.setMinimumSize(600, 400)
        
        # Khởi tạo UI
        self.init_ui()
        
        # Danh sách file đã chọn
        self.selected_files = []
        
    def _get_translation(self, key):
        """Lấy bản dịch cho key dựa trên ngôn ngữ hiện tại"""
        if self.translations:
            lang_dict = self.translations.get(self.language, {})
            return lang_dict.get(key, key)
        else:
            return get_translation(self.language, key)
    
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Ô nhập đường dẫn và nút duyệt
        path_layout = QtWidgets.QHBoxLayout()
        
        self.path_input = QtWidgets.QLineEdit(self)
        self.path_input.setPlaceholderText(self._get_translation("path_placeholder"))
        
        self.browse_btn = QtWidgets.QPushButton(self._get_translation("browse_btn"), self)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        self.go_btn = QtWidgets.QPushButton(self._get_translation("go_btn"), self)
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
        default_path = DEFAULT_PATH
        self.file_tree.setRootPath(default_path)
        self.path_input.setText(default_path)
        
        layout.addWidget(self.file_tree)
        
        # Danh sách file đã chọn
        selected_group = QtWidgets.QGroupBox(self._get_translation("selected_files"))
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
        
        self.clear_btn = QtWidgets.QPushButton(self._get_translation("clear_btn"), self)
        self.clear_btn.clicked.connect(self.clear_selection)
        
        self.attach_btn = QtWidgets.QPushButton(self._get_translation("attach_btn"), self)
        self.attach_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QtWidgets.QPushButton(self._get_translation("cancel_btn"), self)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.attach_btn)
        
        layout.addLayout(buttons_layout)
        
        # Áp dụng stylesheet
        self.setStyleSheet(get_file_dialog_stylesheet())
    
    def browse_folder(self):
        """Mở hộp thoại chọn thư mục"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            self._get_translation("select_folder"),
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
                self._get_translation("error"),
                self._get_translation("path_not_exist")
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
        remove_action = menu.addAction(self._get_translation("remove_file"))
        
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