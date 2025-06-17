#!/usr/bin/env python3
import logging
from typing import List, Optional

from ..services.gemini_service import GeminiService
# To access config for log level in __main__ or for URIs if not passed via GeminiService
from ..utils.config import config 

logger = logging.getLogger(__name__)

class QAModule:
    """
    Handles question answering by leveraging the Gemini API with contextual information
    from a PDF guidebook and HTML snapshot of a calculator website.
    """

    def __init__(self, gemini_service: GeminiService):
        """
        Initializes the QAModule with a GeminiService instance.

        Args:
            gemini_service: An instance of GeminiService to interact with the Gemini API.
        """
        self.gemini_service = gemini_service
        if not self.gemini_service._guidebook_file_uri:
            logger.warning("QAModule initialized but GeminiService is missing Guidebook File URI. Q&A may be limited.")
        if not self.gemini_service._calculator_html_file_uri:
            logger.warning("QAModule initialized but GeminiService is missing Calculator HTML File URI. Q&A may be limited.")

    def answer_question(self, question: str) -> str:
        """
        Answers a user's question based on the BA II Plus guidebook and calculator website HTML.

        Args:
            question: The user's question.

        Returns:
            The generated answer string from the AI, or an error message if issues occur.
        """
        if not question:
            logger.warning("answer_question called with an empty question.")
            return "Please provide a question."

        # Prepare the list of file URIs to be used as context
        file_uris: List[str] = []
        if self.gemini_service._guidebook_file_uri:
            file_uris.append(self.gemini_service._guidebook_file_uri)
        else:
            logger.warning("Guidebook File URI is not available for Q&A.")
        
        if self.gemini_service._calculator_html_file_uri:
            file_uris.append(self.gemini_service._calculator_html_file_uri)
        else:
            logger.warning("Calculator HTML File URI is not available for Q&A.")

        if not file_uris:
            logger.error("No contextual file URIs (guidebook, HTML) are available. Cannot answer question effectively.")
            return "I apologize, but I don't have the necessary context documents (guidebook or website snapshot) to answer your question."

        # Construct the prompt for Gemini
        # Persona: AE Sales Rep
        # Task: Answer based on provided PDF guidebook and HTML snapshot
        prompt = (
            f"You are an AE Sales Rep for the BA II Plus calculator. Your goal is to convincingly answer user questions "
            f"and demonstrate how the calculator meets their requirements. "
            f"Please answer the following question using the information available in the provided BA II Plus PDF guidebook "
            f"and the HTML snapshot of the calculator website (https://baiiplus.com/). "
            f"Prioritize information from the guidebook if there's a conflict or for detailed operational steps. "
            f"Be helpful, clear, and maintain a professional, positive tone.\n\n"
            f"User's Question: \"{question}\"\n\n"
            f"Answer:"
        )

        logger.info(f"Sending question to Gemini for Q&A: '{question[:100]}...'")
        logger.debug(f"Using file URIs for context: {file_uris}")
        
        try:
            answer = self.gemini_service.generate_text(prompt=prompt, file_uris=file_uris)
            if not answer.strip():
                logger.warning("Gemini returned an empty answer for the question.")
                return "I received an empty response from the AI. Please try rephrasing your question."
            logger.info(f"Received answer from Gemini: '{answer[:100]}...'")
            return answer
        except Exception as e:
            logger.error(f"Error during Gemini Q&A text generation: {e}", exc_info=True)
            return f"I encountered an error trying to answer your question. Error: {str(e)}"

# Example Usage
if __name__ == "__main__":
    # Setup basic logging for this direct script run
    LOG_LEVEL_TO_SET = logging.INFO
    try:
        LOG_LEVEL_TO_SET = config.log_level
    except Exception:
        pass # Keep INFO if config is not available or log_level isn't set
    logging.basicConfig(level=LOG_LEVEL_TO_SET, 
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logger.info("--- Q&A Module Direct Run --- ")

    if not config.gemini_api_key:
        logger.critical("GEMINI_API_KEY is not configured. Q&A module cannot run. Check .env file.")
    elif not config.guidebook_file_uri or not config.calculator_html_file_uri:
        logger.critical("Guidebook or Calculator HTML File URI is not configured in .env. Q&A module may not function as intended.")
    else:
        try:
            logger.info("Initializing GeminiService for Q&A module test...")
            gemini_service_instance = GeminiService()
            qa_module_instance = QAModule(gemini_service_instance)
            logger.info("QAModule initialized.")

            questions = [
                "How do I calculate Net Present Value (NPV) on the BA II Plus?",
                "What are the primary functions of the CF key?",
                "Explain the amortization feature.",
                "How to set the number of decimal places?"
            ]

            for q in questions:
                print(f"\nAsking: {q}")
                response = qa_module_instance.answer_question(q)
                print(f"AI Response:\n{response}")
                # Add a small delay if making many calls quickly, though not strictly necessary here
                # import time
                # time.sleep(1) 

        except ValueError as ve: # Catches API key issues from GeminiService initialization
            logger.error(f"Initialization error: {ve}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred during Q&A module test: {e}", exc_info=True)

    logger.info("--- Q&A Module Direct Run Finished ---") 