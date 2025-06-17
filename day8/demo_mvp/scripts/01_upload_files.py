#!/usr/bin/env python3
import google.generativeai as genai
import os
import pathlib
import logging
from dotenv import load_dotenv
import requests

# Basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Define Paths & Constants ---
# Assumes this script is in demo_mvp/scripts/
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
DOTENV_PATH = PROJECT_ROOT / '.env'
LOCAL_PDF_PATH = PROJECT_ROOT / "documents" / "BAIIPlus_Guidebook_EN.pdf"
CALCULATOR_URL = "https://baiiplus.com/" # URL from which to fetch HTML
HTML_SNAPSHOT_DIR = PROJECT_ROOT / "documents" / "website"
HTML_SNAPSHOT_PATH = HTML_SNAPSHOT_DIR / "baiiplus_com_snapshot.html"

def configure_gemini_api():
    """Loads API key and configures the Gemini API."""
    load_dotenv(dotenv_path=DOTENV_PATH)
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        logger.critical("GEMINI_API_KEY not found in environment variables or .env file.")
        logger.critical(f"Please ensure it's set in {DOTENV_PATH} or as an environment variable.")
        # You could prompt here, but for a script, failing is often better.
        # gemini_api_key = input("Please enter your GEMINI_API_KEY: ")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required.")

    try:
        genai.configure(api_key=gemini_api_key)
        logger.info("Gemini API configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        raise

def fetch_and_save_html(url: str, output_path: pathlib.Path) -> bool:
    """Fetches HTML content from a URL and saves it to a file."""
    try:
        logger.info(f"Fetching HTML from {url}...")
        response = requests.get(url, timeout=30) # 30 seconds timeout
        response.raise_for_status() # Raise an exception for HTTP errors
        html_content = response.text
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"HTML content successfully fetched and saved to {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching HTML from {url}: {e}")
        return False
    except IOError as e:
        logger.error(f"Error saving HTML to {output_path}: {e}")
        return False

def upload_file_to_gemini(file_path: pathlib.Path, display_name: str) -> str | None:
    """Uploads a file to Gemini File API and returns its URI."""
    if not file_path.exists():
        logger.error(f"File not found for upload: {file_path}")
        return None
    try:
        logger.info(f"Uploading '{display_name}' from {file_path}...")
        uploaded_file = genai.upload_file(path=str(file_path), display_name=display_name)
        logger.info(f"Successfully uploaded '{display_name}'. Name: {uploaded_file.name}, URI: {uploaded_file.uri}")
        return uploaded_file.uri
    except Exception as e:
        logger.error(f"Error uploading {display_name} ({file_path}): {e}")
        return None

def main():
    """Main function to orchestrate fetching and uploading files."""
    logger.info("--- Starting File Upload Script ---")
    
    configure_gemini_api() # Will raise error if API key is not set

    # Create the directory for HTML snapshot if it doesn't exist (fetch_and_save_html also does this)
    HTML_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Local PDF path set to: {LOCAL_PDF_PATH}")
    logger.info(f"Calculator URL for HTML: {CALCULATOR_URL}")
    logger.info(f"HTML snapshot will be saved to: {HTML_SNAPSHOT_PATH}")

    if not LOCAL_PDF_PATH.exists():
        logger.error(f"CRITICAL: PDF file not found at {LOCAL_PDF_PATH}. Please ensure it's there.")
        # Decide if you want to exit or continue with HTML only
        # return

    # Fetch and save the HTML
    html_fetch_successful = fetch_and_save_html(CALCULATOR_URL, HTML_SNAPSHOT_PATH)
    if not html_fetch_successful:
        logger.warning("HTML fetching/saving failed. Check logs. Will attempt PDF upload only.")

    # --- Upload PDF ---
    pdf_file_uri = None
    if LOCAL_PDF_PATH.exists():
        pdf_file_uri = upload_file_to_gemini(LOCAL_PDF_PATH, "BA II Plus Guidebook")
    else:
        logger.warning(f"Skipping PDF upload as file not found at {LOCAL_PDF_PATH}")

    # --- Upload HTML snapshot ---
    html_file_uri = None
    if html_fetch_successful and HTML_SNAPSHOT_PATH.exists():
        html_file_uri = upload_file_to_gemini(HTML_SNAPSHOT_PATH, "Calculator Website HTML Snapshot")
    elif not html_fetch_successful:
        logger.warning("Skipping HTML upload because fetching/saving failed earlier.")
    else: # HTML fetch was successful but file doesn't exist (should not happen if saving worked)
        logger.warning(f"Skipping HTML upload as file not found at {HTML_SNAPSHOT_PATH} despite fetch attempt.")

    # --- Results ---
    print("\n--- Upload Script Results ---")
    if pdf_file_uri:
        print(f"PDF Guidebook File URI: {pdf_file_uri}")
        print(f"  Add to .env: GUIDEBOOK_FILE_URI=\"{pdf_file_uri}\"")
    else:
        print("PDF Guidebook upload FAILED or was skipped. Check logs above.")

    if html_file_uri:
        print(f"\nCalculator HTML Snapshot File URI: {html_file_uri}")
        print(f"  Add to .env: CALCULATOR_HTML_FILE_URI=\"{html_file_uri}\"")
    else:
        print("\nCalculator HTML Snapshot upload FAILED or was skipped. Check logs above.")
    
    print("\n--- Script Finished ---")

if __name__ == "__main__":
    main() 