# Configuration management for AI Interaction Tool
import json
import os
import sys
from ..constants import CONFIG_FILENAME, DEFAULT_LANGUAGE

class ConfigManager:
    """
    Quản lý cấu hình cho AI Interaction Tool
    """
    
    def __init__(self):
        """
        Khởi tạo ConfigManager với đường dẫn file cấu hình
        """
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            CONFIG_FILENAME
        )
        self.config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self):
        """
        Trả về cấu hình mặc định
        
        Returns:
            dict: Dictionary chứa cấu hình mặc định
        """
        return {
            'language': DEFAULT_LANGUAGE,
            'window_size': {
                'width': 700,
                'height': 500
            },
            'ui_preferences': {
                'continue_chat_default': True,
                'remember_last_path': True,
                'auto_expand_folders': True
            }
        }
    
    def load_config(self):
        """
        Tải cấu hình từ file config.json nếu tồn tại
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge với config mặc định để đảm bảo có đủ các key
                    self.config.update(loaded_config)
                    print(f"[ConfigManager] Đã tải cấu hình từ {self.config_path}", file=sys.stderr)
            else:
                print(f"[ConfigManager] File cấu hình không tồn tại, sử dụng cấu hình mặc định", file=sys.stderr)
        except Exception as e:
            print(f"[ConfigManager] Lỗi khi tải cấu hình: {str(e)}", file=sys.stderr)
            # Sử dụng cấu hình mặc định nếu có lỗi
            self.config = self._load_default_config()
    
    def save_config(self):
        """
        Lưu cấu hình vào file config.json
        
        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            print(f"[ConfigManager] Đã lưu cấu hình vào {self.config_path}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[ConfigManager] Lỗi khi lưu cấu hình: {str(e)}", file=sys.stderr)
            return False
    
    def get(self, key, default=None):
        """
        Lấy giá trị cấu hình theo key
        
        Args:
            key (str): Key cấu hình (có thể dùng dot notation như 'ui_preferences.continue_chat_default')
            default: Giá trị mặc định nếu key không tồn tại
            
        Returns:
            Giá trị cấu hình hoặc default
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key, value):
        """
        Đặt giá trị cấu hình
        
        Args:
            key (str): Key cấu hình (có thể dùng dot notation)
            value: Giá trị cần đặt
        """
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set the value
            config_ref[keys[-1]] = value
        except Exception as e:
            print(f"[ConfigManager] Lỗi khi đặt cấu hình {key}: {str(e)}", file=sys.stderr)
    
    def get_language(self):
        """
        Lấy ngôn ngữ hiện tại
        
        Returns:
            str: Mã ngôn ngữ
        """
        return self.get('language', DEFAULT_LANGUAGE)
    
    def set_language(self, language):
        """
        Đặt ngôn ngữ và lưu cấu hình
        
        Args:
            language (str): Mã ngôn ngữ
        """
        self.set('language', language)
        self.save_config()
    
    def get_window_size(self):
        """
        Lấy kích thước cửa sổ
        
        Returns:
            tuple: (width, height)
        """
        size = self.get('window_size', {'width': 700, 'height': 500})
        return size.get('width', 700), size.get('height', 500)
    
    def set_window_size(self, width, height):
        """
        Đặt kích thước cửa sổ
        
        Args:
            width (int): Chiều rộng
            height (int): Chiều cao
        """
        self.set('window_size', {'width': width, 'height': height})
        self.save_config() 