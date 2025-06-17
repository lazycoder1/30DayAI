#!/usr/bin/env python3

"""
Mouse Service for precise element-based mouse control.
Integrates with BrowserService to get element coordinates and uses PyAutoGUI for smooth mouse movements.
"""

import pyautogui
import time
import logging
import random
import math
from typing import Tuple, List, Dict, Optional
from ..services.browser_service import BrowserService
from ..utils.config import config

logger = logging.getLogger(__name__)

# Configure PyAutoGUI for macOS
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1      # Small pause between commands

# Default timing settings
DEFAULT_MOVE_DURATION = 0.1    # seconds for mouse movement
DEFAULT_ACTION_DELAY = 0.1     # seconds after actions
DEFAULT_CURVE_INTENSITY = 0.3  # How curved the movement should be

class MouseService:
    """
    Service for precise mouse control using element coordinates from BrowserService.
    """
    
    def __init__(self, browser_service: BrowserService):
        """
        Initialize the Mouse Service with a Browser Service instance.
        
        Args:
            browser_service: BrowserService instance for element detection
        """
        self.browser_service = browser_service
        self._setup_mouse_tooltip()
        logger.info("MouseService initialized with BrowserService integration")

    def _setup_mouse_tooltip(self):
        """Setup CSS tooltip for mouse pointer if enabled."""
        if not config.enable_mouse_tooltip:
            return

        try:
            page = self.browser_service.get_current_page()
            if not page:
                logger.warning("No active page to setup mouse tooltip")
                return

            # Inject CSS for the tooltip
            page.add_style_tag(content="""
                .mouse-tooltip {
                    position: fixed;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 14px;
                    pointer-events: none;
                    z-index: 9999;
                    transform: translate(20px, -50%);
                    transition: opacity 0.2s;
                    opacity: 0;
                    max-width: 300px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .mouse-tooltip.visible {
                    opacity: 1;
                }
            """)

            # Add tooltip div
            page.evaluate("""
                () => {
                    const tooltip = document.createElement('div');
                    tooltip.className = 'mouse-tooltip';
                    tooltip.id = 'mouse-tooltip';
                    document.body.appendChild(tooltip);
                }
            """)

            logger.info("Mouse tooltip CSS setup completed")
        except Exception as e:
            logger.error(f"Error setting up mouse tooltip: {e}")

    def _update_tooltip(self, text: str, visible: bool = True):
        """Update the tooltip text and visibility."""
        if not config.enable_mouse_tooltip:
            return

        try:
            page = self.browser_service.get_current_page()
            if not page:
                return

            page.evaluate(f"""
                () => {{
                    const tooltip = document.getElementById('mouse-tooltip');
                    if (tooltip) {{
                        tooltip.textContent = {repr(text)};
                        tooltip.style.left = window.mouseX + 'px';
                        tooltip.style.top = window.mouseY + 'px';
                        tooltip.classList.toggle('visible', {str(visible).lower()});
                    }}
                }}
            """)
        except Exception as e:
            logger.error(f"Error updating tooltip: {e}")

    def _track_mouse_position(self):
        """Track mouse position for tooltip updates."""
        if not config.enable_mouse_tooltip:
            return

        try:
            page = self.browser_service.get_current_page()
            if not page:
                return

            # Add mouse move listener
            page.evaluate("""
                () => {
                    window.mouseX = 0;
                    window.mouseY = 0;
                    document.addEventListener('mousemove', (e) => {
                        window.mouseX = e.clientX;
                        window.mouseY = e.clientY;
                    });
                }
            """)
        except Exception as e:
            logger.error(f"Error setting up mouse tracking: {e}")

    def move_to_element(self, element_selector: str, duration: float = 2.0, tooltip_text: Optional[str] = None) -> bool:
        """
        Move the mouse to an element using its selector.
        
        Args:
            element_selector: CSS selector or XPath for the element
            duration: Duration of the mouse movement in seconds
            tooltip_text: Optional text to display in the tooltip
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get element coordinates from browser service
            coords = self.browser_service.get_element_coordinates(element_selector)
            if not coords:
                logger.error(f"Could not find element with selector: {element_selector}")
                return False

            # Update tooltip if enabled
            if tooltip_text and config.enable_mouse_tooltip:
                self._update_tooltip(tooltip_text, True)

            # Move mouse to the element
            pyautogui.moveTo(coords['x'], coords['y'], duration=duration)
            logger.debug(f"Moved mouse to element {element_selector} at coordinates ({coords['x']}, {coords['y']})")
            return True

        except Exception as e:
            logger.error(f"Error moving to element: {e}")
            if config.enable_mouse_tooltip:
                self._update_tooltip("", False)
            return False

    def click_element(self, element_selector: str, tooltip_text: Optional[str] = None) -> bool:
        """
        Click an element using its selector.
        
        Args:
            element_selector: CSS selector or XPath for the element
            tooltip_text: Optional text to display in the tooltip
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get element coordinates from browser service
            coords = self.browser_service.get_element_coordinates(element_selector)
            if not coords:
                logger.error(f"Could not find element with selector: {element_selector}")
                return False

            # Update tooltip if enabled
            if tooltip_text and config.enable_mouse_tooltip:
                self._update_tooltip(tooltip_text, True)

            # Click the element
            pyautogui.click(coords['x'], coords['y'])
            logger.debug(f"Clicked element {element_selector} at coordinates ({coords['x']}, {coords['y']})")
            return True

        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            if config.enable_mouse_tooltip:
                self._update_tooltip("", False)
            return False

    def click_element_by_text(self, text: str, element_type: str = "button",
                            duration: float = DEFAULT_MOVE_DURATION,
                            delay_after: float = DEFAULT_ACTION_DELAY,
                            use_curved_movement: bool = True,
                            force_refresh_position: bool = True) -> bool:
        """
        Click on an element identified by its text content.
        Tries both PyAutoGUI and Playwright clicks for better reliability.
        
        Args:
            text: Text content of the element
            element_type: Type of element (e.g., "button", "div")
            duration: Time for mouse movement
            delay_after: Delay after clicking
            use_curved_movement: Whether to use curved movement
            force_refresh_position: Whether to refresh browser position (recommended if window might have moved)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the element by text
            element_info = self.browser_service.find_element_by_text(text, element_type)
            if not element_info:
                logger.error(f"Could not find {element_type} element with text: {text}")
                return False
            
            # Calculate screen coordinates with optional position refresh
            screen_x, screen_y = self.browser_service.calculate_screen_coordinates(
                element_info, force_refresh=force_refresh_position
            )
            
            # Move mouse to element
            if use_curved_movement:
                self._move_mouse_curved(screen_x, screen_y, duration)
            else:
                pyautogui.moveTo(screen_x, screen_y, duration=duration)
            
            # Small pause before clicking
            time.sleep(random.uniform(0.05, 0.15))
            
            # Try PyAutoGUI click first
            try:
                logger.info("Attempting PyAutoGUI click...")
                pyautogui.click()
                logger.info("PyAutoGUI click successful")
            except Exception as pyautogui_error:
                logger.warning(f"PyAutoGUI click failed: {pyautogui_error}")
                # Try Playwright click as fallback
                try:
                    logger.info("Attempting Playwright click as fallback...")
                    page = self.browser_service.get_current_page()
                    if page:
                        # Try to click using Playwright's native click
                        element = page.locator(element_type + ":has-text('" + text + "')")
                        if element.count() > 0:
                            element.click(timeout=5000)  # 5 second timeout
                            logger.info("Playwright click successful")
                        else:
                            logger.error("Element not found by Playwright")
                            return False
                    else:
                        logger.error("No active page for Playwright click")
                        return False
                except Exception as playwright_error:
                    logger.error(f"Playwright click also failed: {playwright_error}")
                    return False
            
            # Delay after clicking
            actual_delay = self._add_random_delay(delay_after)
            time.sleep(actual_delay)
            
            logger.info(f"Successfully clicked {element_type} with text '{text}' at ({screen_x}, {screen_y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking {element_type} with text '{text}': {e}")
            return False

    def type_text(self, text: str, delay_after: float = DEFAULT_ACTION_DELAY) -> bool:
        """
        Type text using PyAutoGUI.
        
        Args:
            text: Text to type
            delay_after: Delay after typing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not text:
                logger.warning("Empty text provided to type_text")
                return True
                
            logger.info(f"Typing text: '{text}'")
            pyautogui.write(text, interval=0.05)  # Small interval between keystrokes
            
            # Delay after typing
            actual_delay = self._add_random_delay(delay_after)
            time.sleep(actual_delay)
            
            return True
            
        except Exception as e:
            logger.error(f"Error typing text '{text}': {e}")
            return False

    def execute_demonstration_plan(self, plan: List[Dict]) -> bool:
        """
        Execute a demonstration plan with element interactions and voice narration.
        
        Args:
            plan: List of action dictionaries
            
        Returns:
            True if all actions executed successfully, False otherwise
        """
        logger.info(f"Executing demonstration plan with {len(plan)} steps")
        
        success = True
        for i, step in enumerate(plan):
            try:
                step_type = step.get('type')
                logger.info(f"Step {i+1}/{len(plan)}: {step_type}")
                
                if step_type == 'element_interaction':
                    action = step.get('action')
                    if action == 'click':
                        element_selector = step.get('element_selector')
                        if element_selector:
                            if not self.click_element(element_selector):
                                logger.error(f"Failed to click element: {element_selector}")
                                success = False
                        else:
                            logger.error(f"No element_selector provided for click action in step {i+1}")
                            success = False
                    elif action == 'type':
                        value = step.get('value', '')
                        if not self.type_text(value):
                            logger.error(f"Failed to type text: {value}")
                            success = False
                    else:
                        logger.warning(f"Unknown action type: {action}")
                        
                elif step_type == 'voice':
                    # Voice handling would be implemented by the calling module
                    content = step.get('content', '')
                    logger.info(f"Voice step: {content[:50]}...")
                    
                else:
                    logger.warning(f"Unknown step type: {step_type}")
                
                # Handle timing
                timing = step.get('timing')
                if timing == 'pause':
                    pause_duration = step.get('duration', 1.0)
                    time.sleep(pause_duration)
                    
            except Exception as e:
                logger.error(f"Error executing step {i+1}: {e}")
                success = False
                
        logger.info(f"Demonstration plan execution completed. Success: {success}")
        return success

    def _move_mouse_curved(self, end_x: int, end_y: int, duration: float) -> None:
        """
        Move mouse using a curved path for natural movement.
        
        Args:
            end_x, end_y: Target coordinates
            duration: Duration for the movement
        """
        try:
            start_x, start_y = pyautogui.position()
            path = self._generate_curved_path(start_x, start_y, end_x, end_y, duration)
            
            point_delay = duration / len(path) if len(path) > 1 else 0
            
            for i, (x, y) in enumerate(path):
                pyautogui.moveTo(x, y)
                if i < len(path) - 1:
                    # Add slight random variation
                    delay_variation = random.uniform(0.8, 1.2)
                    time.sleep(point_delay * delay_variation)
                    
        except Exception as e:
            logger.error(f"Error during curved mouse movement: {e}")
            # Fallback to direct movement
            pyautogui.moveTo(end_x, end_y, duration=duration)

    def _generate_curved_path(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                             duration: float, curve_intensity: float = DEFAULT_CURVE_INTENSITY) -> List[Tuple[int, int]]:
        """
        Generate a curved path between two points.
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            duration: Duration for movement (affects number of points)
            curve_intensity: How curved the path should be
            
        Returns:
            List of (x, y) coordinate tuples
        """
        num_points = max(10, int(duration * 20))  # More points for longer durations
        
        if num_points < 2:
            return [(start_x, start_y), (end_x, end_y)]
        
        path = []
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Create control point for curve
        mid_x = start_x + dx / 2
        mid_y = start_y + dy / 2
        
        curve_direction = random.choice([-1, 1])
        
        if distance > 0:
            perp_x = -dy / distance
            perp_y = dx / distance
            
            curve_offset = curve_intensity * distance * 0.2 * curve_direction
            control_x = mid_x + perp_x * curve_offset
            control_y = mid_y + perp_y * curve_offset
        else:
            control_x, control_y = mid_x, mid_y
        
        # Generate Bezier curve points
        for i in range(num_points):
            t = i / (num_points - 1)
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
            path.append((int(x), int(y)))
        
        return path

    def _add_random_delay(self, base_delay: float, variation: float = 0.3) -> float:
        """
        Add random variation to delay for more human-like timing.
        
        Args:
            base_delay: Base delay time
            variation: Percentage variation
            
        Returns:
            Randomized delay time
        """
        min_delay = base_delay * (1 - variation)
        max_delay = base_delay * (1 + variation)
        return random.uniform(min_delay, max_delay)


# Example usage
if __name__ == '__main__':
    import logging
    from ..services.browser_service import BrowserService
    from ..utils.config import config
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    print("--- Testing MouseService ---")
    print("This will open a browser and test element clicking")
    print("Make sure to have the calculator website accessible")
    
    try:
        with BrowserService() as browser_service:
            mouse_service = MouseService(browser_service)
            
            print("\nTesting element detection and clicking...")
            
            # Test clicking a button by text
            success = mouse_service.click_element_by_text("1", "button")
            if success:
                print("Successfully clicked '1' button")
            else:
                print("Failed to click '1' button")
            
            # Test clicking another button
            success = mouse_service.click_element_by_text("+", "button")
            if success:
                print("Successfully clicked '+' button")
            else:
                print("Failed to click '+' button")
                
            print("\nMouseService test completed")
            
    except Exception as e:
        print(f"Error during MouseService test: {e}") 