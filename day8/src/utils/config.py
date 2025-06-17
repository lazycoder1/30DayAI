import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the AI Financial Calculator Assistant.

    Attributes:
        gemini_api_key (str): API key for Gemini.
        log_level (int): Logging level for the application.
        calculator_url (str): URL of the financial calculator.
        text_model_name (str): Name of the text generation model.
        multimodal_model_name (str): Name of the multimodal generation model.
        tts_model_name (str): Name of the text-to-speech model.
        guidebook_file_uri (str, optional): URI of the guidebook file for Q&A.
        calculator_html_file_uri (str, optional): URI of the calculator HTML file for demonstrations.
    """
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            logging.warning("GEMINI_API_KEY is not set. Please set it in your .env file or environment.")
            # Potentially raise an error or exit if the API key is critical
            # raise ValueError("GEMINI_API_KEY is not set.")

        # Configure logging level
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_level = getattr(logging, log_level_str, logging.INFO)

        self.calculator_url = os.getenv("CALCULATOR_URL", "https://baiiplus.com/")

        # Model names
        self.text_model_name = os.getenv("TEXT_MODEL_NAME", "gemini-1.5-flash-latest")
        self.multimodal_model_name = os.getenv("MULTIMODAL_MODEL_NAME", "gemini-1.5-flash-latest")
        # Use one of the new models found: models/gemini-2.5-flash-preview-tts or models/gemini-2.5-pro-preview-tts
        self.tts_model_name = os.getenv("TTS_MODEL_NAME", "models/gemini-2.5-flash-preview-tts")

        # File URIs for Q&A and Demonstration modules (Optional)
        self.guidebook_file_uri = os.getenv("GUIDEBOOK_FILE_URI")
        self.calculator_html_file_uri = os.getenv("CALCULATOR_HTML_FILE_URI")

        if not self.guidebook_file_uri:
            logging.warning("GUIDEBOOK_FILE_URI is not set. Q&A module might not function as expected.")
        if not self.calculator_html_file_uri:
            logging.warning("CALCULATOR_HTML_FILE_URI is not set. Some demonstration features might be limited.")


# Global instance of the configuration
config = Config() 