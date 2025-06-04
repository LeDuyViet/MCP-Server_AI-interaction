# Stylesheets for AI Interaction Tool UI components

def get_main_stylesheet():
    """
    Trả về stylesheet chính cho InputDialog
    """
    return """
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
    """

def get_file_dialog_stylesheet():
    """
    Trả về stylesheet cho FileAttachDialog
    """
    return """
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
    """ 