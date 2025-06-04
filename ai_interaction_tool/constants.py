# Constants for AI Interaction Tool
import os

# Window settings
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
MIN_INPUT_HEIGHT = 200
MAX_FILE_LIST_HEIGHT = 80

# File settings
CONFIG_FILENAME = "config.json"
SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

# UI settings
TREE_DEPTH_EXPANSION = 0
SHADOW_BLUR_RADIUS = 15
SHADOW_OFFSET = (0, 0)
SHADOW_OPACITY = 80

# Metadata format
METADATA_FORMAT = "[AI_INTERACTION_TOOL] METADATA: {{'continue_chat': {}}}"

# Default paths
DEFAULT_PATH = os.path.expanduser("~")

# Languages
SUPPORTED_LANGUAGES = ["en", "vi"]
DEFAULT_LANGUAGE = "en" 