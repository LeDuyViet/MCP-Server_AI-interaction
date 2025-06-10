# Main input dialog for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json
import os
from .config import ConfigManager
from ..ui.file_dialog import FileAttachDialog
from ..ui.styles import get_main_stylesheet, get_context_menu_stylesheet
from ..utils.translations import get_translations, get_translation
from ..utils.file_utils import read_file_content, validate_file_path
from ..constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, MIN_INPUT_HEIGHT, MAX_FILE_LIST_HEIGHT,
    SHADOW_BLUR_RADIUS, SHADOW_OFFSET, SHADOW_OPACITY
)

class InputDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # Khởi tạo config manager
        self.config_manager = ConfigManager()
        
        # Set responsive sizing instead of fixed
        self.setMinimumSize(800, 700)  # Much larger minimum size for comfortable UX
        
        # Load saved window size or use default
        saved_width, saved_height = self.config_manager.get_window_size()
        self.resize(saved_width, saved_height)
        
        # Khởi tạo danh sách lưu đường dẫn file đính kèm
        self.attached_files = []
        
        # Lưu workspace state để reuse - load từ config
        last_workspace = self.config_manager.get_last_workspace()
        if last_workspace and os.path.exists(last_workspace):
            self.current_workspace_path = last_workspace
            self.current_workspace_name = self.config_manager.get_last_workspace_name()
            # Load attached files từ config
            saved_files = self.config_manager.get_last_attached_files()
            if saved_files:
                self.attached_files = saved_files
        else:
            # Clear invalid workspace từ config
            self.current_workspace_path = None
            self.current_workspace_name = None
            if last_workspace:  # Có workspace path nhưng không tồn tại
                self.config_manager.set_last_workspace(None)
        
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
        
        # Restore attached files UI nếu có
        self._restore_attached_files_ui()
        
        # Force refresh button styles để apply semantic colors
        self._refresh_button_styles()
        
        self.result_text = None
        self.result_continue = False
        self.result_ready = False
        
        # Setup resize timer for saving window size
        self.resize_timer = QtCore.QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_window_size)
        self.resize_timer.setInterval(500)  # Save 500ms after last resize
    
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
        """Thiết lập thông tin hướng dẫn"""
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
        self.input.setMinimumHeight(200)  # Larger minimum for big window
        self.input.setMaximumHeight(400)  # Allow more text editing space
        self.layout.addWidget(self.input)
    
    def _setup_file_attachment(self):
        """Thiết lập khu vực đính kèm file"""
        # Row 1: Attach button và label
        attach_layout = QtWidgets.QHBoxLayout()
        
        self.attach_btn = QtWidgets.QPushButton(self.get_translation("attach_btn"), self)
        self.attach_btn.setObjectName("attachBtn")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.attach_btn.setProperty("button-type", "info")
        
        self.attached_files_label = QtWidgets.QLabel(self.get_translation("attached_files_label"), self)
        self.attached_files_label.setVisible(False)
        
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addWidget(self.attached_files_label)
        attach_layout.addStretch()
        
        self.layout.addLayout(attach_layout)
        
        # Row 2: Clear buttons (chỉ hiện khi có files)
        clear_layout = QtWidgets.QHBoxLayout()
        
        self.clear_selected_btn = QtWidgets.QPushButton(self.get_translation("clear_selected"), self)
        self.clear_selected_btn.setObjectName("clearSelectedBtn")
        self.clear_selected_btn.clicked.connect(self.clear_selected_files)
        self.clear_selected_btn.setEnabled(False)  # Always visible, but disabled by default
        self.clear_selected_btn.setToolTip(self.get_translation("clear_selected_tooltip"))
        self.clear_selected_btn.setProperty("button-type", "warning")
        
        self.clear_all_btn = QtWidgets.QPushButton(self.get_translation("clear_all"), self)
        self.clear_all_btn.setObjectName("clearAllBtn")
        self.clear_all_btn.clicked.connect(self.clear_all_files)
        self.clear_all_btn.setEnabled(False)  # Always visible, but disabled by default
        self.clear_all_btn.setToolTip(self.get_translation("clear_all_tooltip"))
        self.clear_all_btn.setProperty("button-type", "danger")
        
        clear_layout.addWidget(self.clear_selected_btn)
        clear_layout.addWidget(self.clear_all_btn)
        clear_layout.addStretch()
        
        self.layout.addLayout(clear_layout)
        
        # Danh sách file đính kèm - enable multi-select
        self.file_list = QtWidgets.QListWidget(self)
        self.file_list.setMaximumHeight(300)  # Much more space for files in large window
        self.file_list.setMinimumHeight(120)  # Larger minimum when visible
        self.file_list.setVisible(False)
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # Multi-select
        self.file_list.setToolTip(self.get_translation("file_list_tooltip"))
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemSelectionChanged.connect(self.update_clear_buttons_state)
        self.layout.addWidget(self.file_list)
    
    def _setup_continue_options(self):
        """Thiết lập các tùy chọn tiếp tục cuộc trò chuyện"""
        # Thêm checkbox tiếp tục trò chuyện
        continue_default = self.config_manager.get('ui_preferences.continue_chat_default', True)
        self.continue_checkbox = QtWidgets.QCheckBox(self.get_translation("continue_checkbox"), self)
        self.continue_checkbox.setChecked(continue_default)
        self.continue_checkbox.setToolTip("Khi chọn, Agent sẽ tự động hiển thị lại hộp thoại này sau khi trả lời")
        self.layout.addWidget(self.continue_checkbox)
        
        # ============= THINKING LOGIC COMPLETELY REMOVED =============
        # Agent uses thinking blocks naturally - no UI controls needed
        # Simplified interface for maximum usability
        
        # Thêm checkbox Maximum Reasoning
        max_reasoning_default = self.config_manager.get('ui_preferences.max_reasoning_default', False)
        self.max_reasoning_checkbox = QtWidgets.QCheckBox(self.get_translation("max_reasoning_checkbox"), self)
        self.max_reasoning_checkbox.setChecked(max_reasoning_default)
        self.max_reasoning_checkbox.setToolTip(self.get_translation("max_reasoning_tooltip"))
        self.layout.addWidget(self.max_reasoning_checkbox)
        
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
        self.submit_btn.setProperty("button-type", "success")
        
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
    
    def _restore_attached_files_ui(self):
        """Restore UI cho attached files từ config"""
        if not self.attached_files:
            return
        
        # Clear list trước
        self.file_list.clear()
        
        # Rebuild UI từ attached files
        for item_info in self.attached_files:
            relative_path = item_info.get("relative_path", "")
            item_type = item_info.get("type", "unknown").upper()
            
            display_name = f"[{item_type}] {relative_path}"
            list_item = QtWidgets.QListWidgetItem(display_name)
            list_item.setToolTip(f"Full relative path: {relative_path}\nTip: Hold Ctrl+Click to select multiple items")
            self.file_list.addItem(list_item)
        
        # Hiển thị UI elements
        if self.attached_files:
            self.attached_files_label.setVisible(True)
            self.file_list.setVisible(True)
        
        # Update button states regardless
        self.update_clear_buttons_state()
    
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
        self.info_label.setText(self.get_translation("info_label"))
        self.language_label.setText(self.get_translation("language_label"))
        self.attached_files_label.setText(self.get_translation("attached_files_label"))
        self.continue_checkbox.setText(self.get_translation("continue_checkbox"))
        # No thinking UI to update
        self.max_reasoning_checkbox.setText(self.get_translation("max_reasoning_checkbox"))
        self.max_reasoning_checkbox.setToolTip(self.get_translation("max_reasoning_tooltip"))
        self.warning_label.setText(self.get_translation("warning_label"))
        
        # Cập nhật các nút
        self.attach_btn.setText(self.get_translation("attach_btn"))
        self.submit_btn.setText(self.get_translation("submit_btn"))
        self.close_btn.setText(self.get_translation("close_btn"))
        self.clear_selected_btn.setText(self.get_translation("clear_selected"))
        self.clear_all_btn.setText(self.get_translation("clear_all"))
        
        # Cập nhật tooltips
        self.clear_selected_btn.setToolTip(self.get_translation("clear_selected_tooltip"))
        self.clear_all_btn.setToolTip(self.get_translation("clear_all_tooltip"))
        self.file_list.setToolTip(self.get_translation("file_list_tooltip"))
        
        # Refresh tooltips cho tất cả items trong file list
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item and len(self.attached_files) > i:
                relative_path = self.attached_files[i]["relative_path"]
                item.setToolTip(self.get_translation("file_item_tooltip").format(path=relative_path))
        
        # Cập nhật placeholder
        self.input.setPlaceholderText(self.get_translation("input_placeholder"))
    
    def attach_file(self):
        """
        Mở hộp thoại chọn file/folder và thêm file được chọn vào danh sách đính kèm
        """
        # Sử dụng hộp thoại chọn file nâng cao với workspace support
        dialog = FileAttachDialog(self, self.current_language, self.translations)
        
        # Khôi phục workspace state nếu có
        if self.current_workspace_path:
            dialog.restore_workspace_state(self.current_workspace_path, self.attached_files)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_items = dialog.get_selected_files()
            workspace_name = dialog.get_workspace_path()
            
            # Lưu workspace state để lần sau sử dụng
            self.current_workspace_path = dialog.get_full_workspace_path()
            self.current_workspace_name = workspace_name
            
            # Persist workspace state vào config
            self.config_manager.set_last_workspace(self.current_workspace_path)
            self.config_manager.set_last_attached_files(self.attached_files)
            
            if not workspace_name:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "No Workspace Selected", 
                    "Please select a workspace directory!"
                )
                return

            # Sync lại toàn bộ attached_files từ dialog
            self._sync_attached_files_from_dialog(selected_items, workspace_name)
            
            # Save attached files state ngay sau khi sync từ dialog
            self.config_manager.set_last_attached_files(self.attached_files)
    
    def _sync_attached_files_from_dialog(self, selected_items, workspace_name):
        """Sync toàn bộ attached_files từ dialog về main UI"""
        # Clear UI hiện tại
        self.file_list.clear()
        self.attached_files.clear()
        
        # Rebuild từ selected_items trong dialog
        for relative_path in selected_items:
            item_name = os.path.basename(relative_path)
            item_type = self._determine_item_type(item_name, relative_path)
            
            item_info = {
                "relative_path": relative_path,
                "workspace_name": workspace_name,
                "name": item_name,
                "type": item_type
            }
            self.attached_files.append(item_info)
            
            display_name = f"[{item_type.upper()}] {relative_path}"
            list_item = QtWidgets.QListWidgetItem(display_name)
            list_item.setToolTip(self.get_translation("file_item_tooltip").format(path=relative_path))
            self.file_list.addItem(list_item)
        
        # Hiển thị/ẩn danh sách file theo số lượng items
        if self.attached_files:
            self.attached_files_label.setVisible(True)
            self.file_list.setVisible(True)
        else:
            self.attached_files_label.setVisible(False)
            self.file_list.setVisible(False)
        
        # Always update button states (they're always visible now)
        self.update_clear_buttons_state()
    
    def update_clear_buttons_state(self):
        """Cập nhật trạng thái các nút clear dựa trên selection"""
        selected_items = self.file_list.selectedItems()
        has_selection = len(selected_items) > 0
        has_files = len(self.attached_files) > 0
        
        # Update Clear Selected button
        self.clear_selected_btn.setEnabled(has_selection)
        if has_selection:
            self.clear_selected_btn.setText(f"{self.get_translation('clear_selected')} ({len(selected_items)})")
            self.clear_selected_btn.setToolTip("Xóa các items đã chọn")
        else:
            self.clear_selected_btn.setText(self.get_translation("clear_selected"))
            self.clear_selected_btn.setToolTip("Chọn items để xóa")
        
        # Update Clear All button
        self.clear_all_btn.setEnabled(has_files)
        if has_files:
            self.clear_all_btn.setText(f"{self.get_translation('clear_all')} ({len(self.attached_files)})")
            self.clear_all_btn.setToolTip("Xóa tất cả items đã đính kèm")
        else:
            self.clear_all_btn.setText(self.get_translation("clear_all"))
            self.clear_all_btn.setToolTip("Không có items để xóa")
    
    def clear_selected_files(self):
        """Xóa các files đã chọn"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.information(
                self,
                self.get_translation("no_selection"), 
                self.get_translation("no_selection_message")
            )
            return
        
        # Xóa từ cuối để tránh thay đổi index
        rows_to_remove = []
        for item in selected_items:
            row = self.file_list.row(item)
            rows_to_remove.append(row)
        
        # Sort descending để xóa từ cuối
        rows_to_remove.sort(reverse=True)
        
        for row in rows_to_remove:
            self.file_list.takeItem(row)
            if row < len(self.attached_files):
                self.attached_files.pop(row)
        
        # Cập nhật trạng thái UI sau khi xóa
        self.update_clear_buttons_state()
        
        # Save state sau khi thay đổi
        self.config_manager.set_last_attached_files(self.attached_files)
        
        # Ẩn danh sách nếu không còn items
        if not self.attached_files:
            self.attached_files_label.setVisible(False)
            self.file_list.setVisible(False)
        
        # Update button states
        self.update_clear_buttons_state()
    
    def clear_all_files(self):
        """Xóa tất cả files đã đính kèm"""
        if not self.attached_files:
            return
            
        reply = QtWidgets.QMessageBox.question(
            self,
            self.get_translation("clear_all_files"),
            self.get_translation("clear_all_confirm").format(count=len(self.attached_files)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.file_list.clear()
            self.attached_files.clear()
            
            # Save state
            self.config_manager.set_last_attached_files(self.attached_files)
            
            # Hide UI elements that should be hidden
            self.attached_files_label.setVisible(False)
            self.file_list.setVisible(False)
            
            # Update button states
            self.update_clear_buttons_state()
    
    def _determine_item_type(self, item_name, relative_path):
        """
        Xác định loại item (file hoặc folder) dựa trên tên và đường dẫn
        """
        # Danh sách các file đặc biệt không có extension nhưng vẫn là file
        known_files_without_ext = {
            'dockerfile', 'makefile', 'readme', 'license', 'changelog',
            'authors', 'contributors', 'copying', 'install', 'news',
            'procfile', 'rakefile', 'gemfile', 'vagrantfile'
        }
        
        # Tên file thường (lowercase để so sánh)
        lower_name = item_name.lower()
        
        # 1. Kiểm tra hidden files/folders (bắt đầu bằng dấu chấm)
        if item_name.startswith('.'):
            # Hidden files thường có extension (như .gitignore, .env)
            # Hidden folders thường không có (như .git, .vscode)
            if '.' in item_name[1:]:  # Có dấu chấm sau dấu chấm đầu
                return "file"
            else:
                return "folder"
        
        # 2. Kiểm tra các file đặc biệt không có extension
        if lower_name in known_files_without_ext:
            return "file"
        
        # 3. Kiểm tra có extension không
        if '.' in item_name and not item_name.endswith('.'):
            # Có extension -> likely file
            return "file"
        
        # 4. Kiểm tra pattern của folder common
        folder_patterns = [
            'src', 'lib', 'bin', 'test', 'tests', 'docs', 'doc',
            'build', 'dist', 'node_modules', 'vendor', 'assets',
            'static', 'public', 'components', 'utils', 'helpers',
            'config', 'configs', 'scripts', 'tools'
        ]
        
        if lower_name in folder_patterns:
            return "folder"
        
        # 5. Kiểm tra path depth - thường folder có nhiều level hơn
        path_parts = relative_path.split('/')
        if len(path_parts) > 2:  # workspace/folder/...
            # Nếu là item cuối cùng và không có extension -> có thể là folder
            if not ('.' in item_name and not item_name.endswith('.')):
                return "folder"
        
        # 6. Default: nếu không có extension thì coi là folder
        return "folder" if '.' not in item_name or item_name.endswith('.') else "file"
    
    def show_context_menu(self, position):
        """
        Hiển thị menu ngữ cảnh cho danh sách file đính kèm
        """
        menu = QtWidgets.QMenu()
        
        # Apply modern context menu styling
        menu.setStyleSheet(get_context_menu_stylesheet())
        
        remove_action = menu.addAction(self.get_translation("remove_file"))
        remove_all_action = menu.addAction(self.get_translation("clear_all"))
        
        current_item = self.file_list.itemAt(position)
        if current_item:
            action = menu.exec_(self.file_list.mapToGlobal(position))
            if action == remove_action:
                row = self.file_list.row(current_item)
                self.file_list.takeItem(row)
                self.attached_files.pop(row)
                
                # Save state sau khi remove
                self.config_manager.set_last_attached_files(self.attached_files)
                
                # Ẩn danh sách nếu không còn file đính kèm
                if self.file_list.count() == 0:
                    self.attached_files_label.setVisible(False)
                    self.file_list.setVisible(False)
                
                # Update button states
                self.update_clear_buttons_state()
            
            elif action == remove_all_action:
                self.clear_all_files()

    def submit_text(self):
        """
        Phương thức xử lý khi người dùng nhấn nút Gửi.
        """
        text = self.input.toPlainText()
        if text.strip() or self.attached_files:
            result_dict = {
                "text": text,
                "language": self.current_language,
                # ====== THINKING LOGIC REMOVED - Natural Behavior ======
                "max_reasoning": self.max_reasoning_checkbox.isChecked()
            }
            
            # Thêm thông tin về file/folder đính kèm nếu có (chỉ metadata, không đọc content)
            if self.attached_files:
                result_dict["attached_files"] = []
                for item_info in self.attached_files:
                    try:
                        relative_path = item_info["relative_path"]
                        workspace_name = item_info["workspace_name"]
                        name = item_info["name"]
                        item_type = item_info["type"]
                        
                        # Chỉ thêm metadata, không đọc file content
                        result_dict["attached_files"].append({
                            "relative_path": relative_path,
                            "workspace_name": workspace_name,
                            "name": name,
                            "type": item_type
                        })
                    except Exception as e:
                        result_dict["attached_files"].append({
                            "relative_path": item_info.get("relative_path", "unknown"),
                            "workspace_name": item_info.get("workspace_name", ""),
                            "name": item_info.get("name", "unknown"),
                            "type": item_info.get("type", "unknown"),
                            "error": str(e)
                        })
            
            self.result_text = json.dumps(result_dict, ensure_ascii=False)
            self.result_continue = self.continue_checkbox.isChecked()
            self.result_ready = True
            
            # Lưu trạng thái checkbox vào config để lần sau sử dụng
            self.config_manager.set('ui_preferences.continue_chat_default', self.continue_checkbox.isChecked())
            # No thinking level to save - always "high" mode
            self.config_manager.set('ui_preferences.max_reasoning_default', self.max_reasoning_checkbox.isChecked())
            self.config_manager.save_config()
            
            self.input.clear()
            self.accept()
    
    # Cho phép gửi bằng phím Enter
    def resizeEvent(self, event):
        """Handle window resize events và save size với debounce"""
        super().resizeEvent(event)
        # Restart timer mỗi lần resize (debounce effect)
        self.resize_timer.start()
    
    def save_window_size(self):
        """Save current window size to config"""
        self.config_manager.set_window_size(self.width(), self.height())
    
    def closeEvent(self, event):
        """Save window size khi đóng dialog"""
        self.save_window_size()
        super().closeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.submit_text()
        else:
            super().keyPressEvent(event)

    def _refresh_button_styles(self):
        """Force refresh button styles để apply semantic colors"""
        buttons_to_refresh = [
            self.submit_btn,
            self.attach_btn,
            self.clear_selected_btn,
            self.clear_all_btn,
            # Note: close_btn uses ID-based styling, không cần property refresh
        ]
        
        for button in buttons_to_refresh:
            # Force style refresh by unpolish then polish
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    @staticmethod
    def getText():
        dialog = InputDialog()
        result = dialog.exec_()
        if dialog.result_ready:
            return dialog.result_text, dialog.result_continue, True
        else:
            return "", False, False 