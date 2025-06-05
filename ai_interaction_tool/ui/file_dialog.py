# File attachment dialog for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore
import os
from .file_tree import FileTreeView, FileTreeDelegate
from .styles import get_file_dialog_stylesheet
from ..utils.translations import get_translation
from ..constants import DEFAULT_PATH
from ..utils.file_utils import (
    validate_workspace_path, 
    validate_file_path_in_workspace,
    create_relative_path_with_workspace,
    normalize_path_unicode
)

class FileAttachDialog(QtWidgets.QDialog):
    """
    Hộp thoại cho phép duyệt và chọn file/folder để đính kèm với workspace support
    """
    def __init__(self, parent=None, language="en", translations=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations or {}
        
        self.setWindowTitle(self._get_translation("file_dialog_title"))
        self.setMinimumSize(700, 500)
        
        # Workspace root path
        self.workspace_path = ""
        
        # Khởi tạo UI
        self.init_ui()
        
        # Danh sách file/folder đã chọn (relative paths)
        self.selected_items = []
        
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
        
        # Workspace selection section
        workspace_group = QtWidgets.QGroupBox("Workspace Configuration")
        workspace_layout = QtWidgets.QVBoxLayout()
        
        # Workspace path display and selection
        workspace_path_layout = QtWidgets.QHBoxLayout()
        self.workspace_label = QtWidgets.QLabel("No workspace selected")
        self.workspace_label.setStyleSheet("QLabel { color: #f38ba8; font-weight: bold; }")
        
        self.select_workspace_btn = QtWidgets.QPushButton("Browse", self)
        self.select_workspace_btn.clicked.connect(self.select_workspace)
        
        workspace_path_layout.addWidget(QtWidgets.QLabel("Workspace:"))
        workspace_path_layout.addWidget(self.workspace_label, 1)
        workspace_path_layout.addWidget(self.select_workspace_btn)
        
        # Workspace path input (for pasting/typing path directly)
        workspace_input_layout = QtWidgets.QHBoxLayout()
        
        self.workspace_input = QtWidgets.QLineEdit(self)
        self.workspace_input.setPlaceholderText("Paste or type workspace path here...")
        self.workspace_input.setToolTip("Bạn có thể paste đường dẫn workspace vào đây thay vì browse\nTip: Nhấn Enter để set workspace")
        self.workspace_input.returnPressed.connect(self.set_workspace_from_input)
        
        self.set_workspace_btn = QtWidgets.QPushButton("Set Workspace", self)
        self.set_workspace_btn.clicked.connect(self.set_workspace_from_input)
        self.set_workspace_btn.setToolTip("Sử dụng đường dẫn đã nhập làm workspace")
        
        workspace_input_layout.addWidget(QtWidgets.QLabel("Or paste path:"))
        workspace_input_layout.addWidget(self.workspace_input, 1)
        workspace_input_layout.addWidget(self.set_workspace_btn)
        
        workspace_layout.addLayout(workspace_path_layout)
        workspace_layout.addLayout(workspace_input_layout)
        workspace_group.setLayout(workspace_layout)
        layout.addWidget(workspace_group)
        
        # File/Folder selection options
        options_layout = QtWidgets.QHBoxLayout()
        

        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        # Ô nhập đường dẫn và nút duyệt
        path_layout = QtWidgets.QHBoxLayout()
        
        self.path_input = QtWidgets.QLineEdit(self)
        self.path_input.setPlaceholderText("Enter path to folder")
        
        self.browse_btn = QtWidgets.QPushButton("Browse", self)
        self.browse_btn.clicked.connect(self.browse_folder)
        
        self.go_btn = QtWidgets.QPushButton("Go", self)
        self.go_btn.clicked.connect(self.navigate_to_path)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.go_btn)
        
        layout.addLayout(path_layout)
        
        # Cây thư mục
        self.file_tree = FileTreeView(self)
        self.file_tree.setItemDelegate(FileTreeDelegate(self))
        self.file_tree.itemSelected.connect(self.update_selected_items)
        
        # Thiết lập đường dẫn mặc định
        default_path = DEFAULT_PATH
        self.file_tree.setRootPath(default_path)
        self.path_input.setText(default_path)
        
        layout.addWidget(self.file_tree)
        
        # Danh sách items đã chọn
        selected_group = QtWidgets.QGroupBox("Selected Items (Relative to Workspace)")
        selected_layout = QtWidgets.QVBoxLayout()
        
        # Clear Selected button
        clear_selected_layout = QtWidgets.QHBoxLayout()
        self.clear_selected_btn = QtWidgets.QPushButton("Clear Selected", self)
        self.clear_selected_btn.clicked.connect(self.clear_selected_items)
        self.clear_selected_btn.setEnabled(False)  # Always visible, disabled by default  # Ẩn ban đầu
        
        clear_selected_layout.addWidget(self.clear_selected_btn)
        clear_selected_layout.addStretch()
        selected_layout.addLayout(clear_selected_layout)
        
        self.selected_list = QtWidgets.QListWidget(self)
        self.selected_list.setAlternatingRowColors(True)
        self.selected_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # Multi-select
        self.selected_list.setToolTip("Tip: Hold Ctrl+Click to select multiple items, Shift+Click for range selection")
        self.selected_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(self.show_selected_context_menu)
        self.selected_list.itemSelectionChanged.connect(self.update_selected_button_state)
        
        selected_layout.addWidget(self.selected_list)
        selected_group.setLayout(selected_layout)
        
        layout.addWidget(selected_group)
        
        # Nút ở dưới cùng
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.clear_btn = QtWidgets.QPushButton("Clear All", self)
        self.clear_btn.clicked.connect(self.clear_selection)
        
        self.attach_btn = QtWidgets.QPushButton("Attach Selected", self)
        self.attach_btn.clicked.connect(self.accept)
        self.attach_btn.setEnabled(False)  # Disabled until workspace is selected
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.attach_btn)
        
        layout.addLayout(buttons_layout)
        
        # Áp dụng stylesheet
        self.setStyleSheet(get_file_dialog_stylesheet())
    
    def select_workspace(self):
        """Chọn workspace root directory"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            "Select Workspace Root Directory",
            self.workspace_path or DEFAULT_PATH
        )
        
        if folder:
            validation_result = validate_workspace_path(folder)
            
            if not validation_result["valid"]:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Invalid Workspace",
                    f"Cannot use selected workspace:\n{validation_result['error']}"
                )
                return
            
            self.clear_selection()
            
            self.workspace_path = validation_result["normalized_path"]
            workspace_name = os.path.basename(self.workspace_path)
            
            self.workspace_label.setText(workspace_name)
            self.workspace_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
            self.workspace_label.setToolTip(f"Full path: {self.workspace_path}")
            self.attach_btn.setEnabled(True)
            
            self.file_tree.setRootPath(self.workspace_path)
            self.path_input.setText(self.workspace_path)
            
            # Update workspace input field với current workspace
            self.workspace_input.setText(self.workspace_path)
    
    def set_workspace_from_input(self):
        """Set workspace từ đường dẫn đã nhập/paste"""
        input_path = self.workspace_input.text().strip()
        
        if not input_path:
            QtWidgets.QMessageBox.warning(
                self,
                "Empty Path",
                "Please enter or paste a workspace path first!"
            )
            return
        
        # Normalize path
        try:
            normalized_path = normalize_path_unicode(input_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid Path",
                f"Invalid path format:\n{str(e)}"
            )
            return
        
        # Validate workspace
        validation_result = validate_workspace_path(normalized_path)
        
        if not validation_result["valid"]:
            QtWidgets.QMessageBox.critical(
                self,
                "Invalid Workspace",
                f"Cannot use this path as workspace:\n{validation_result['error']}\n\nPath: {normalized_path}"
            )
            return
        
        # Clear existing selections
        self.clear_selection()
        
        # Set workspace
        self.workspace_path = validation_result["normalized_path"]
        workspace_name = os.path.basename(self.workspace_path)
        
        self.workspace_label.setText(workspace_name)
        self.workspace_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
        self.workspace_label.setToolTip(f"Full path: {self.workspace_path}")
        self.attach_btn.setEnabled(True)
        
        self.file_tree.setRootPath(self.workspace_path)
        self.path_input.setText(self.workspace_path)
        
        # Update workspace input với final normalized path
        self.workspace_input.setText(self.workspace_path)
        
        # Success feedback
        QtWidgets.QMessageBox.information(
            self,
            "Workspace Set",
            f"Workspace successfully set to:\n{workspace_name}\n\nFull path: {self.workspace_path}"
        )

    def browse_folder(self):
        """Mở hộp thoại chọn thư mục"""
        start_path = self.workspace_path if self.workspace_path else self.path_input.text()
        
        if start_path and not os.path.exists(start_path):
            start_path = DEFAULT_PATH
        
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            "Select Folder",
            start_path
        )
        
        if folder:
            normalized_folder = normalize_path_unicode(folder)
            
            if os.path.exists(normalized_folder) and os.path.isdir(normalized_folder):
                self.path_input.setText(normalized_folder)
                self.file_tree.setRootPath(normalized_folder)
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Folder",
                    f"Selected folder is not accessible: {folder}"
                )
    
    def navigate_to_path(self):
        """Di chuyển đến đường dẫn đã nhập"""
        path = self.path_input.text().strip()
        
        if not path:
            QtWidgets.QMessageBox.warning(
                self,
                "Empty Path",
                "Please enter a path first!"
            )
            return
        
        normalized_path = normalize_path_unicode(path)
        
        if not os.path.exists(normalized_path):
            QtWidgets.QMessageBox.warning(
                self,
                "Path Not Found",
                f"The specified path does not exist:\n{normalized_path}"
            )
            return
        
        if not os.path.isdir(normalized_path):
            QtWidgets.QMessageBox.warning(
                self,
                "Not a Directory",
                f"The specified path is not a directory:\n{normalized_path}"
            )
            return
        
        if not os.access(normalized_path, os.R_OK):
            QtWidgets.QMessageBox.warning(
                self,
                "Access Denied",
                f"Cannot access the specified directory:\n{normalized_path}"
            )
            return
        
        try:
            self.file_tree.setRootPath(normalized_path)
            self.path_input.setText(normalized_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Navigation Error",
                f"Error navigating to path:\n{str(e)}"
            )
    
    def update_selected_items(self, item_path, selected):
        """Cập nhật danh sách items đã chọn"""
        if not self.workspace_path:
            QtWidgets.QMessageBox.warning(
                self,
                "No Workspace Selected",
                "Please select a workspace directory first!"
            )
            return
        
        try:
            validation_result = validate_file_path_in_workspace(item_path, self.workspace_path)
            
            if not validation_result["valid"]:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    f"Cannot select this item:\n{validation_result['error']}"
                )
                return
            
            full_relative_path, error = create_relative_path_with_workspace(
                item_path, self.workspace_path
            )
            
            if error:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Path Error",
                    f"Error creating relative path:\n{error}"
                )
                return
            
            if selected:
                if full_relative_path not in self.selected_items:
                    self.selected_items.append(full_relative_path)
                    
                    item_type = "FOLDER" if validation_result["is_dir"] else "FILE"
                    
                    if validation_result["is_symlink"]:
                        item_type += " (SYMLINK)"
                    
                    basename = validation_result["basename"]
                    display_name = f"[{item_type}] {basename}"
                    
                    if len(full_relative_path) > 60:
                        short_path = "..." + full_relative_path[-57:]
                        display_name += f" ({short_path})"
                    else:
                        display_name += f" ({full_relative_path})"
                    
                    list_item = QtWidgets.QListWidgetItem(display_name)
                    list_item.setToolTip(f"Full relative path: {full_relative_path}\nTip: Hold Ctrl+Click to select multiple items")
                    self.selected_list.addItem(list_item)
            else:
                if full_relative_path in self.selected_items:
                    index = self.selected_items.index(full_relative_path)
                    self.selected_items.pop(index)
                    item = self.selected_list.takeItem(index)
                    if item:
                        del item
                        
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred:\n{str(e)}\n\nPlease try again or select a different item."
            )
    
    def _is_safe_path(self, path):
        """Kiểm tra xem path có an toàn không (deprecated - sử dụng utils functions)"""
        # Chuyển sang sử dụng function từ utils
        from ..utils.file_utils import contains_dangerous_patterns
        return not contains_dangerous_patterns(path)
    
    def show_selected_context_menu(self, position):
        """Hiển thị menu ngữ cảnh cho danh sách items đã chọn"""
        if not self.selected_list.count():
            return
            
        menu = QtWidgets.QMenu(self)
        remove_action = menu.addAction("Remove Item")
        remove_all_action = menu.addAction("Remove All Items")
        
        action = menu.exec_(self.selected_list.mapToGlobal(position))
        
        if action == remove_action:
            current_row = self.selected_list.currentRow()
            if current_row >= 0 and current_row < len(self.selected_items):
                try:
                    relative_path = self.selected_items[current_row]
                    self.selected_items.pop(current_row)
                    list_item = self.selected_list.takeItem(current_row)
                    if list_item:
                        del list_item
                    
                    workspace_name = os.path.basename(self.workspace_path)
                    if relative_path.startswith(f"{workspace_name}/"):
                        path_without_workspace = relative_path[len(workspace_name)+1:]
                        full_path = os.path.join(self.workspace_path, path_without_workspace.replace('/', os.sep))
                        normalized_full_path = normalize_path_unicode(full_path)
                        self.file_tree.deselectItem(normalized_full_path)
                        
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Remove Error", 
                        f"Error removing item: {str(e)}"
                    )
        
        elif action == remove_all_action:
            self.clear_selection()
    
    def update_selected_button_state(self):
        """Cập nhật trạng thái Clear Selected button"""
        selected_items = self.selected_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.clear_selected_btn.setEnabled(has_selection)
        if has_selection:
            self.clear_selected_btn.setText(f"Clear Selected ({len(selected_items)})")
            self.clear_selected_btn.setToolTip("Xóa các items đã chọn trong list")
        else:
            self.clear_selected_btn.setText("Clear Selected")
            self.clear_selected_btn.setToolTip("Chọn items trong list để xóa")
    
    def clear_selected_items(self):
        """Xóa các items đã chọn trong list"""
        selected_items = self.selected_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                "No Selection", 
                "Please select items to remove first.\nTip: Hold Ctrl+Click to select multiple items."
            )
            return
        
        # Get rows to remove và corresponding relative paths
        rows_to_remove = []
        relative_paths_to_remove = []
        
        for item in selected_items:
            row = self.selected_list.row(item)
            if row < len(self.selected_items):
                rows_to_remove.append(row)
                relative_paths_to_remove.append(self.selected_items[row])
        
        # Sort descending để xóa từ cuối
        rows_to_remove.sort(reverse=True)
        
        # Remove from UI list
        for row in rows_to_remove:
            self.selected_list.takeItem(row)
            if row < len(self.selected_items):
                self.selected_items.pop(row)
        
        # Deselect in tree view
        for relative_path in relative_paths_to_remove:
            workspace_name = os.path.basename(self.workspace_path)
            if relative_path.startswith(f"{workspace_name}/"):
                path_without_workspace = relative_path[len(workspace_name)+1:]
                full_path = os.path.join(self.workspace_path, path_without_workspace.replace('/', os.sep))
                normalized_full_path = normalize_path_unicode(full_path)
                
                # Tìm index và deselect trực tiếp
                index = self.file_tree.model.index(normalized_full_path)
                if index.isValid():
                    self.file_tree.model.setSelected(index, False)
        
        # Force repaint tree view
        self.file_tree.viewport().update()
        self.file_tree.repaint()
        
        # Update button state
        self.update_selected_button_state()
    
    def clear_selection(self):
        """Xóa tất cả các lựa chọn"""
        try:
            self.selected_items.clear()
            self.selected_list.clear()
            self.file_tree.clearSelection()
            self.update_selected_button_state()
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Clear Error",
                f"Error clearing selections: {str(e)}"
            )
    
    def get_selected_files(self):
        """Trả về danh sách các items đã chọn"""
        validated_items = []
        
        for relative_path in self.selected_items:
            try:
                workspace_name = os.path.basename(self.workspace_path)
                if relative_path.startswith(f"{workspace_name}/"):
                    path_without_workspace = relative_path[len(workspace_name)+1:]
                    full_path = os.path.join(self.workspace_path, path_without_workspace.replace('/', os.sep))
                    
                    if os.path.exists(full_path) and os.access(full_path, os.R_OK):
                        validated_items.append(relative_path)
                else:
                    validated_items.append(relative_path)
                    
            except Exception:
                continue
        
        return validated_items
    
    def get_workspace_path(self):
        """Trả về tên workspace gốc"""
        if not self.workspace_path:
            return ""
        
        workspace_name = os.path.basename(self.workspace_path)
        return workspace_name
    
    def get_full_workspace_path(self):
        """Trả về full path của workspace"""
        return self.workspace_path
    
    def restore_workspace_state(self, workspace_path, current_attached_files):
        """Khôi phục workspace state và highlight các items đã select"""
        if not workspace_path or not os.path.exists(workspace_path):
            return
        
        # Set workspace
        validation_result = validate_workspace_path(workspace_path)
        if validation_result["valid"]:
            self.workspace_path = validation_result["normalized_path"]
            workspace_name = os.path.basename(self.workspace_path)
            
            self.workspace_label.setText(workspace_name)
            self.workspace_label.setStyleSheet("QLabel { color: #a6e3a1; font-weight: bold; }")
            self.workspace_label.setToolTip(f"Full path: {self.workspace_path}")
            self.attach_btn.setEnabled(True)
            
            self.file_tree.setRootPath(self.workspace_path)
            self.path_input.setText(self.workspace_path)
            
            # Khôi phục selected items
            for item_info in current_attached_files:
                try:
                    relative_path = item_info["relative_path"]
                    if relative_path not in self.selected_items:
                        self.selected_items.append(relative_path)
                        
                        # Thêm vào UI list
                        item_type = item_info.get("type", "unknown").upper()
                        basename = item_info.get("name", "unknown")
                        display_name = f"[{item_type}] {basename}"
                        
                        if len(relative_path) > 60:
                            short_path = "..." + relative_path[-57:]
                            display_name += f" ({short_path})"
                        else:
                            display_name += f" ({relative_path})"
                        
                        list_item = QtWidgets.QListWidgetItem(display_name)
                        list_item.setToolTip(f"Full relative path: {relative_path}\nTip: Hold Ctrl+Click to select multiple items")
                        self.selected_list.addItem(list_item)
                        
                        # Highlight trong tree nếu tìm thấy
                        workspace_name_prefix = f"{workspace_name}/"
                        if relative_path.startswith(workspace_name_prefix):
                            path_without_workspace = relative_path[len(workspace_name_prefix):]
                            full_path = os.path.join(self.workspace_path, path_without_workspace.replace('/', os.sep))
                            self._highlight_item_in_tree(full_path)
                            
                except Exception:
                    continue
            
            # Update button state after restore
            self.update_selected_button_state()
    
    def _highlight_item_in_tree(self, full_path):
        """Highlight một item trong tree view"""
        try:
            normalized_path = normalize_path_unicode(full_path)
            if os.path.exists(normalized_path):
                # Tìm index của item trong model
                index = self.file_tree.model.index(normalized_path)
                if index.isValid():
                    self.file_tree.model.setSelected(index, True)
                    self.file_tree.refreshView()
        except Exception:
            pass 