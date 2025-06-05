# File tree components for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from ..constants import TREE_DEPTH_EXPANSION
from ..utils.file_utils import normalize_path_unicode, validate_file_path_in_workspace

class FileSystemModel(QtWidgets.QFileSystemModel):
    """Mô hình hệ thống tệp tùy chỉnh cho cây thư mục"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_items = set()
        self._workspace_path = ""
        self.setReadOnly(True)
        self.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.AllEntries | QtCore.QDir.NoDotAndDotDot)
    
    def setWorkspacePath(self, workspace_path):
        """Thiết lập workspace path"""
        self._workspace_path = normalize_path_unicode(workspace_path) if workspace_path else ""
    
    def isSelected(self, index):
        """Kiểm tra xem item có được chọn không"""
        if not index.isValid():
            return False
        
        item_path = normalize_path_unicode(self.filePath(index))
        return item_path in self._selected_items
    
    def setSelected(self, index, selected=True):
        """Đặt trạng thái chọn cho item"""
        if not index.isValid():
            return False
        
        item_path = normalize_path_unicode(self.filePath(index))
        
        if selected:
            self._selected_items.add(item_path)
        elif item_path in self._selected_items:
            self._selected_items.remove(item_path)
        
        return True
    
    def selectedItems(self):
        """Trả về danh sách các item đã chọn"""
        valid_items = []
        items_to_remove = []
        
        for item_path in self._selected_items:
            try:
                if os.path.exists(item_path):
                    valid_items.append(item_path)
                else:
                    items_to_remove.append(item_path)
            except Exception:
                items_to_remove.append(item_path)
        
        for item_path in items_to_remove:
            self._selected_items.discard(item_path)
        
        return valid_items
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        self._selected_items.clear()
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Override data để hiển thị thông tin file"""
        if role == QtCore.Qt.DisplayRole:
            original_name = super().data(index, role)
            if original_name:
                normalized_name = normalize_path_unicode(str(original_name))
                return normalized_name
        
        return super().data(index, role)

class FileTreeView(QtWidgets.QTreeView):
    """Widget hiển thị cây thư mục với khả năng chọn nhiều file và folder"""
    itemSelected = QtCore.pyqtSignal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FileSystemModel(self)
        self.setModel(self.model)
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setAnimated(True)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(False)  # Tắt để tránh conflict với custom highlight
        
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        
        self._workspace_path = ""
        
        self.clicked.connect(self.onItemClicked)
        
        header = self.header()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(200)
    
    def setRootPath(self, path):
        """Thiết lập đường dẫn gốc cho cây thư mục"""
        if not path:
            return False
        
        try:
            normalized_path = normalize_path_unicode(path)
            
            if not os.path.exists(normalized_path):
                return False
            
            if not os.path.isdir(normalized_path):
                return False
            
            if not os.access(normalized_path, os.R_OK):
                return False
            
            self._workspace_path = normalized_path
            self.model.setWorkspacePath(normalized_path)
            
            index = self.model.setRootPath(normalized_path)
            self.setRootIndex(index)
            
            try:
                self.expandToDepth(min(TREE_DEPTH_EXPANSION, 2))
            except Exception:
                pass
            
            return True
            
        except Exception:
            return False
    

    
    def onItemClicked(self, index):
        """Xử lý khi một mục được click"""
        try:
            if not index.isValid():
                return
            
            item_path = normalize_path_unicode(self.model.filePath(index))
            is_dir = self.model.isDir(index)
            

            
            is_selected = self.model.isSelected(index)
            
            if self.model.setSelected(index, not is_selected):
                self.itemSelected.emit(item_path, not is_selected)
                # Force refresh toàn bộ view để đảm bảo highlight hiển thị đúng
                self.refreshView()
            
        except Exception as e:
            print(f"Error in onItemClicked: {str(e)}")
    
    def getSelectedItems(self):
        """Lấy danh sách các item đã chọn"""
        return self.model.selectedItems()
    
    def clearSelection(self):
        """Xóa tất cả các lựa chọn"""
        try:
            self.model.clearSelection()
            self.viewport().update()
        except Exception as e:
            print(f"Error clearing selection: {str(e)}")
    
    def refreshView(self):
        """Force refresh toàn bộ tree view"""
        try:
            self.viewport().update()
            self.repaint()
        except Exception as e:
            print(f"Error refreshing view: {str(e)}")
    
    def deselectItem(self, item_path):
        """Bỏ chọn một item cụ thể"""
        try:
            if not item_path:
                return
            
            normalized_path = normalize_path_unicode(item_path)
            root_index = self.rootIndex()
            
            if self._deselectItemAtLevel(root_index, normalized_path):
                return
            
            self._deselectItemRecursive(root_index, normalized_path)
            
        except Exception as e:
            print(f"Error deselecting item: {str(e)}")
    
    def _deselectItemAtLevel(self, parent_index, item_path):
        """Tìm và bỏ chọn item ở một level cụ thể"""
        try:
            for i in range(self.model.rowCount(parent_index)):
                index = self.model.index(i, 0, parent_index)
                if not index.isValid():
                    continue
                
                current_path = normalize_path_unicode(self.model.filePath(index))
                if current_path == item_path:
                    self.model.setSelected(index, False)
                    self.viewport().update()
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _deselectItemRecursive(self, parent_index, item_path, max_depth=10):
        """Tìm và bỏ chọn item một cách đệ quy"""
        if max_depth <= 0:
            return False
        
        try:
            for i in range(self.model.rowCount(parent_index)):
                index = self.model.index(i, 0, parent_index)
                if not index.isValid():
                    continue
                
                current_path = normalize_path_unicode(self.model.filePath(index))
                if current_path == item_path:
                    self.model.setSelected(index, False)
                    self.viewport().update()
                    return True
                
                if self.model.isDir(index) and self.model.hasChildren(index):
                    if not self.isExpanded(index):
                        self.expand(index)
                    
                    if self._deselectItemRecursive(index, item_path, max_depth - 1):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def keyPressEvent(self, event):
        """Override key press để xử lý an toàn"""
        try:
            if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_F2]:
                return
            
            super().keyPressEvent(event)
            
        except Exception:
            pass

class FileTreeDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate tùy chỉnh để vẽ mục trong cây thư mục"""
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Tùy chỉnh cách vẽ mục trong cây thư mục"""
        try:
            if not index.isValid():
                super().paint(painter, option, index)
                return
            
            model = index.model()
            is_selected = hasattr(model, 'isSelected') and model.isSelected(index)
            
            # Vẽ alternating background trước (chỉ khi không selected)
            if not is_selected and index.row() % 2 == 1:
                alt_color = QtGui.QColor(240, 240, 245, 30)  # Rất nhạt
                painter.fillRect(option.rect, alt_color)
            
            # Vẽ highlight background nếu selected (ưu tiên cao hơn)
            if is_selected:
                highlight_color = QtGui.QColor(45, 45, 60, 200)  # Tăng opacity để rõ hơn
                painter.fillRect(option.rect, highlight_color)
            
            # Vẽ nội dung item
            super().paint(painter, option, index)
            
            # Vẽ checkmark sau cùng để đảm bảo nó hiển thị trên top
            if is_selected:
                self._drawCheckMark(painter, option.rect)
                
        except Exception as e:
            try:
                super().paint(painter, option, index)
            except Exception:
                pass
    
    def _drawCheckMark(self, painter, rect):
        """Vẽ dấu tick"""
        try:
            check_rect = QtCore.QRect(rect)
            check_rect.setLeft(rect.right() - 20)
            
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor(137, 180, 250), 2))
            
            painter.drawLine(
                check_rect.left() + 4, check_rect.center().y(), 
                check_rect.center().x(), check_rect.bottom() - 4
            )
            painter.drawLine(
                check_rect.center().x(), check_rect.bottom() - 4, 
                check_rect.right() - 4, check_rect.top() + 4
            )
            
            painter.restore()
            
        except Exception:
            pass
    
    def sizeHint(self, option, index):
        """Override size hint"""
        try:
            size = super().sizeHint(option, index)
            size.setHeight(max(size.height(), 20))
            return size
        except Exception:
            return QtCore.QSize(200, 20) 