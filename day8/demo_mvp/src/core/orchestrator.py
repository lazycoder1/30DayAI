#!/usr/bin/env python3
import logging
from typing import Dict, Any, Optional, List

from ..modules.qa_module import QAModule
from ..modules.demonstration_module import DemonstrationModule
from ..services.browser_service import BrowserService # Optional, for future use or if passed down
from ..utils.config import config

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Manages the flow of user interaction, determines intent, and routes requests
    to the appropriate module (Q&A or Demonstration).
    """

    DEMONSTRATION_KEYWORDS = [
        "show me how to", "show how to", "demonstrate how to", "demonstrate", "guide me through",
        "perform", "execute", "run through", "how do I use", "how to use", "illustrate",
        "can you do", "do the calculation", "calculate on the", "on the calculator", 
        "use the calculator", "press the buttons", "enter on calculator", "type on calculator",
        "click on", "show me the", "walk through", "step by step", "can you calculate",
        "let me see", "can you show", "input on", "key in", "button press",
        # Additional natural language patterns
        "show me", "show", "let me watch", "watch you", "see you do", "do it on", 
        "perform on", "try on", "test on", "run on", "calculate using", "compute using",
        "add on", "subtract on", "multiply on", "divide on", "work out on"
    ]

    def __init__(self, 
                 qa_module: QAModule, 
                 demonstration_module: DemonstrationModule, 
                 browser_service: Optional[BrowserService] = None):
        """
        Initializes the Orchestrator.

        Args:
            qa_module: An instance of QAModule.
            demonstration_module: An instance of DemonstrationModule.
            browser_service: An optional instance of BrowserService.
        """
        self.qa_module = qa_module
        self.demonstration_module = demonstration_module
        self.browser_service = browser_service # Stored for potential future use
        logger.info("Orchestrator initialized.")

    def determine_intent(self, user_input: str) -> str:
        """
        Determines the user's intent based on keywords in their input.

        Args:
            user_input: The user's text input.

        Returns:
            A string indicating the intent, either "demonstration" or "qa".
        """
        user_input_lower = user_input.lower()
        for keyword in self.DEMONSTRATION_KEYWORDS:
            if keyword in user_input_lower:
                logger.info(f"Intent determined as 'demonstration' based on keyword: '{keyword}'")
                return "demonstration"
        logger.info("Intent determined as 'qa' (default).")
        return "qa"

    def process_qa(self, user_input: str) -> Dict[str, Any]:
        """
        Processes a Q&A request.

        Args:
            user_input: The user's question.

        Returns:
            A dictionary containing the type of response ("qa") and the answer.
        """
        logger.info(f"Processing Q&A request: '{user_input[:100]}...'")
        answer = self.qa_module.answer_question(question=user_input)
        return {"type": "qa", "response": answer}

    def process_demonstration(self, user_input: str) -> Dict[str, Any]:
        """
        Processes a demonstration request using element-based interactions.

        Args:
            user_input: The user's instruction for the demonstration.

        Returns:
            A dictionary containing the type of response ("demonstration") and the plan (list of actions).
        """
        logger.info(f"Processing demonstration request: '{user_input[:100]}...'")
        
        try:
            # Get demonstration plan using element-based approach
            plan = self.demonstration_module.get_demonstration_plan(instruction=user_input)
            
            if not plan:
                logger.warning("Empty demonstration plan returned")
                return {"type": "demonstration", "plan": [], "error": "Could not generate demonstration plan"}
            
            logger.info(f"Generated demonstration plan with {len(plan)} steps")
            return {"type": "demonstration", "plan": plan}
            
        except Exception as e:
            logger.error(f"Error processing demonstration: {e}")
            return {"type": "demonstration", "plan": [], "error": str(e)}

    def handle_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Handles a user request by determining intent and calling the appropriate module.
        Updated to work with element-based demonstrations (no screenshot required).

        Args:
            user_input: The user's text input.

        Returns:
            A dictionary containing the response type and data from the processed module.
        """
        if not user_input or not user_input.strip():
            logger.warning("handle_user_request received empty input.")
            return {"type": "error", "message": "Input cannot be empty."}

        intent = self.determine_intent(user_input)

        if intent == "demonstration":
            return self.process_demonstration(user_input)
        elif intent == "qa":
            return self.process_qa(user_input)
        else:
            logger.error(f"Unknown intent: {intent}. Defaulting to Q&A.")
            # This case should ideally not be reached with current logic
            return self.process_qa(user_input) 

# Example Usage (Illustrative - Requires Mocking for real standalone test)
if __name__ == "__main__":
    LOG_LEVEL_TO_SET = logging.INFO
    try:
        LOG_LEVEL_TO_SET = config.log_level
    except Exception:
        pass 
    logging.basicConfig(level=LOG_LEVEL_TO_SET, 
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    logger.info("--- Orchestrator Module Direct Run (Illustrative) --- ")

    # Mocking dependencies for standalone testing of Orchestrator logic
    class MockQAModule:
        def answer_question(self, question: str) -> str:
            logger.info(f"[MockQAModule] Answering question: {question}")
            return f"This is a mock answer to: {question}"

    class MockDemonstrationModule:
        def get_demonstration_plan(self, instruction: str) -> List[Dict[str, Any]]:
            logger.info(f"[MockDemonstrationModule] Getting plan for: {instruction}")
            return [
                {"type": "voice", "content": f"Mock voice: Starting demonstration for {instruction}", "timing": "before_interaction"},
                {"type": "element_interaction", "action": "click", "element_selector": "button:has-text('1')", "description": "Click number 1"}
            ]
    
    mock_qa_module = MockQAModule()
    mock_demo_module = MockDemonstrationModule()
    
    orchestrator = Orchestrator(qa_module=mock_qa_module, demonstration_module=mock_demo_module)

    test_inputs = [
        "What is NPV?",
        "Show me how to calculate 1 + 1",
        "Explain cash flows.",
        "Demonstrate setting P/Y",
        "How do I use the DATE worksheet?"
    ]

    for text_input in test_inputs:
        print(f"\nProcessing user input: '{text_input}'")
        result = orchestrator.handle_user_request(text_input)
        print(f"Orchestrator Response Type: {result.get('type')}")
        if result.get('type') == 'qa':
            print(f"  Answer: {result.get('response')}")
        elif result.get('type') == 'demonstration':
            print(f"  Plan: {result.get('plan')}")
            if result.get('error'):
                print(f"  Error: {result.get('error')}")
        elif result.get('type') == 'error':
            print(f"  Error: {result.get('message')}")
        print("---")

    logger.info("--- Orchestrator Module Direct Run Finished ---") 