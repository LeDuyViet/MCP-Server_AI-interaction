# File utilities for AI Interaction Tool
import os
import sys
from ..constants import SUPPORTED_ENCODINGS

def read_file_content(file_path):
    """
    Đọc nội dung file với nhiều encoding khác nhau
    
    Args:
        file_path (str): Đường dẫn đến file
        
    Returns:
        dict: Dictionary chứa content hoặc error message
    """
    try:
        # Thử đọc với các encoding khác nhau
        for encoding in SUPPORTED_ENCODINGS:
            try:
                with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                    content = f.read()
                return {
                    "content": content,
                    "encoding": encoding,
                    "success": True
                }
            except UnicodeDecodeError:
                continue
        
        # Nếu tất cả encoding đều thất bại
        return {
            "error": f"Cannot decode file with supported encodings: {SUPPORTED_ENCODINGS}",
            "success": False
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def validate_file_path(file_path):
    """
    Kiểm tra tính hợp lệ của đường dẫn file
    
    Args:
        file_path (str): Đường dẫn file cần kiểm tra
        
    Returns:
        dict: Dictionary chứa kết quả validation
    """
    if not file_path:
        return {
            "valid": False,
            "error": "File path is empty"
        }
    
    if not os.path.exists(file_path):
        return {
            "valid": False,
            "error": "File does not exist"
        }
    
    if not os.path.isfile(file_path):
        return {
            "valid": False,
            "error": "Path is not a file"
        }
    
    try:
        # Kiểm tra quyền đọc file
        with open(file_path, 'r', encoding='utf-8', errors='ignore'):
            pass
        return {
            "valid": True,
            "error": None
        }
    except PermissionError:
        return {
            "valid": False,
            "error": "Permission denied to read file"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def get_file_info(file_path):
    """
    Lấy thông tin chi tiết về file
    
    Args:
        file_path (str): Đường dẫn file
        
    Returns:
        dict: Dictionary chứa thông tin file
    """
    try:
        stat = os.stat(file_path)
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK)
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        } 