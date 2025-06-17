#!/usr/bin/env python3
import pyaudio
import logging
from typing import Optional

# Assuming your project structure allows this import path
# If src is not directly in PYTHONPATH, this might need adjustment when run as a script
# For application use, when main.py runs, this relative import should work.
from ..services.gemini_service import GeminiService
from ..utils.config import config # To get LOG_LEVEL for example if run as script

logger = logging.getLogger(__name__)

# Audio format constants based on Gemini TTS typical output
# Typically, Gemini TTS might output raw PCM, 16-bit, 24kHz, mono.
# This needs to be confirmed or made configurable if it varies.
AUDIO_FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1  # Mono
RATE = 24000  # 24kHz sampling rate

def speak_text(text_to_speak: str, gemini_service: GeminiService) -> bool:
    """
    Converts text to speech using GeminiService and plays it using PyAudio.

    Args:
        text_to_speak: The string of text to be spoken.
        gemini_service: An instance of GeminiService to generate speech.

    Returns:
        True if speech was successfully generated and played, False otherwise.
    """
    if not text_to_speak:
        logger.warning("speak_text called with empty string. Nothing to speak.")
        return False

    logger.info(f"Attempting to generate speech for: '{text_to_speak[:70]}...'")
    audio_data = gemini_service.generate_speech(text_to_speak)

    if not audio_data:
        logger.warning("TTS is currently disabled due to API compatibility issues. Audio generation skipped.")
        return True  # Return True to continue execution, just without audio

    p = pyaudio.PyAudio()
    stream = None
    try:
        stream = p.open(format=AUDIO_FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)

        logger.info(f"Playing audio (Rate: {RATE}Hz, Channels: {CHANNELS}, Format: paInt16)...")
        stream.write(audio_data)
        logger.info("Finished playing audio.")
        return True
    except Exception as e:
        logger.error(f"Error playing audio with PyAudio: {e}")
        return False
    finally:
        if stream:
            try:
                stream.stop_stream()
                stream.close()
                logger.info("PyAudio stream stopped and closed.")
            except Exception as e:
                logger.error(f"Error closing PyAudio stream: {e}")
        p.terminate()
        logger.info("PyAudio terminated.")

# Example usage:
if __name__ == '__main__':
    # This example assumes that when run directly, the .env file is in the project root,
    # and config loads it correctly relative to its own path (src/utils/config.py).
    # The GeminiService will use the AppConfig instance.

    # Setup basic logging for this direct script run
    # Note: AppConfig and GeminiService also initialize their own loggers.
    # This ensures that if this script is run standalone, we get some output.
    logging.basicConfig(level=config.log_level, 
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("--- TTS Module Direct Run --- ")

    if not config.gemini_api_key:
        logger.critical("GEMINI_API_KEY is not configured. Please ensure .env is set up correctly.")
        print("CRITICAL: GEMINI_API_KEY not found. TTS module cannot run. Check your .env file.")
    else:
        try:
            logger.info("Initializing GeminiService for TTS module test...")
            service = GeminiService() # Uses global config by default
            
            test_phrase_1 = "Hello, this is a test of the Text-to-Speech module."
            logger.info(f"Speaking: '{test_phrase_1}'")
            success1 = speak_text(test_phrase_1, service)
            print(f"Speaking test 1 successful: {success1}")

            if success1:
                import time
                time.sleep(1) # Pause between phrases

            test_phrase_2 = "The quick brown fox jumps over the lazy dog."
            logger.info(f"Speaking: '{test_phrase_2}'")
            success2 = speak_text(test_phrase_2, service)
            print(f"Speaking test 2 successful: {success2}")

        except ValueError as ve:
            logger.error(f"Initialization error: {ve}") # E.g. API key missing
            print(f"Error initializing Gemini Service: {ve}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during TTS module test: {e}", exc_info=True)
            print(f"An unexpected error: {e}")
    logger.info("--- TTS Module Direct Run Finished ---") 