# File tree components for AI Interaction Tool
from PyQt5 import QtWidgets, QtCore, QtGui
import os
from ..constants import TREE_DEPTH_EXPANSION

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
        if os.path.exists(path):
            index = self.model.setRootPath(path)
            self.setRootIndex(index)
            self.expandToDepth(TREE_DEPTH_EXPANSION)  # Mở rộng thư mục gốc
            return True
        return False
    
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
        if hasattr(model, 'isSelected') and model.isSelected(index):
            painter.fillRect(option.rect, QtGui.QColor(45, 45, 60))
        
        # Gọi phương thức vẽ mặc định
        super().paint(painter, option, index)
        
        # Nếu mục đã được chọn, vẽ biểu tượng tick
        if (hasattr(model, 'isSelected') and model.isSelected(index) and 
            hasattr(model, 'isDir') and not model.isDir(index)):
            
            check_rect = QtCore.QRect(option.rect)
            check_rect.setLeft(option.rect.right() - 20)
            
            painter.save()
            painter.setPen(QtGui.QPen(QtGui.QColor(137, 180, 250), 2))
            painter.drawLine(check_rect.left() + 4, check_rect.center().y(), 
                            check_rect.center().x(), check_rect.bottom() - 4)
            painter.drawLine(check_rect.center().x(), check_rect.bottom() - 4, 
                            check_rect.right() - 4, check_rect.top() + 4)
            painter.restore() 