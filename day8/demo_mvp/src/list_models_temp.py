#!/usr/bin/env python3
import logging
import sys
import os

# Ensure the src directory is in the Python path
# This allows the script to find the src package when run from demo_mvp root
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# SRC_DIR = os.path.join(SCRIPT_DIR, "src") # This was for when script was in root
# if SRC_DIR not in sys.path:
# sys.path.insert(0, SRC_DIR)

# When running as python -m src.list_models_temp, imports should be relative to src
from .utils import config, helpers 
from .services.gemini_service import GeminiService

if __name__ == "__main__":
    helpers.setup_logging() # Use the project's logging setup
    logger = logging.getLogger("list_models_temp")
    logger.info("Attempting to list Gemini models...")

    if not config.gemini_api_key:
        logger.critical("GEMINI_API_KEY is not set. Cannot list models. Check .env file.")
        print("CRITICAL: GEMINI_API_KEY not found. Check your .env file.")
    else:
        try:
            service = GeminiService()
            service.list_available_models()
        except ValueError as ve:
            logger.error(f"Initialization Error: {ve}")
            print(f"Error initializing Gemini Service: {ve}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            print(f"An unexpected error: {e}")
    logger.info("Finished listing models.") 