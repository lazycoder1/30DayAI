# Gemini API service 
import google.generativeai as genai
import os
import logging
from PIL import Image
from io import BytesIO
from typing import List, Dict, Union, Optional, Any
from ..utils.config import config # Import the AppConfig instance
import base64

logger = logging.getLogger(__name__)

class GeminiService:
    """
    A service class to interact with the Google Gemini API.
    Handles text generation, multimodal prompting, and text-to-speech.
    """
    def __init__(self, 
                 api_key: str | None = None, 
                 text_model_name: str | None = None, 
                 multimodal_model_name: str | None = None, 
                 tts_model_name: str | None = None):
        """
        Initializes the GeminiService.
        Uses configuration from AppConfig by default, but can be overridden by direct arguments.

        Args:
            api_key: The Google Gemini API key. Overrides config if provided.
            text_model_name: The name of the text generation model. Overrides config if provided.
            multimodal_model_name: The name of the multimodal model. Overrides config if provided.
            tts_model_name: The name of the TTS model. Overrides config if provided.
        """
        self.api_key = api_key or config.gemini_api_key
        self.text_model_name = text_model_name or config.gemini_text_model
        self.multimodal_model_name = multimodal_model_name or config.gemini_multimodal_model
        self.tts_model_name = tts_model_name or config.gemini_tts_model
        
        # Store the full URI, but we'll extract the 'name' part before API calls
        self._guidebook_file_uri = config.guidebook_file_uri
        self._calculator_html_file_uri = config.calculator_html_file_uri

        if not self.api_key:
            logger.critical(f"GEMINI_API_KEY not found. Please set it in .env or pass it to the constructor.")
            raise ValueError("GEMINI_API_KEY is required for GeminiService")
        
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini API configured successfully in GeminiService.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API in GeminiService: {e}")
            raise

        self.text_model = genai.GenerativeModel(self.text_model_name)
        logger.info(f"Using text model: {self.text_model_name}")
        self.multimodal_model = genai.GenerativeModel(self.multimodal_model_name)
        logger.info(f"Using multimodal model: {self.multimodal_model_name}")
        
        # Instantiate a GenerativeModel for TTS
        try:
            self.speech_model = genai.GenerativeModel(self.tts_model_name)
            logger.info(f"TTS model initialized: {self.tts_model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize TTS model ({self.tts_model_name}): {e}")
            # Depending on strictness, could raise an error or allow service to continue without TTS
            self.speech_model = None # Ensure it's None if initialization fails

        if not self._guidebook_file_uri:
            logger.warning("Guidebook File URI not configured. Q&A and Demonstration features requiring it may be affected.")
        if not self._calculator_html_file_uri:
            logger.warning("Calculator HTML File URI not configured. Demonstration features requiring it may be affected.")

    def _get_file_name_from_uri(self, uri: str) -> str | None:
        """Extracts the 'files/...' name from a full URI."""
        if not uri:
            return None
        # Example URI: https://generativelanguage.googleapis.com/v1beta/files/w4mkj0n5apl2
        # We need to extract "files/w4mkj0n5apl2"
        if '/files/' in uri:
            return 'files/' + uri.split('/files/')[-1]
        logger.warning(f"Could not extract file name from URI: {uri}")
        return None

    def list_available_models(self):
        """Lists available Gemini models and their supported generation methods."""
        logger.info("Listing available Gemini models:")
        print("\nAvailable Gemini Models:")
        for m in genai.list_models():
            supported_methods = getattr(m, 'supported_generation_methods', 'N/A')
            print(f"  Name: {m.name}")
            print(f"    Display Name: {getattr(m, 'display_name', 'N/A')}")
            print(f"    Description: {getattr(m, 'description', 'N/A')[:100]}...")
            print(f"    Supported Generation Methods: {supported_methods}")
            # Check if it's a TTS model based on typical naming or capabilities
            if "text-to-speech" in m.name or "tts" in m.name or (isinstance(supported_methods, list) and any("generateSpeech" in method or "synthesizeSpeech" in method for method in supported_methods)):
                print(f"    >> POTENTIAL TTS MODEL <<")
            print("-" * 20)

    def generate_text(self, prompt: str, file_uris: list[str] | None = None) -> str:
        """
        Generates text using the configured text model, optionally with file context.

        Args:
            prompt: The text prompt to send to the model.
            file_uris: A list of file URIs to include in the prompt.

        Returns:
            The generated text as a string.

        Raises:
            Exception: If there is an error during generation or no text is returned.
        """
        try:
            logger.info(f"Generating text with model {self.text_model_name}.")
            
            content_parts = [prompt]
            if file_uris:
                for uri in file_uris:
                    file_name = self._get_file_name_from_uri(uri)
                    if not file_name:
                        logger.error(f"Could not process invalid file URI: {uri}")
                        continue
                    try:
                        file_input = genai.get_file(name=file_name) # Verify file exists via API
                        content_parts.append(file_input)
                        logger.info(f"Added file URI to prompt: {file_name} (MIME: {file_input.mime_type})")
                    except Exception as e:
                        logger.error(f"Failed to retrieve or prepare file {file_name} for prompting: {e}")
                        # Decide if you want to continue without the file or raise an error
                        # For now, we log and continue without it.
            
            response = self.text_model.generate_content(content_parts)
            # Assuming response.text or similar attribute holds the generated text.
            # You might need to inspect response.parts or response.candidates[0].content.parts[0].text
            # based on the Gemini API version and response structure.
            if response.parts:
                return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            else:
                logger.warning(f"No text found in response: {response}")
                raise ValueError(f"No text content returned from Gemini model for prompt: {prompt[:100]}...")

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            # Consider re-raising or returning a specific error message
            raise

    def generate_multimodal_content(self, prompt_parts: list[Any], file_uris: list[str] | None = None) -> str:
        """
        Generates content using the multimodal model with a list of parts (text, images, file URIs).
        Images should be passed as part of prompt_parts (e.g., PIL.Image objects or Part.from_data).
        Additional file URIs can also be provided to be appended.

        Args:
            prompt_parts: A list where each item can be a string (text), 
                          a PIL Image object, or a dict adhering to Gemini content part structure.
            file_uris: A list of file URIs to include in the prompt.

        Returns:
            The generated text content as a string.

        Raises:
            Exception: If there is an error during generation or no text is returned.
        """
        try:
            logger.info(f"Generating multimodal content with model {self.multimodal_model_name}.")
            
            content_to_send = list(prompt_parts) # Start with provided parts (text, inline images)

            if file_uris:
                for uri in file_uris:
                    file_name = self._get_file_name_from_uri(uri)
                    if not file_name:
                        logger.error(f"Could not process invalid file URI for multimodal content: {uri}")
                        continue
                    try:
                        file_input = genai.get_file(name=file_name) # Verify/get file metadata
                        content_to_send.append(file_input)
                        logger.info(f"Added file URI to multimodal prompt: {file_name} (MIME: {file_input.mime_type})")
                    except Exception as e:
                        logger.error(f"Failed to retrieve or prepare file {file_name} for multimodal prompting: {e}")
            
            response = self.multimodal_model.generate_content(content_to_send)

            # Similar to generate_text, extract the response text carefully
            if response.parts:
                return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            else:
                logger.warning(f"No text found in multimodal response: {response}")
                raise ValueError(f"No text content returned from Gemini multimodal model.")

        except Exception as e:
            logger.error(f"Error generating multimodal content: {e}")
            raise

    def generate_speech(self, text_to_speak: str) -> Optional[bytes]:
        """
        Generates audio from text using Gemini TTS.
        
        Note: This is a simplified implementation since the current google-generativeai
        library doesn't support the advanced TTS features. This returns None for now
        to prevent crashes, allowing the rest of the application to work.

        Args:
            text_to_speak: The text to convert to speech.

        Returns:
            None (TTS temporarily disabled due to API compatibility issues)
        """
        logger.warning(f"TTS temporarily disabled. Would have spoken: '{text_to_speak[:100]}...'")
        return None
        
        # TODO: Implement TTS using the new google-genai library when available
        # The current google-generativeai library doesn't support the required TTS API structure

# Example usage (for testing purposes, typically not run directly from here)
if __name__ == '__main__':
    # Ensure the config module (which loads .env) is imported if running this directly
    # This is now handled by the top-level import of `config`
    # from dotenv import load_dotenv
    # load_dotenv(dotenv_path="../../.env") # Path from src/services to project root .env
    
    # Configure basic logging for the example (config.py also sets up a logger)
    # If run directly, this ensures logging is active.
    # If imported, the main app's logging setup should take precedence.
    if not logging.getLogger().hasHandlers(): # Setup basic logging only if no handlers are configured
        logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    # API key is now sourced from config by default in GeminiService constructor
    # gemini_api_key = config.GEMINI_API_KEY 
    if not config.GEMINI_API_KEY:
        print("CRITICAL: GEMINI_API_KEY is not set. Check .env file or environment variables.")
    else:
        try:
            print(f"Attempting to initialize GeminiService using AppConfig...")
            # No need to pass api_key explicitly if it's in .env and loaded by config
            service = GeminiService()
            
            # List models first
            print("\n--- Listing Available Models ---")
            service.list_available_models()
            
            # Test text generation
            print("\n--- Testing Text Generation ---")
            text_prompt = "Explain the concept of Net Present Value in simple terms."
            generated_text = service.generate_text(text_prompt)
            print(f"Prompt: {text_prompt}")
            print(f"Response: {generated_text}")

            # Test multimodal generation (requires an image)
            print("\n--- Testing Multimodal Generation (with dummy image) ---")
            try:
                dummy_image = Image.new('RGB', (60, 30), color = 'red')
                multimodal_prompt = ["What color is this image?", dummy_image]
                multimodal_text = service.generate_multimodal_content(multimodal_prompt)
                print(f"Multimodal Prompt: ['What color is this image?', <dummy_red_image>]")
                print(f"Multimodal Response: {multimodal_text}")
            except ImportError:
                print("Pillow (PIL) is not installed. Skipping multimodal image test.")
            except Exception as e:
                print(f"Error during multimodal test: {e}")

            # Test TTS
            print("\n--- Testing TTS ---")
            tts_text = "Hello from the AI Financial Calculator Assistant!"
            audio_bytes = service.generate_speech(tts_text)
            if audio_bytes:
                print(f"Generated speech for: '{tts_text}' (audio_bytes length: {len(audio_bytes)})")
            else:
                print(f"Failed to generate speech for: '{tts_text}'")
                
        except ValueError as ve:
            print(f"Initialization Error: {ve}") # Catches GEMINI_API_KEY not found from constructor
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 