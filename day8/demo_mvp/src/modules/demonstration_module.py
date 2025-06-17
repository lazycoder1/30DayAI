#!/usr/bin/env python3

"""
Demonstration Module for generating and executing calculator demonstrations.
Uses element selectors instead of screenshots for precise, reliable interactions.
"""

import logging
import json
from typing import List, Dict, Optional, Any

from ..services.gemini_service import GeminiService
from ..services.browser_service import BrowserService
from ..services.mouse_service import MouseService
from ..utils.config import config

logger = logging.getLogger(__name__)

class DemonstrationModule:
    """
    Handles the generation and execution of demonstration plans using element selectors
    and precise mouse control via BrowserService + MouseService integration.
    """

    def __init__(self, gemini_service: GeminiService, browser_service: BrowserService, mouse_service: MouseService):
        """
        Initialize the DemonstrationModule with required services.

        Args:
            gemini_service: Instance of GeminiService for AI planning
            browser_service: Instance of BrowserService for element detection
            mouse_service: Instance of MouseService for precise mouse control
        """
        self.gemini_service = gemini_service
        self.browser_service = browser_service
        self.mouse_service = mouse_service
        logger.info("DemonstrationModule initialized with integrated services")

    def get_demonstration_plan(self, instruction: str, html_content: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate a demonstration plan using element selectors instead of screenshots.

        Args:
            instruction: User's instruction for the demonstration 
                        (e.g., "show me how to calculate 1 + 2")
            html_content: Optional HTML content for context
            
        Returns:
            List of dictionaries representing element interactions and voice narration,
            or empty list if error occurs.
        """
        if not instruction:
            logger.warning("get_demonstration_plan called with empty instruction.")
            return []

        try:
            # CRITICAL: Refresh browser position and ensure page is ready for demonstration
            logger.info("Refreshing browser position and page state for demonstration...")
            self._prepare_browser_for_demonstration()

            # Get HTML content if not provided
            if not html_content:
                html_content = self.browser_service.get_current_page_html()
                if not html_content:
                    logger.error("Could not get HTML content from browser")
                    return []

            # Find available calculator elements
            available_elements = self.browser_service.find_calculator_elements()
            logger.info(f"Found {len(available_elements)} calculator elements")

            # Prepare context for Gemini
            file_uris = []
            if self.gemini_service._guidebook_file_uri:
                file_uris.append(self.gemini_service._guidebook_file_uri)
            else:
                logger.warning("Guidebook File URI not available")

            # Create element context for Gemini
            element_context = self._create_element_context(available_elements)

            # Generate prompt for element-based demonstration
            prompt = self._create_demonstration_prompt(instruction, element_context, html_content)

            logger.info(f"Requesting demonstration plan from Gemini for: '{instruction[:100]}...'")

            # Get response from Gemini
            response_text = self.gemini_service.generate_text(
                prompt=prompt,
                file_uris=file_uris
            )

            if not response_text or not response_text.strip():
                logger.warning("Gemini returned empty response for demonstration plan")
                return []

            # Parse and validate the response
            plan = self._parse_demonstration_response(response_text)
            
            if plan:
                logger.info(f"Successfully generated demonstration plan with {len(plan)} steps")
                return plan
            else:
                logger.error("Failed to parse demonstration plan from Gemini response")
                return []

        except Exception as e:
            logger.error(f"Error generating demonstration plan: {e}")
            return []

    def _prepare_browser_for_demonstration(self) -> None:
        """
        Prepare browser for demonstration by refreshing position, scroll state, and ensuring page readiness.
        This ensures all coordinate calculations will be accurate.
        """
        try:
            # Refresh browser window position (handles window movement)
            if not self.browser_service.refresh_browser_position():
                logger.warning("Failed to refresh browser position")
            
            # Get current scroll position for logging
            scroll_info = self.browser_service.get_current_scroll_position()
            if scroll_info['scrollX'] != 0 or scroll_info['scrollY'] != 0:
                logger.info(f"Page scroll detected: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
                logger.info("Coordinate calculations will account for scroll offset")
            else:
                logger.debug("Page is at scroll position (0, 0)")
            
            # Ensure page is ready and bring browser to front
            if self.browser_service.page and not self.browser_service.page.is_closed():
                self.browser_service.page.bring_to_front()
                logger.debug("Browser brought to front for demonstration")
            
            logger.info("Browser preparation complete - coordinates will be dynamically calculated")
            
        except Exception as e:
            logger.error(f"Error preparing browser for demonstration: {e}")

    def execute_demonstration_plan(self, plan: List[Dict[str, Any]]) -> bool:
        """
        Execute a demonstration plan with both element interactions and voice narration.
        
        Args:
            plan: List of demonstration steps
            
        Returns:
            True if execution successful, False otherwise
        """
        if not plan:
            logger.warning("Empty demonstration plan provided")
            return False

        logger.info(f"Executing demonstration plan with {len(plan)} steps")

        try:
            # CRITICAL: Refresh browser state again before execution
            # This ensures coordinates are accurate even if time has passed since planning
            logger.info("Refreshing browser state before demonstration execution...")
            self._prepare_browser_for_demonstration()

            success = True
            for i, step in enumerate(plan):
                step_type = step.get('type')
                logger.info(f"Executing step {i+1}/{len(plan)}: {step_type}")

                if step_type == 'element_interaction':
                    # Get tooltip text if available
                    tooltip_text = step.get('tooltip_text', '')
                    if not self._execute_element_interaction(step, tooltip_text):
                        success = False
                        logger.error(f"Failed to execute element interaction in step {i+1}")
                        
                elif step_type == 'voice':
                    if not self._execute_voice_step(step):
                        success = False
                        logger.error(f"Failed to execute voice step in step {i+1}")
                        
                else:
                    logger.warning(f"Unknown step type in step {i+1}: {step_type}")

                # Handle timing and pauses
                self._handle_step_timing(step)

            logger.info(f"Demonstration plan execution completed. Success: {success}")
            return success

        except Exception as e:
            logger.error(f"Error executing demonstration plan: {e}")
            return False

    def _create_element_context(self, available_elements: Dict[str, Dict]) -> str:
        """
        Create a context string describing available calculator elements for Gemini.
        
        Args:
            available_elements: Dictionary of element names to element info
            
        Returns:
            String describing available elements
        """
        if not available_elements:
            return "No calculator elements detected."

        context_lines = ["Available calculator elements:"]
        for element_name, element_info in available_elements.items():
            selector = element_info.get('selector', 'Unknown selector')
            context_lines.append(f"- {element_name}: {selector}")

        return "\n".join(context_lines)

    def _create_demonstration_prompt(self, instruction: str, element_context: str, html_content: str) -> str:
        """
        Create a prompt for Gemini to generate element-based demonstration plans.
        
        Args:
            instruction: User's instruction
            element_context: Available elements description
            html_content: HTML content for additional context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert financial calculator sales representative demonstrating the BA II Plus calculator. Your goal is to provide clear, accurate, and educational demonstrations that help users understand how to use the calculator effectively.

INSTRUCTION: {instruction}

AVAILABLE CALCULATOR ELEMENTS:
{element_context}

PLANNING PROCESS:
1. First, carefully analyze the user's request and break it down into logical steps
2. Reference the BA II Plus manual to ensure accuracy of the steps
3. Consider the user's perspective and what they need to learn
4. Plan each step to be clear and educational
5. Verify that all required elements are available
6. Ensure the sequence of steps is logical and efficient

Please generate a step-by-step demonstration plan using the available elements. Return your response as a JSON array with the following structure:

[
    {{
        "type": "voice",
        "content": "Text to be spoken to the user",
        "timing": "before_interaction"
    }},
    {{
        "type": "element_interaction", 
        "action": "click",
        "element_selector": "button.btn-number:has-text('1')",
        "description": "Click the number 1 button",
        "timing": "immediate",
        "tooltip_text": "Clicking the number 1 button to enter the first digit"
    }},
    {{
        "type": "element_interaction",
        "action": "type", 
        "value": "1000",
        "description": "Type the value 1000",
        "timing": "immediate",
        "tooltip_text": "Entering the value 1000 into the calculator"
    }}
]

IMPORTANT GUIDELINES:
1. Use ONLY elements that are listed in the "AVAILABLE CALCULATOR ELEMENTS" section above
2. For element interactions, use the exact selectors from the available elements list
3. Common patterns for the calculator include:
   - Numbers: "button.btn-number:has-text('1')", "button.btn-number:has-text('2')", etc.
   - Operators: "button.btn-operator:has-text('+')", "button.btn-operator:has-text('-')", etc.
   - Functions: "button.btn-function:has-text('CF')", "button.btn-function:has-text('NPV')", etc.
   - Compute: "button.btn-operator:has-text('CPT')" for calculations
   - Clear: "button.btn-operator:has-text('CE/C')" for clearing
4. Include voice narration to explain each step as a sales representative would
5. Make the demonstration clear and educational
6. Only return the JSON array, no additional text
7. Ensure all selectors match exactly what's available
8. For element interactions, include a concise tooltip_text that explains what the action does
   - Keep tooltip text short and informative (max 50 characters)
   - Make it user-friendly and educational
   - Focus on the purpose of the action

DEMONSTRATION QUALITY GUIDELINES:
1. Accuracy: Double-check all steps against the manual
2. Clarity: Each step should be clear and easy to follow
3. Education: Explain the purpose of each action
4. Efficiency: Use the most direct method to achieve the goal
5. Verification: Include steps to verify the result
6. Error Prevention: Guide users to avoid common mistakes
7. Context: Provide relevant background information
8. Pace: Allow time for users to understand each step

If you cannot complete the instruction with available elements, return an empty array [].
"""
        return prompt

    def _parse_demonstration_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse Gemini's response into a demonstration plan.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed demonstration plan or empty list
        """
        try:
            # Clean up response text
            response_text = response_text.strip()
            
            # Remove code block markers if present
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()

            # Parse JSON
            plan = json.loads(response_text)
            
            if not isinstance(plan, list):
                logger.error(f"Expected list, got {type(plan)}")
                return []

            # Validate plan structure
            for i, step in enumerate(plan):
                if not isinstance(step, dict):
                    logger.error(f"Step {i} is not a dictionary")
                    return []
                    
                step_type = step.get('type')
                if step_type not in ['voice', 'element_interaction']:
                    logger.error(f"Invalid step type in step {i}: {step_type}")
                    return []

            logger.debug(f"Successfully parsed demonstration plan with {len(plan)} steps")
            return plan

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. Response: {response_text[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Error parsing demonstration response: {e}")
            return []

    def _execute_element_interaction(self, step: Dict[str, Any], tooltip_text: str = '') -> bool:
        """
        Execute an element interaction step.
        
        Args:
            step: The step dictionary containing action details
            tooltip_text: Optional text to display in the tooltip
            
        Returns:
            True if successful, False otherwise
        """
        try:
            action = step.get('action')
            element_selector = step.get('element_selector')
            value = step.get('value')
            
            if not element_selector:
                logger.error("No element selector provided in step")
                return False

            # Get element coordinates
            element_coords = self.browser_service.get_element_coordinates(element_selector)
            if not element_coords:
                logger.error(f"Could not find element with selector: {element_selector}")
                return False

            # Move to element with tooltip
            if not self.mouse_service.move_to_element(element_coords, tooltip_text=tooltip_text):
                logger.error(f"Failed to move to element: {element_selector}")
                return False

            # Perform the action
            if action == 'click':
                if not self.mouse_service.click_element(element_coords):
                    logger.error(f"Failed to click element: {element_selector}")
                    return False
            elif action == 'type' and value is not None:
                if not self.mouse_service.type_text(value):
                    logger.error(f"Failed to type value: {value}")
                    return False
            else:
                logger.error(f"Invalid action or missing value: {action}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error executing element interaction: {e}")
            return False

    def _execute_voice_step(self, step: Dict[str, Any]) -> bool:
        """
        Execute a voice narration step.
        
        Args:
            step: Step dictionary with voice content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            content = step.get('content', '')
            if not content:
                logger.warning("Empty voice content")
                return True

            # For now, just log the voice content
            # In a full implementation, this would use TTS
            logger.info(f"VOICE: {content}")
            
            # TODO: Integrate with TTS module when available
            # self.tts_service.speak(content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing voice step: {e}")
            return False

    def _handle_step_timing(self, step: Dict[str, Any]) -> None:
        """
        Handle timing and pauses for a step.
        
        Args:
            step: Step dictionary with timing information
        """
        import time
        
        timing = step.get('timing')
        if timing == 'pause':
            duration = step.get('duration', 1.0)
            logger.debug(f"Pausing for {duration} seconds")
            time.sleep(duration)
        elif timing == 'after_interaction':
            # Small pause after interactions
            time.sleep(0.5)


# Example usage
if __name__ == "__main__":
    from ..services.browser_service import BrowserService
    from ..services.mouse_service import MouseService
    from ..services.gemini_service import GeminiService
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    logger.info("--- Demonstration Module Test ---")

    if not config.gemini_api_key:
        logger.critical("GEMINI_API_KEY not configured")
        exit(1)

    try:
        # Initialize services
        gemini_service = GeminiService()
        
        with BrowserService() as browser_service:
            mouse_service = MouseService(browser_service)
            demo_module = DemonstrationModule(gemini_service, browser_service, mouse_service)
            
            # Test demonstration planning
            test_instruction = "Show me how to calculate 1 + 2"
            print(f"\nGenerating demonstration plan for: {test_instruction}")
            
            plan = demo_module.get_demonstration_plan(test_instruction)
            
            if plan:
                print(f"\nGenerated plan with {len(plan)} steps:")
                print(json.dumps(plan, indent=2))
                
                # Test execution
                print("\nExecuting demonstration plan...")
                success = demo_module.execute_demonstration_plan(plan)
                print(f"Execution successful: {success}")
            else:
                print("Failed to generate demonstration plan")

    except Exception as e:
        logger.error(f"Error during demonstration module test: {e}")

    logger.info("--- Demonstration Module Test Finished ---") 