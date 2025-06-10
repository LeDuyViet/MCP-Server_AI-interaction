# Modern styling for AI Interaction Tool UI components
from PyQt5 import QtGui, QtCore
import base64

class ModernTheme:
    """Modern dark theme based on Catppuccin Mocha with enhancements"""
    
    # Base colors (Catppuccin Mocha inspired)
    COLORS = {
        # Background colors
        'background': QtGui.QColor(24, 24, 37),         # #181825 - Main background
        'surface0': QtGui.QColor(49, 50, 68),           # #313244 - Secondary background
        'surface1': QtGui.QColor(69, 71, 90),           # #45475a - Tertiary background
        'surface2': QtGui.QColor(88, 91, 112),          # #585b70 - Card background
        
        # Interactive colors
        'hover': QtGui.QColor(49, 50, 68),              # #313244 - Hover state
        'selected': QtGui.QColor(137, 180, 250, 40),    # rgba(137, 180, 250, 0.15) - Selection
        'selected_border': QtGui.QColor(137, 180, 250), # #89b4fa - Selection border
        'pressed': QtGui.QColor(137, 180, 250, 60),     # rgba(137, 180, 250, 0.23) - Pressed state
        
        # Text colors
        'text': QtGui.QColor(205, 214, 244),            # #cdd6f4 - Primary text
        'text_secondary': QtGui.QColor(166, 173, 200),  # #a6adc8 - Secondary text
        'text_disabled': QtGui.QColor(108, 112, 134),   # #6c7086 - Disabled text
        
        # Accent colors
        'accent_blue': QtGui.QColor(137, 180, 250),     # #89b4fa - Primary accent
        'accent_green': QtGui.QColor(166, 227, 161),    # #a6e3a1 - Success/files
        'accent_yellow': QtGui.QColor(249, 226, 175),   # #f9e2af - Folders/warning
        'accent_red': QtGui.QColor(243, 139, 168),      # #f38ba8 - Error/danger
        'accent_pink': QtGui.QColor(245, 194, 231),     # #f5c2e7 - Special
        'accent_mauve': QtGui.QColor(203, 166, 247),    # #cba6f7 - Purple accent
        
        # Semantic colors
        'success': QtGui.QColor(166, 227, 161),         # #a6e3a1
        'warning': QtGui.QColor(249, 226, 175),         # #f9e2af
        'error': QtGui.QColor(243, 139, 168),           # #f38ba8
        'info': QtGui.QColor(137, 180, 250),            # #89b4fa
    }
    
    # Typography
    FONTS = {
        'default_size': 13,
        'small_size': 11,
        'large_size': 15,
        'icon_size': 16,
        'family': 'Segoe UI, Arial, sans-serif',
    }
    
    # Spacing and dimensions
    SPACING = {
        'small': 4,
        'medium': 8,
        'large': 12,
        'xlarge': 16,
        'border_radius': 6,
        'item_height': 28,
        'icon_size': 20,
        'checkmark_size': 18,
    }
    
    @classmethod
    def get_tree_view_stylesheet(cls):
        """Get stylesheet for QTreeView with modern dark theme"""
        return f"""
        QTreeView {{
            background-color: {cls.COLORS['surface0'].name()};
            border: 1px solid {cls.COLORS['surface1'].name()};
            border-radius: {cls.SPACING['border_radius']}px;
            outline: none;
            color: {cls.COLORS['text'].name()};
            font-family: {cls.FONTS['family']};
            font-size: {cls.FONTS['default_size']}px;
            selection-background-color: transparent;
        }}
        
        QTreeView::item {{
            height: {cls.SPACING['item_height']}px;
            padding: {cls.SPACING['small']}px;
            border: none;
            margin: 1px 4px;
            border-radius: {cls.SPACING['border_radius']}px;
        }}
        
        QTreeView::item:hover {{
            background-color: {cls.COLORS['hover'].name()};
        }}
        
        QTreeView::item:selected {{
            background-color: transparent;
        }}
        
        QTreeView::branch {{
            background: transparent;
            width: 16px;
        }}
        

        
        QScrollBar:vertical {{
            background-color: {cls.COLORS['surface0'].name()};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['surface2'].name()};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['text_secondary'].name()};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['surface0'].name()};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['surface2'].name()};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['text_secondary'].name()};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        """
    
    @classmethod
    def _get_chevron_right_svg(cls):
        """Get base64 encoded chevron right SVG"""
        svg = f"""<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 4L10 8L6 12" stroke="{cls.COLORS['text'].name()}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
        return base64.b64encode(svg.encode()).decode()
    
    @classmethod 
    def _get_chevron_down_svg(cls):
        """Get base64 encoded chevron down SVG"""
        svg = f"""<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 6L8 10L12 6" stroke="{cls.COLORS['text'].name()}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>"""
        return base64.b64encode(svg.encode()).decode()

class FileTypeIcons:
    """Modern file type icons using Unicode with better categorization"""
    
    ICONS = {
        # Folders
        'folder_closed': '📁',
        'folder_open': '📂',
        
        # Programming languages
        'python': '🐍',
        'javascript': '🟨', 
        'typescript': '🔷',
        'html': '🌐',
        'css': '🎨',
        'json': '📋',
        'xml': '📄',
        'yaml': '📄',
        'cpp': '⚙️',
        'java': '☕',
        'csharp': '🔷',
        'go': '🐹',
        'rust': '🦀',
        'php': '🐘',
        'ruby': '💎',
        'swift': '🕊️',
        'kotlin': '📱',
        
        # Data and config
        'database': '🗃️',
        'config': '⚙️',
        'env': '🔐',
        'dockerfile': '🐳',
        'makefile': '🔨',
        
        # Documents
        'text': '📄',
        'markdown': '📝',
        'pdf': '📕',
        'word': '📘',
        'excel': '📊',
        'powerpoint': '📰',
        
        # Media
        'image': '🖼️',
        'video': '🎬',
        'audio': '🎵',
        'font': '🔤',
        
        # Archives
        'archive': '📦',
        'zip': '🗜️',
        
        # Default
        'file': '📄',
        'unknown': '❓',
    }
    
    # File extension mappings
    EXTENSION_MAP = {
        # Programming
        'py': 'python',
        'js': 'javascript', 
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'html': 'html',
        'htm': 'html',
        'css': 'css',
        'scss': 'css',
        'sass': 'css',
        'less': 'css',
        'json': 'json',
        'xml': 'xml',
        'yml': 'yaml',
        'yaml': 'yaml',
        'cpp': 'cpp',
        'c': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'h': 'cpp',
        'hpp': 'cpp',
        'java': 'java',
        'cs': 'csharp',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'rb': 'ruby',
        'swift': 'swift',
        'kt': 'kotlin',
        
        # Data
        'sql': 'database',
        'db': 'database',
        'sqlite': 'database',
        'conf': 'config',
        'config': 'config',
        'ini': 'config',
        'toml': 'config',
        'env': 'env',
        'dockerfile': 'dockerfile',
        'makefile': 'makefile',
        
        # Documents
        'txt': 'text',
        'md': 'markdown',
        'markdown': 'markdown',
        'rst': 'markdown',
        'pdf': 'pdf',
        'doc': 'word',
        'docx': 'word',
        'xls': 'excel',
        'xlsx': 'excel',
        'ppt': 'powerpoint',
        'pptx': 'powerpoint',
        
        # Media
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'svg': 'image',
        'bmp': 'image',
        'webp': 'image',
        'ico': 'image',
        'mp4': 'video',
        'avi': 'video',
        'mkv': 'video',
        'mov': 'video',
        'wmv': 'video',
        'webm': 'video',
        'mp3': 'audio',
        'wav': 'audio',
        'flac': 'audio',
        'aac': 'audio',
        'm4a': 'audio',
        'ogg': 'audio',
        'ttf': 'font',
        'otf': 'font',
        'woff': 'font',
        'woff2': 'font',
        
        # Archives
        'zip': 'zip',
        'rar': 'archive',
        '7z': 'archive',
        'tar': 'archive',
        'gz': 'archive',
        'bz2': 'archive',
        'xz': 'archive',
    }
    
    @classmethod
    def get_icon(cls, filename, is_directory=False):
        """Get appropriate icon for file or directory"""
        if is_directory:
            return cls.ICONS['folder_closed']
        
        if not filename or '.' not in filename:
            return cls.ICONS['file']
        
        extension = filename.lower().split('.')[-1]
        icon_type = cls.EXTENSION_MAP.get(extension, 'file')
        return cls.ICONS.get(icon_type, cls.ICONS['file'])

# Legacy functions for backward compatibility
def get_main_stylesheet():
    """Main stylesheet for dialog"""
    return f"""
    QDialog {{
        background-color: {ModernTheme.COLORS['background'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        font-family: {ModernTheme.FONTS['family']};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QLabel {{
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        background: transparent;
    }}
    
    QLineEdit {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        padding: {ModernTheme.SPACING['medium']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {ModernTheme.COLORS['accent_blue'].name()};
    }}
    

    
    /* Default button styling */
    QPushButton {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        color: {ModernTheme.COLORS['background'].name()};
        border: none;
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        padding: {ModernTheme.SPACING['medium']}px {ModernTheme.SPACING['large']}px;
        font-size: {ModernTheme.FONTS['default_size']}px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {ModernTheme.COLORS['accent_blue'].lighter(110).name()};
    }}
    
    QPushButton:pressed {{
        background-color: {ModernTheme.COLORS['accent_blue'].darker(110).name()};
    }}
    
    QPushButton:disabled {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text_disabled'].name()};
    }}
    
    /* Semantic button variants - HIGH PRIORITY */
    QPushButton[button-type="success"] {{
        background-color: {ModernTheme.COLORS['success'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="success"]:hover {{
        background-color: {ModernTheme.COLORS['success'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="success"]:pressed {{
        background-color: {ModernTheme.COLORS['success'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="warning"] {{
        background-color: {ModernTheme.COLORS['warning'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="warning"]:hover {{
        background-color: {ModernTheme.COLORS['warning'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="warning"]:pressed {{
        background-color: {ModernTheme.COLORS['warning'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="danger"] {{
        background-color: {ModernTheme.COLORS['error'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="danger"]:hover {{
        background-color: {ModernTheme.COLORS['error'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="danger"]:pressed {{
        background-color: {ModernTheme.COLORS['error'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="info"] {{
        background-color: {ModernTheme.COLORS['info'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="info"]:hover {{
        background-color: {ModernTheme.COLORS['info'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="info"]:pressed {{
        background-color: {ModernTheme.COLORS['info'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="special"] {{
        background-color: {ModernTheme.COLORS['accent_mauve'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="special"]:hover {{
        background-color: {ModernTheme.COLORS['accent_mauve'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="special"]:pressed {{
        background-color: {ModernTheme.COLORS['accent_mauve'].darker(110).name()} !important;
    }}
    
    /* Secondary button variant */
    QPushButton[button-type="secondary"] {{
        background-color: {ModernTheme.COLORS['surface1'].name()} !important;
        color: {ModernTheme.COLORS['text'].name()} !important;
        border: 1px solid {ModernTheme.COLORS['surface2'].name()} !important;
    }}
    
    QPushButton[button-type="secondary"]:hover {{
        background-color: {ModernTheme.COLORS['surface2'].name()} !important;
        border: 1px solid {ModernTheme.COLORS['accent_blue'].name()} !important;
    }}
    
    QPushButton[button-type="secondary"]:pressed {{
        background-color: {ModernTheme.COLORS['surface0'].name()} !important;
    }}
    
    /* Close button - specific styling */
    QPushButton#closeBtn {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        border: 1px solid {ModernTheme.COLORS['surface2'].name()};
    }}
    
    QPushButton#closeBtn:hover {{
        background-color: {ModernTheme.COLORS['error'].name()};
        color: {ModernTheme.COLORS['background'].name()};
        border: 1px solid {ModernTheme.COLORS['error'].darker(110).name()};
    }}
    
    QPushButton#closeBtn:pressed {{
        background-color: {ModernTheme.COLORS['error'].darker(110).name()};
    }}
    
    QCheckBox {{
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {ModernTheme.COLORS['surface1'].name()};
        background-color: {ModernTheme.COLORS['surface0'].name()};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        border: 2px solid {ModernTheme.COLORS['accent_blue'].name()};
    }}
    
    QComboBox {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        padding: {ModernTheme.SPACING['medium']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QComboBox:focus {{
        border: 2px solid {ModernTheme.COLORS['accent_blue'].name()};
    }}
    
    QComboBox::drop-down {{
            border: none;
        padding-right: 10px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        selection-background-color: {ModernTheme.COLORS['accent_blue'].name()};
        selection-color: {ModernTheme.COLORS['background'].name()};
    }}
    
    /* List and Table styling */
    QListWidget {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        alternate-background-color: {ModernTheme.COLORS['surface0'].name()};
    }}
    
    QListWidget::item {{
        padding: {ModernTheme.SPACING['medium']}px;
        border: 1px solid transparent;
        color: {ModernTheme.COLORS['text'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:hover {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:selected {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].darker(120).name()};
        color: {ModernTheme.COLORS['background'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:selected:hover {{
        background-color: {ModernTheme.COLORS['accent_blue'].lighter(110).name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].darker(120).name()};
        color: {ModernTheme.COLORS['background'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QTextEdit {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        selection-background-color: {ModernTheme.COLORS['accent_blue'].name()};
        selection-color: {ModernTheme.COLORS['background'].name()};
    }}
    
    QTextEdit:focus {{
        border: 2px solid {ModernTheme.COLORS['accent_blue'].name()};
    }}
    
    /* GroupBox styling */
    QGroupBox {{
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        font-weight: 500;
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        margin-top: 10px;
        padding-top: 10px;
    }}
    
    QGroupBox::title {{
        color: {ModernTheme.COLORS['text'].name()};
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        background-color: {ModernTheme.COLORS['background'].name()};
    }}
    
    /* Modern Context Menu Styling */
    QMenu {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        padding: 2px 0px;
        min-width: 150px;
    }}
    
    QMenu::item {{
        background-color: transparent;
        color: {ModernTheme.COLORS['text'].name()};
        padding: {ModernTheme.SPACING['medium']}px {ModernTheme.SPACING['large']}px;
        border: 1px solid transparent;
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        margin: 0px 2px;
    }}
    
    QMenu::item:hover {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        color: {ModernTheme.COLORS['background'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].lighter(120).name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QMenu::item:selected {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        color: {ModernTheme.COLORS['background'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].lighter(120).name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QMenu::item:pressed {{
        background-color: {ModernTheme.COLORS['accent_blue'].darker(110).name()};
        color: {ModernTheme.COLORS['background'].name()};
    }}
    
    QMenu::item:disabled {{
        color: {ModernTheme.COLORS['text_disabled'].name()};
        background-color: transparent;
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {ModernTheme.COLORS['surface1'].name()};
        margin: {ModernTheme.SPACING['small']}px {ModernTheme.SPACING['medium']}px;
    }}
        """ 

def get_context_menu_stylesheet():
    """Get stylesheet for context menus with modern styling"""
    return f"""
        QMenu {{
            background-color: {ModernTheme.COLORS['surface0'].name()};
            border: 1px solid {ModernTheme.COLORS['surface1'].name()};
            border-radius: {ModernTheme.SPACING['border_radius']}px;
            color: {ModernTheme.COLORS['text'].name()};
            font-size: {ModernTheme.FONTS['default_size']}px;
            padding: 0px;
        }}
        
        QMenu::item {{
            background-color: transparent;
            color: {ModernTheme.COLORS['text'].name()};
            padding: {ModernTheme.SPACING['medium']}px {ModernTheme.SPACING['large']}px;
            border: none;
            margin: 0px;
        }}
        
        QMenu::item:hover {{
            background-color: {ModernTheme.COLORS['accent_red'].name()};
            color: {ModernTheme.COLORS['background'].name()};
        }}
        
        QMenu::item:selected {{
            background-color: {ModernTheme.COLORS['accent_red'].name()};
            color: {ModernTheme.COLORS['background'].name()};
        }}
        
        QMenu::item:pressed {{
            background-color: {ModernTheme.COLORS['accent_red'].darker(110).name()};
            color: {ModernTheme.COLORS['background'].name()};
        }}
        
        QMenu::item:disabled {{
            color: {ModernTheme.COLORS['text_disabled'].name()};
            background-color: transparent;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {ModernTheme.COLORS['surface1'].name()};
            margin: {ModernTheme.SPACING['small']}px {ModernTheme.SPACING['medium']}px;
        }}
    """

def get_file_dialog_stylesheet():
    """File dialog stylesheet with comprehensive dark theme"""
    return f"""
    QDialog {{
        background-color: {ModernTheme.COLORS['background'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        font-family: {ModernTheme.FONTS['family']};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QLabel {{
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        background: transparent;
    }}
    
    QLineEdit {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        padding: {ModernTheme.SPACING['medium']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {ModernTheme.COLORS['accent_blue'].name()};
    }}
    
    QPushButton {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        color: {ModernTheme.COLORS['background'].name()};
        border: none;
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        padding: {ModernTheme.SPACING['medium']}px {ModernTheme.SPACING['large']}px;
        font-size: {ModernTheme.FONTS['default_size']}px;
        font-weight: 500;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {ModernTheme.COLORS['accent_blue'].lighter(110).name()};
    }}
    
    QPushButton:pressed {{
        background-color: {ModernTheme.COLORS['accent_blue'].darker(110).name()};
    }}
    
    QPushButton:disabled {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text_disabled'].name()};
    }}
    
    /* Semantic button variants for file dialog - HIGH PRIORITY */
    QPushButton[button-type="success"] {{
        background-color: {ModernTheme.COLORS['success'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="success"]:hover {{
        background-color: {ModernTheme.COLORS['success'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="success"]:pressed {{
        background-color: {ModernTheme.COLORS['success'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="warning"] {{
        background-color: {ModernTheme.COLORS['warning'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="warning"]:hover {{
        background-color: {ModernTheme.COLORS['warning'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="warning"]:pressed {{
        background-color: {ModernTheme.COLORS['warning'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="danger"] {{
        background-color: {ModernTheme.COLORS['error'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="danger"]:hover {{
        background-color: {ModernTheme.COLORS['error'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="danger"]:pressed {{
        background-color: {ModernTheme.COLORS['error'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="info"] {{
        background-color: {ModernTheme.COLORS['info'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="info"]:hover {{
        background-color: {ModernTheme.COLORS['info'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="info"]:pressed {{
        background-color: {ModernTheme.COLORS['info'].darker(110).name()} !important;
    }}
    
    QPushButton[button-type="special"] {{
        background-color: {ModernTheme.COLORS['accent_mauve'].name()} !important;
        color: {ModernTheme.COLORS['background'].name()} !important;
        border: none !important;
    }}
    
    QPushButton[button-type="special"]:hover {{
        background-color: {ModernTheme.COLORS['accent_mauve'].lighter(110).name()} !important;
    }}
    
    QPushButton[button-type="special"]:pressed {{
        background-color: {ModernTheme.COLORS['accent_mauve'].darker(110).name()} !important;
    }}
    
    /* Secondary button variant */
    QPushButton[button-type="secondary"] {{
        background-color: {ModernTheme.COLORS['surface1'].name()} !important;
        color: {ModernTheme.COLORS['text'].name()} !important;
        border: 1px solid {ModernTheme.COLORS['surface2'].name()} !important;
    }}
    
    QPushButton[button-type="secondary"]:hover {{
        background-color: {ModernTheme.COLORS['surface2'].name()} !important;
        border: 1px solid {ModernTheme.COLORS['accent_blue'].name()} !important;
    }}
    
    QPushButton[button-type="secondary"]:pressed {{
        background-color: {ModernTheme.COLORS['surface0'].name()} !important;
    }}
    
    QListWidget {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        alternate-background-color: {ModernTheme.COLORS['surface0'].name()};
    }}
    
    QListWidget::item {{
        padding: {ModernTheme.SPACING['medium']}px;
        border: 1px solid transparent;
        border-bottom: 1px solid {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:hover {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:selected {{
        background-color: {ModernTheme.COLORS['accent_blue'].name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].darker(120).name()};
        color: {ModernTheme.COLORS['background'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    QListWidget::item:selected:hover {{
        background-color: {ModernTheme.COLORS['accent_blue'].lighter(110).name()};
        border: 1px solid {ModernTheme.COLORS['accent_blue'].darker(120).name()};
        color: {ModernTheme.COLORS['background'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
    }}
    
    /* TreeView styling for file browser */
    QTreeView {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        selection-background-color: transparent;
        show-decoration-selected: 0;
        alternate-background-color: {ModernTheme.COLORS['surface1'].name()};
    }}
    
    QTreeView::item {{
        height: {ModernTheme.SPACING['item_height']}px;
        padding: {ModernTheme.SPACING['small']}px;
        border: none;
        margin: 1px 4px;
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        color: {ModernTheme.COLORS['text'].name()};
    }}
    
    QTreeView::item:hover {{
        background-color: {ModernTheme.COLORS['hover'].name()};
        color: {ModernTheme.COLORS['text'].name()};
    }}
    
    QTreeView::item:selected {{
        background-color: transparent;
        color: {ModernTheme.COLORS['text'].name()};
    }}
    

    
    QHeaderView::section {{
        background-color: {ModernTheme.COLORS['surface1'].name()};
        color: {ModernTheme.COLORS['text'].name()};
        border: none;
        padding: {ModernTheme.SPACING['medium']}px;
        font-weight: 500;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {ModernTheme.COLORS['surface2'].name()};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {ModernTheme.COLORS['text_secondary'].name()};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    
    QScrollBar:horizontal {{
        background-color: {ModernTheme.COLORS['surface0'].name()};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {ModernTheme.COLORS['surface2'].name()};
        border-radius: 6px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {ModernTheme.COLORS['text_secondary'].name()};
    }}
    
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    
    /* GroupBox styling */
    QGroupBox {{
        color: {ModernTheme.COLORS['text'].name()};
        font-size: {ModernTheme.FONTS['default_size']}px;
        font-weight: 500;
        border: 1px solid {ModernTheme.COLORS['surface1'].name()};
        border-radius: {ModernTheme.SPACING['border_radius']}px;
        margin-top: 10px;
            padding-top: 10px;
    }}
    
    QGroupBox::title {{
        color: {ModernTheme.COLORS['text'].name()};
            subcontrol-origin: margin;
            left: 10px;
        padding: 0 8px 0 8px;
        background-color: {ModernTheme.COLORS['background'].name()};
    }}
    

    """ 

def apply_semantic_button_color(button, button_type):
    """
    Apply semantic color to a QPushButton
    
    Args:
        button: QPushButton instance
        button_type: str - One of 'success', 'warning', 'danger', 'info', 'special', 'secondary'
    """
    valid_types = ['success', 'warning', 'danger', 'info', 'special', 'secondary']
    if button_type not in valid_types:
        print(f"Warning: Unknown button type '{button_type}'. Valid types: {valid_types}")
        return
    
    button.setProperty("button-type", button_type)
    # Force style refresh
    button.style().unpolish(button)
    button.style().polish(button)
    button.update() 