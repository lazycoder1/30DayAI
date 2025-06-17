#!/usr/bin/env python3

"""
AI Financial Calculator Assistant - Main Application

COORDINATE SYSTEM FEATURES:
- ✅ Dynamic position refresh: Browser window position refreshed on every AI request
- ✅ Automatic scroll handling: Page scroll offset calculated and compensated automatically  
- ✅ 20px chrome height adjustment: Precise clicking with improved accuracy
- ✅ Force refresh positioning: All element interactions use dynamic coordinate calculation
- ✅ Browser movement handling: Accurate clicks even when browser window is moved
- ✅ Production-ready reliability: Robust fallbacks and error handling

The coordinate system now ensures accurate mouse clicks regardless of:
- Browser window movement
- Page scrolling (vertical/horizontal)  
- Time gaps between planning and execution
- Multiple sequential AI requests
"""

import logging
import time
from io import BytesIO

# Project-specific imports
from .utils import config, helpers
from .services.gemini_service import GeminiService
from .services.browser_service import BrowserService
from .services.mouse_service import MouseService
from .modules.qa_module import QAModule
from .modules.demonstration_module import DemonstrationModule
from .modules import tts_module
from .core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

def main():
    """Main function to run the AI Financial Calculator Assistant."""
    
    # === TEMPORARY: DISABLE VOICE FOR TESTING ===
    DISABLE_VOICE = True  # Set to False to re-enable voice
    
    helpers.setup_logging()
    logger.info(f"Starting AI Financial Calculator Assistant (Log Level: {config.log_level})...")
    
    if DISABLE_VOICE:
        logger.info("VOICE/TTS DISABLED - Testing element-based interactions only")
        print("🔇 Voice disabled - Testing element-based interactions only")

    # --- Initialize Services and Modules ---
    gemini_service = None
    browser_service = None
    mouse_service = None
    orchestrator = None

    try:
        logger.info("Initializing GeminiService...")
        gemini_service = GeminiService(text_model_name=config.gemini_text_model, multimodal_model_name=config.gemini_multimodal_model)
        logger.info("GeminiService initialized.")

        logger.info("Initializing BrowserService...")
        calculator_url = getattr(config, 'calculator_url', 'https://baiiplus.com/')
        logger.info(f"Target calculator URL: {calculator_url}")
        browser_service = BrowserService(calculator_url)
        logger.info("BrowserService initialized and browser launched.")

        logger.info("Initializing MouseService...")
        mouse_service = MouseService(browser_service)
        logger.info("MouseService initialized.")

        logger.info("Initializing QAModule...")
        qa_module = QAModule(gemini_service)
        logger.info("QAModule initialized.")

        logger.info("Initializing DemonstrationModule...")
        demonstration_module = DemonstrationModule(gemini_service, browser_service, mouse_service)
        logger.info("DemonstrationModule initialized.")

        logger.info("Initializing Orchestrator...")
        orchestrator = Orchestrator(qa_module, demonstration_module, browser_service)
        logger.info("Orchestrator initialized.")

    except ValueError as ve:
        logger.critical(f"Configuration error during initialization: {ve}", exc_info=True)
        print(f"Critical configuration error: {ve}. Please check your .env file and Gemini API key.")
        return # Exit if core services can't initialize
    except Exception as e:
        logger.critical(f"Failed to initialize core services: {e}", exc_info=True)
        print(f"An unexpected error occurred during initialization: {e}")
        if browser_service:
            browser_service.close()
        return

    # --- Main Application Loop ---
    try:
        logger.info("Starting main application loop. Type 'exit' or 'quit' to stop.")
        print("\nWelcome to the AI Financial Calculator Assistant!")
        print("How can I help you today? (Type 'exit' or 'quit' to stop)")

        while True:
            user_input = input("> ").strip()

            if user_input.lower() in ["exit", "quit"]:
                logger.info("User requested to exit.")
                break
            
            if not user_input:
                continue

            logger.info(f"User input: '{user_input}'")
            intent = orchestrator.determine_intent(user_input)
            response_data = None

            if intent == "demonstration":
                print("Preparing for demonstration...")
                logger.info("Demonstration intent: Using element-based interaction...")
                try:
                    # Generate demonstration plan using element selectors
                    response_data = orchestrator.handle_user_request(user_input)
                except Exception as e:
                    logger.error(f"Error during demonstration handling: {e}", exc_info=True)
                    print(f"Error during demonstration setup: {e}")
                    if not DISABLE_VOICE:
                        tts_module.speak_text(f"I encountered an error setting up the demonstration: {e}", gemini_service)
                    continue
            
            elif intent == "qa":
                response_data = orchestrator.handle_user_request(user_input)
            
            else: # Should not happen with current orchestrator logic
                logger.error(f"Orchestrator returned unknown intent type: {intent}")
                print("Sorry, I'm not sure how to handle that request.")
                if not DISABLE_VOICE:
                    tts_module.speak_text("I'm not sure how to handle that request.", gemini_service)
                continue

            # --- Process and Execute Response ---
            if response_data:
                response_type = response_data.get("type")
                if response_type == "qa":
                    answer = response_data.get("response", "I don't have an answer for that.")
                    print(f"\nAI Assistant: {answer}")
                    if not DISABLE_VOICE:
                        tts_module.speak_text(answer, gemini_service)
                
                elif response_type == "demonstration":
                    plan = response_data.get("plan")
                    if response_data.get("error"):
                        error_msg = response_data.get("error")
                        logger.error(f"Demonstration plan error: {error_msg}")
                        print(f"Error in demonstration: {error_msg}")
                        if not DISABLE_VOICE:
                            tts_module.speak_text(f"Sorry, I couldn't generate the demonstration plan: {error_msg}", gemini_service)
                    elif not plan:
                        logger.warning("Demonstration plan is empty or not generated.")
                        print("Sorry, I couldn't generate a demonstration plan for that.")
                        if not DISABLE_VOICE:
                            tts_module.speak_text("I'm sorry, I couldn't generate a demonstration plan for that request.", gemini_service)
                    else:
                        print("\n🎯 Starting element-based demonstration...")
                        logger.info(f"Executing demonstration plan with {len(plan)} steps using element selectors.")
                        
                        # Execute demonstration plan using the new DemonstrationModule
                        success = demonstration_module.execute_demonstration_plan(plan)
                        
                        if success:
                            print("✅ Demonstration completed successfully!")
                            logger.info("Demonstration execution completed successfully")
                        else:
                            print("❌ Demonstration encountered some issues")
                            logger.warning("Demonstration execution had some failures")
                            
                else:
                    logger.warning(f"Unknown response type: {response_type}")
                    print("I'm not sure how to process that response.")
            else:
                logger.warning("No response data received from orchestrator.")
                print("Sorry, I didn't receive a proper response.")

            print("\nHow else can I help you? (Type 'exit' or 'quit' to stop)")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C).")
        print("\nApplication stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error in main application loop: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
    finally:
        # --- Cleanup ---
        if browser_service:
            logger.info("Closing BrowserService...")
            browser_service.close()
            logger.info("BrowserService closed.")
        
        logger.info("AI Financial Calculator Assistant stopped.")
        print("Goodbye!")

if __name__ == "__main__":
    main() 