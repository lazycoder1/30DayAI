import os
from dotenv import load_dotenv
import logging
import pathlib

logger = logging.getLogger(__name__)

class AppConfig:
    """Application configuration class."""
    def __init__(self):
        current_file_path = pathlib.Path(__file__).resolve()
        # Assuming config.py is in demo_mvp/src/utils/
        # project_root should be demo_mvp/
        self.project_root: pathlib.Path = current_file_path.parent.parent.parent
        self.dotenv_path: pathlib.Path = self.project_root / ".env"

        if self.dotenv_path.exists():
            logger.info(f"Loading environment variables from {self.dotenv_path}")
            load_dotenv(dotenv_path=self.dotenv_path)
        else:
            logger.warning(f".env file not found at {self.dotenv_path}. Environment variables should be set directly or are already in the environment.")

        # --- API Keys ---
        self.gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # --- General Settings ---
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # --- Gemini Model Names ---
        self.gemini_text_model: str = os.getenv("TEXT_MODEL_NAME", "gemini-1.5-flash-latest")
        self.gemini_multimodal_model: str = os.getenv("MULTIMODAL_MODEL_NAME", "gemini-1.5-flash-latest")
        self.gemini_tts_model: str = os.getenv("TTS_MODEL_NAME", "gemini-2.5-flash-preview-tts")

        # --- External Resource Paths/URLs ---
        self.calculator_url: str = os.getenv("CALCULATOR_URL", "https://baiiplus.com/")
        
        # --- Mouse Control Settings ---
        self.default_action_delay: float = float(os.getenv("DEFAULT_ACTION_DELAY", "0.5"))
        
        # --- Browser Chrome Height Settings ---
        # Fine-tune coordinate calculations for different browser setups
        self.browser_chrome_height_offset: int = int(os.getenv("BROWSER_CHROME_HEIGHT_OFFSET", "0"))
        self.enable_dynamic_chrome_calculation: bool = os.getenv("ENABLE_DYNAMIC_CHROME_CALCULATION", "true").lower() == "true"
        
        # --- Screen Resolution & Scaling Settings (Mac Retina Display Support) ---
        # Physical screen resolution (what screenshot captures)
        self.physical_screen_width: int = int(os.getenv("PHYSICAL_SCREEN_WIDTH", "0"))  # 0 = auto-detect
        self.physical_screen_height: int = int(os.getenv("PHYSICAL_SCREEN_HEIGHT", "0"))  # 0 = auto-detect
        
        # Logical screen resolution (what mouse coordinates use)
        self.logical_screen_width: int = int(os.getenv("LOGICAL_SCREEN_WIDTH", "0"))  # 0 = auto-detect
        self.logical_screen_height: int = int(os.getenv("LOGICAL_SCREEN_HEIGHT", "0"))  # 0 = auto-detect
        
        # Manual scaling factor override (if auto-detection fails)
        self.manual_scale_factor_x: float = float(os.getenv("MANUAL_SCALE_FACTOR_X", "0.0"))  # 0.0 = auto-calculate
        self.manual_scale_factor_y: float = float(os.getenv("MANUAL_SCALE_FACTOR_Y", "0.0"))  # 0.0 = auto-calculate
        
        # Enable/disable coordinate scaling
        self.enable_coordinate_scaling: bool = os.getenv("ENABLE_COORDINATE_SCALING", "true").lower() == "true"
        
        # --- Multi-Monitor Settings ---
        # Which monitor to capture (0 = primary/first monitor, 1 = second monitor, etc.)
        self.target_monitor: int = int(os.getenv("TARGET_MONITOR", "0"))
        
        # Monitor-specific capture region (if you know the exact region)
        self.monitor_capture_region: str = os.getenv("MONITOR_CAPTURE_REGION", "")  # Format: "x,y,width,height" or empty for auto-detect
        
        self.guidebook_pdf_path: str = os.getenv(
            "GUIDEBOOK_PDF_PATH", 
            str(self.project_root / "documents" / "BAIIPlus_Guidebook_EN.pdf")
        )

        # --- Gemini File API URIs ---
        self.guidebook_file_uri: str | None = os.getenv("GUIDEBOOK_FILE_URI")
        self.calculator_html_file_uri: str | None = os.getenv("CALCULATOR_HTML_FILE_URI")

        # --- Mouse Tooltip Configuration ---
        self.enable_mouse_tooltip = os.getenv('ENABLE_MOUSE_TOOLTIP', 'false').lower() == 'true'

        self._validate_configs()

    def _validate_configs(self):
        """Validate critical configurations."""
        if not self.gemini_api_key:
            logger.critical("CRITICAL: GEMINI_API_KEY is not set. Application might not function.")
        else:
            logger.info("GEMINI_API_KEY found.")

        if not self.guidebook_file_uri:
            logger.warning("WARNING: GUIDEBOOK_FILE_URI is not set. Q&A module might not function as expected.")
        else:
            logger.info(f"GUIDEBOOK_FILE_URI loaded: {self.guidebook_file_uri}")

        if not self.calculator_html_file_uri:
            logger.warning("WARNING: CALCULATOR_HTML_FILE_URI is not set. Some demonstration features might be limited.")
        else:
            logger.info(f"CALCULATOR_HTML_FILE_URI loaded: {self.calculator_html_file_uri}")

# Singleton instance of the configuration
config = AppConfig()

# Example of how to access config values (for testing or direct script runs):
if __name__ == "__main__":
    print(f"Project Root: {config.project_root}")
    print(f".env Path: {config.dotenv_path}")
    print(f"Gemini API Key (loaded): {'Set' if config.gemini_api_key else 'Not Set'}")
    print(f"Log Level: {config.log_level}")
    print(f"Text Model: {config.gemini_text_model}")
    print(f"Multimodal Model: {config.gemini_multimodal_model}")
    print(f"TTS Model: {config.gemini_tts_model}")
    print(f"Calculator URL: {config.calculator_url}")
    print(f"Guidebook PDF Path: {config.guidebook_pdf_path}")
    if not (config.project_root / config.guidebook_pdf_path).exists() and not os.path.isabs(config.guidebook_pdf_path):
         # Check if it's an absolute path first
        guidebook_full_path = pathlib.Path(config.guidebook_pdf_path)
        if not guidebook_full_path.is_absolute():
            guidebook_full_path = config.project_root / config.guidebook_pdf_path
        
        if not guidebook_full_path.exists():
            print(f"WARNING: Guidebook PDF not found at specified path: {guidebook_full_path}")
    elif os.path.exists(config.guidebook_pdf_path):
        print(f"Guidebook PDF found at absolute path: {config.guidebook_pdf_path}")
    
    print(f"Guidebook File URI: {config.guidebook_file_uri}")
    print(f"Calculator HTML URI: {config.calculator_html_file_uri}") 