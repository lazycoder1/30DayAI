# Browser service (Playwright) 
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
import logging
import asyncio
from typing import Optional, Dict, Tuple, List
from ..utils.config import config # Import the AppConfig instance

logger = logging.getLogger(__name__)

class BrowserService:
    """
    A service class to manage browser interactions using Playwright.
    Handles launching the browser, opening pages, fetching content, and calculating
    precise element coordinates for PyAutoGUI mouse control.
    """
    def __init__(self, base_url: Optional[str] = None):
        """
        Initializes the BrowserService.
        Uses CALCULATOR_URL from AppConfig by default, but can be overridden.

        Args:
            base_url: The base URL to navigate to upon page creation. Overrides config if provided.
        """
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.base_url: str = base_url if base_url is not None else config.calculator_url
        self._initialize_browser()

    def _initialize_browser(self):
        """Starts Playwright and launches a browser instance (Chromium by default)."""
        try:
            self.playwright = sync_playwright().start()
            # Launch browser with settings for visibility and slower operations
            self.browser = self.playwright.chromium.launch(
                headless=False,
                slow_mo=500,  # 500ms delay between actions for visibility
            )
            logger.info(f"Playwright started and browser launched. Target URL: {self.base_url}")
            self.page = self.navigate_to_url(self.base_url) # Open initial page
            
            # Bring browser to front and try additional load waiting
            if self.page:
                self.page.bring_to_front()
                try:
                    self.page.wait_for_load_state('networkidle', timeout=10000)  # 10 seconds
                    logger.info("Browser brought to front and page fully loaded")
                except Exception as wait_error:
                    logger.warning(f"Page load wait timeout, but continuing: {wait_error}")
                    logger.info("Browser is ready even if not fully loaded")
            else:
                logger.warning("Page navigation failed, but browser is still available")
        except Exception as e:
            logger.error(f"Error initializing browser: {e}")
            self.close()
            raise

    def navigate_to_url(self, url: str) -> Optional[Page]:
        """
        Navigates the current page to the specified URL or opens a new page if none exists.

        Args:
            url: The URL to navigate to.

        Returns:
            The Page object after navigation, or None if an error occurs.
        """
        if not self.browser:
            logger.error("Browser not initialized. Cannot navigate.")
            return None
        try:
            if self.page and not self.page.is_closed():
                logger.info(f"Attempting to navigate to URL: {url}")
                self.page.goto(url, timeout=30000)  # Reduced to 30 seconds
                # Try to wait for network idle, but don't fail if it times out
                try:
                    self.page.wait_for_load_state('networkidle', timeout=15000)  # 15 seconds
                except Exception as wait_error:
                    logger.warning(f"Network idle timeout, but continuing: {wait_error}")
                    # Try to wait for basic load state instead
                    self.page.wait_for_load_state('load', timeout=5000)
                logger.info(f"Successfully navigated to URL: {url}")
            else:
                logger.info(f"Creating new page and navigating to URL: {url}")
                self.page = self.browser.new_page()
                self.page.goto(url, timeout=30000)  # Reduced to 30 seconds
                # Try to wait for network idle, but don't fail if it times out
                try:
                    self.page.wait_for_load_state('networkidle', timeout=15000)  # 15 seconds
                except Exception as wait_error:
                    logger.warning(f"Network idle timeout, but continuing: {wait_error}")
                    # Try to wait for basic load state instead
                    self.page.wait_for_load_state('load', timeout=5000)
                logger.info(f"New page created and successfully navigated to URL: {url}")
            return self.page
        except Exception as e:
            logger.error(f"Error navigating to URL '{url}': {e}")
            logger.info("You may need to check your internet connection or try again later.")
            return None

    def get_browser_window_position(self) -> Dict[str, int]:
        """
        Get the browser window position and scroll information via JavaScript.
        
        Returns:
            Dictionary with window positioning information
        """
        if not self.page or self.page.is_closed():
            logger.warning("No active page to get browser position from.")
            return {}
        
        try:
            browser_bounds = self.page.evaluate("""
                () => ({
                    x: window.screenX,
                    y: window.screenY,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY,
                    innerWidth: window.innerWidth,
                    innerHeight: window.innerHeight
                })
            """)
            logger.debug(f"Browser window position: {browser_bounds}")
            return browser_bounds
        except Exception as e:
            logger.error(f"Error getting browser window position: {e}")
            return {}

    def find_element_by_selector(self, selector: str) -> Optional[Dict[str, any]]:
        """
        Find an element using CSS selector and return its bounding box and other info.
        
        Args:
            selector: CSS selector string
            
        Returns:
            Dictionary with element info or None if not found
        """
        if not self.page or self.page.is_closed():
            logger.warning("No active page to find element on.")
            return None
            
        try:
            element = self.page.locator(selector)
            if element.count() > 0:
                # Get the first matching element's bounding box
                box = element.bounding_box()
                if box:
                    element_info = {
                        'selector': selector,
                        'x': box['x'],
                        'y': box['y'], 
                        'width': box['width'],
                        'height': box['height'],
                        'center_x': box['x'] + box['width'] / 2,
                        'center_y': box['y'] + box['height'] / 2
                    }
                    logger.debug(f"Found element with selector '{selector}': {element_info}")
                    return element_info
                else:
                    logger.warning(f"Element found but no bounding box available for selector: {selector}")
                    return None
            else:
                logger.warning(f"No element found with selector: {selector}")
                return None
        except Exception as e:
            logger.error(f"Error finding element with selector '{selector}': {e}")
            return None

    def find_element_by_text(self, text: str, element_type: str = "button") -> Optional[Dict[str, any]]:
        """
        Find an element by its text content.
        
        Args:
            text: Text content to search for
            element_type: Type of element to search (e.g., "button", "div", "*")
            
        Returns:
            Dictionary with element info or None if not found
        """
        if not self.page or self.page.is_closed():
            logger.warning("No active page to find element on.")
            return None
            
        try:
            # Use Playwright's text selector
            element = self.page.locator(f"{element_type}:has-text('{text}')")
            if element.count() > 0:
                box = element.bounding_box()
                if box:
                    element_info = {
                        'text': text,
                        'element_type': element_type,
                        'x': box['x'],
                        'y': box['y'],
                        'width': box['width'], 
                        'height': box['height'],
                        'center_x': box['x'] + box['width'] / 2,
                        'center_y': box['y'] + box['height'] / 2
                    }
                    logger.debug(f"Found element with text '{text}': {element_info}")
                    return element_info
                else:
                    logger.warning(f"Element with text '{text}' found but no bounding box available")
                    return None
            else:
                logger.warning(f"No {element_type} element found with text: {text}")
                return None
        except Exception as e:
            logger.error(f"Error finding element with text '{text}': {e}")
            return None

    def get_current_scroll_position(self) -> Dict[str, int]:
        """
        Get the current scroll position of the page.
        
        Returns:
            Dictionary with scrollX and scrollY values
        """
        if not self.page or self.page.is_closed():
            logger.warning("No active page to get scroll position from.")
            return {'scrollX': 0, 'scrollY': 0}
        
        try:
            scroll_info = self.page.evaluate("""
                () => ({
                    scrollX: window.scrollX || window.pageXOffset || 0,
                    scrollY: window.scrollY || window.pageYOffset || 0,
                    maxScrollX: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
                    maxScrollY: Math.max(0, document.documentElement.scrollHeight - window.innerHeight)
                })
            """)
            logger.debug(f"Current scroll position: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
            return scroll_info
        except Exception as e:
            logger.error(f"Error getting scroll position: {e}")
            return {'scrollX': 0, 'scrollY': 0}

    def refresh_browser_position(self) -> bool:
        """
        Refresh and validate browser window position.
        Call this before coordinate calculations if you suspect the window has moved.
        
        Returns:
            True if position was successfully refreshed, False otherwise
        """
        try:
            if not self.page or self.page.is_closed():
                logger.warning("No active page to refresh position for.")
                return False
                
            # Get fresh browser position
            browser_bounds = self.get_browser_window_position()
            if not browser_bounds:
                logger.warning("Could not get current browser position")
                return False
                
            logger.info(f"Browser position refreshed: x={browser_bounds.get('x', 'unknown')}, "
                       f"y={browser_bounds.get('y', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing browser position: {e}")
            return False

    def calculate_screen_coordinates(self, element_info: Dict[str, any], force_refresh: bool = False) -> Tuple[int, int]:
        """
        Calculate absolute screen coordinates for an element.
        
        Args:
            element_info: Element information dict from find_element methods
            force_refresh: If True, ensure fresh browser position data
            
        Returns:
            Tuple of (screen_x, screen_y) coordinates
        """
        try:
            # Refresh browser position if requested (useful if window was moved)
            if force_refresh:
                self.refresh_browser_position()
                
            browser_bounds = self.get_browser_window_position()
            if not browser_bounds:
                logger.error("Could not get browser window position")
                return (0, 0)
            
            # Get viewport info with more stable calculation
            viewport_info = self.page.evaluate("""
                () => ({
                    viewportHeight: window.innerHeight,
                    windowHeight: window.outerHeight,
                    viewportWidth: window.innerWidth,
                    windowWidth: window.outerWidth,
                    scrollX: window.scrollX || window.pageXOffset || 0,
                    scrollY: window.scrollY || window.pageYOffset || 0,
                    screenX: window.screenX,
                    screenY: window.screenY,
                    devicePixelRatio: window.devicePixelRatio || 1
                })
            """)
            
            # Validate that JavaScript window position matches our browser_bounds
            js_x = viewport_info.get('screenX', browser_bounds['x'])
            js_y = viewport_info.get('screenY', browser_bounds['y'])
            
            if abs(js_x - browser_bounds['x']) > 5 or abs(js_y - browser_bounds['y']) > 5:
                logger.warning(f"Position mismatch detected - Browser bounds: ({browser_bounds['x']}, {browser_bounds['y']}) "
                             f"vs JS coords: ({js_x}, {js_y}). Using JS coordinates.")
                browser_bounds['x'] = js_x
                browser_bounds['y'] = js_y
            
            if config.enable_dynamic_chrome_calculation:
                # Chrome height calculation with validation
                calculated_chrome = viewport_info['windowHeight'] - viewport_info['viewportHeight']
                
                # CRITICAL FIX: Adjust chrome height calculation for better accuracy
                # The calculated chrome includes the title bar but we need to account for 
                # the difference between window.screenY (which includes title bar) and 
                # the actual content area
                adjusted_chrome = calculated_chrome - 25  # Increased adjustment for better accuracy
                
                # Validate chrome height is reasonable 
                if adjusted_chrome < 10 or adjusted_chrome > 180:
                    logger.warning(f"Unusual adjusted chrome height: {adjusted_chrome}px, using fallback")
                    adjusted_chrome = 70  # Increased fallback value
                    
                total_chrome_height = adjusted_chrome + config.browser_chrome_height_offset
                chrome_calculation_method = f"dynamic(calc:{calculated_chrome}px, adj:{adjusted_chrome}px)"
                
                logger.info(f"Chrome height details - Raw calc: {calculated_chrome}px, "
                           f"Adjusted: {adjusted_chrome}px, Offset: {config.browser_chrome_height_offset}px, "
                           f"Total: {total_chrome_height}px")
            else:
                # Use fixed chrome height from config
                total_chrome_height = config.browser_chrome_height_offset
                chrome_calculation_method = "fixed"
            
            # Calculate absolute screen coordinates
            # CRITICAL: Properly handle page scrolling by accounting for scroll offsets
            scroll_x = viewport_info.get('scrollX', 0)
            scroll_y = viewport_info.get('scrollY', 0)
            
            # FIXED: Add scroll offsets instead of subtracting them
            screen_x = browser_bounds['x'] + element_info['center_x'] + scroll_x
            screen_y = browser_bounds['y'] + element_info['center_y'] + total_chrome_height + scroll_y
            
            # Log scroll information for debugging
            if scroll_x != 0 or scroll_y != 0:
                logger.info(f"Page scroll detected - X: {scroll_x}px, Y: {scroll_y}px")
                logger.info(f"Adjusting coordinates for scroll offset")
            
            # Apply device pixel ratio if needed (for high DPI displays)
            pixel_ratio = viewport_info.get('devicePixelRatio', 1)
            if pixel_ratio != 1:
                logger.debug(f"Device pixel ratio: {pixel_ratio}")
                # Note: Usually screen coordinates don't need pixel ratio adjustment, 
                # but worth logging for debugging
            
            logger.info(f"Calculated screen coordinates: ({screen_x:.0f}, {screen_y:.0f}) "
                       f"for element at page coordinates ({element_info['center_x']:.0f}, {element_info['center_y']:.0f}) "
                       f"with chrome height: {total_chrome_height}px ({chrome_calculation_method}) "
                       f"scroll: ({scroll_x}, {scroll_y})")
            
            return (int(screen_x), int(screen_y))
        except Exception as e:
            logger.error(f"Error calculating screen coordinates: {e}")
            # Fallback to simple calculation with reduced chrome height
            browser_bounds = self.get_browser_window_position()
            if browser_bounds:
                fallback_chrome = 35  # Further reduced fallback chrome height
                screen_x = browser_bounds['x'] + element_info['center_x']
                screen_y = browser_bounds['y'] + element_info['center_y'] + fallback_chrome
                logger.warning(f"Using fallback coordinates: ({screen_x}, {screen_y}) with chrome height: {fallback_chrome}px")
                return (int(screen_x), int(screen_y))
            return (0, 0)

    def find_calculator_elements(self) -> Dict[str, Dict[str, any]]:
        """
        Find common calculator elements and return their information.
        
        Returns:
            Dictionary mapping element names to their info
        """
        elements = {}
        
        # Common calculator button selectors to try
        # Updated to be more specific and avoid strict mode violations
        common_buttons = {
            '0': ['button.btn-number:has-text("0")', 'button:has-text("0"):not(:has-text("N/A"))'],
            '1': ['button.btn-number:has-text("1")', 'button:has-text("1"):not(:has-text("/"))'], 
            '2': ['button.btn-number:has-text("2")', 'button:has-text("2"):not(:has-text("ND"))'],
            '3': ['button.btn-number:has-text("3")', '[data-key="3"]', '.btn-3'],
            '4': ['button.btn-number:has-text("4")', '[data-key="4"]', '.btn-4'],
            '5': ['button.btn-number:has-text("5")', '[data-key="5"]', '.btn-5'],
            '6': ['button.btn-number:has-text("6")', '[data-key="6"]', '.btn-6'],
            '7': ['button.btn-number:has-text("7")', '[data-key="7"]', '.btn-7'],
            '8': ['button.btn-number:has-text("8")', '[data-key="8"]', '.btn-8'],
            '9': ['button.btn-number:has-text("9")', '[data-key="9"]', '.btn-9'],
            '+': ['button.btn-operator:has-text("+")', 'button:has-text("+"):not(:has-text("/-"))'],
            '-': ['button.btn-operator:has-text("-")', 'button:has-text("-"):not(:has-text("/-"))'],
            '*': ['button.btn-operator:has-text("×")', 'button.btn-operator:has-text("*")', '[data-key="*"]'],
            '/': ['button.btn-operator:has-text("÷")', 'button.btn-operator:has-text("/")', '[data-key="/"]'],
            '=': ['button.btn-operator:has-text("=")', '[data-key="="]', '.btn-equals'],
            'C': ['button.btn-operator:has-text("CE/C")', 'button:has-text("CE/C")'],
            'CE': ['button:has-text("CE/C")', '[data-key="CE"]', '.btn-clear-entry'],
            'CF': ['button.btn-function:has-text("CF")', '[data-key="CF"]'],
            'NPV': ['button.btn-function:has-text("NPV")', '[data-key="NPV"]'],
            'IRR': ['button.btn-function:has-text("IRR")', '[data-key="IRR"]'],
            'ENTER': ['button.btn-operator:has-text("CPT")', 'button:has-text("CPT")'],
            'CPT': ['button.btn-operator:has-text("CPT")', 'button:has-text("CPT")']
        }
        
        for button_name, selectors in common_buttons.items():
            for selector in selectors:
                element_info = self.find_element_by_selector(selector)
                if element_info:
                    # Add the selector that worked to the element_info
                    element_info['selector'] = selector
                    elements[button_name] = element_info
                    logger.debug(f"Found calculator button '{button_name}' with selector '{selector}'")
                    break
            else:
                logger.debug(f"Could not find calculator button '{button_name}' with any selector")
        
        logger.info(f"Found {len(elements)} calculator elements")
        return elements

    def get_current_page_html(self) -> Optional[str]:
        """
        Fetches the full HTML content of the current page.

        Returns:
            The HTML content as a string, or None if an error occurs or no page is active.
        """
        if self.page and not self.page.is_closed():
            try:
                html_content = self.page.content()
                logger.info(f"Fetched HTML content from: {self.page.url}")
                return html_content
            except Exception as e:
                logger.error(f"Error fetching HTML content: {e}")
                return None
        else:
            logger.warning("No active page to get HTML from.")
            return None

    def get_current_page(self) -> Optional[Page]:
        """Returns the current active page."""
        if self.page and not self.page.is_closed():
            return self.page
        logger.warning("No active page available.")
        return None

    def close(self):
        """Closes the browser and stops Playwright."""
        if self.browser:
            try:
                self.browser.close()
                logger.info("Browser closed.")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            self.browser = None
        
        if self.playwright:
            try:
                self.playwright.stop()
                logger.info("Playwright stopped.")
            except Exception as e:
                logger.error(f"Error stopping Playwright: {e}")
            self.playwright = None

    def __enter__(self):
        """Allows the service to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures resources are cleaned up when exiting context manager."""
        self.close()

    def calibrate_coordinates(self, test_element_selector: str = "button.btn-number:has-text('5')") -> Dict[str, any]:
        """
        Test coordinate accuracy by finding an element and providing calibration info.
        This helps debug coordinate calculation issues.
        
        Args:
            test_element_selector: CSS selector for an element to test with (default: number 5 button)
            
        Returns:
            Dictionary with calibration information
        """
        try:
            element_info = self.find_element_by_selector(test_element_selector)
            if not element_info:
                return {"error": f"Could not find test element: {test_element_selector}"}
            
            # Get all the coordinate information
            browser_bounds = self.get_browser_window_position()
            viewport_info = self.page.evaluate("""
                () => ({
                    viewportHeight: window.innerHeight,
                    windowHeight: window.outerHeight,
                    viewportWidth: window.innerWidth,
                    windowWidth: window.outerWidth,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY,
                    devicePixelRatio: window.devicePixelRatio
                })
            """)
            
            screen_coords = self.calculate_screen_coordinates(element_info)
            
            calibration_info = {
                "test_element": test_element_selector,
                "element_page_coords": {
                    "x": element_info['center_x'], 
                    "y": element_info['center_y']
                },
                "calculated_screen_coords": {
                    "x": screen_coords[0], 
                    "y": screen_coords[1]
                },
                "browser_window": browser_bounds,
                "viewport_info": viewport_info,
                "chrome_height_calculated": viewport_info['windowHeight'] - viewport_info['viewportHeight'] + config.browser_chrome_height_offset if config.enable_dynamic_chrome_calculation else config.browser_chrome_height_offset,
                "config_settings": {
                    "dynamic_chrome_calculation": config.enable_dynamic_chrome_calculation,
                    "chrome_height_offset": config.browser_chrome_height_offset
                },
                "suggestions": {
                    "if_clicking_too_low": f"Reduce BROWSER_CHROME_HEIGHT_OFFSET (currently {config.browser_chrome_height_offset}px)",
                    "if_clicking_too_high": f"Increase BROWSER_CHROME_HEIGHT_OFFSET (currently {config.browser_chrome_height_offset}px)",
                    "current_method": "dynamic" if config.enable_dynamic_chrome_calculation else "fixed"
                }
            }
            
            logger.info(f"Coordinate calibration for {test_element_selector}:")
            logger.info(f"  Page coords: ({element_info['center_x']:.0f}, {element_info['center_y']:.0f})")
            logger.info(f"  Screen coords: {screen_coords}")
            logger.info(f"  Chrome height: {calibration_info['chrome_height_calculated']}px")
            logger.info(f"  Device pixel ratio: {viewport_info['devicePixelRatio']}")
            
            return calibration_info
            
        except Exception as e:
            logger.error(f"Error during coordinate calibration: {e}")
            return {"error": str(e)}

    def get_element_coordinates(self, element_selector: str) -> Optional[Dict[str, int]]:
        """
        Get the screen coordinates for an element using its selector.
        
        Args:
            element_selector: CSS selector or XPath for the element
            
        Returns:
            Dictionary with x, y coordinates or None if element not found
        """
        try:
            # Find the element using the selector
            element = self.page.locator(element_selector).first
            if not element:
                logger.error(f"Element not found with selector: {element_selector}")
                return None

            # Get element bounding box
            bbox = element.bounding_box()
            if not bbox:
                logger.error(f"Could not get bounding box for element: {element_selector}")
                return None

            # Format element info for calculate_screen_coordinates
            element_info = {
                'center_x': bbox['x'] + bbox['width'] / 2,
                'center_y': bbox['y'] + bbox['height'] / 2,
                'width': bbox['width'],
                'height': bbox['height']
            }

            # Calculate screen coordinates
            screen_x, screen_y = self.calculate_screen_coordinates(element_info)
            if not screen_x or not screen_y:
                logger.error(f"Could not calculate screen coordinates for element: {element_selector}")
                return None

            logger.debug(f"Element coordinates for {element_selector}: ({screen_x}, {screen_y})")
            return {'x': screen_x, 'y': screen_y}

        except Exception as e:
            logger.error(f"Error getting element coordinates: {e}")
            return None

# Example usage (for testing purposes)
if __name__ == '__main__':
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=config.log_level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    print("--- Testing Enhanced BrowserService ---")
    print(f"Target URL: {config.calculator_url}")
    
    try:
        with BrowserService() as browser_service:
            if browser_service.page:
                print(f"Successfully navigated to: {browser_service.page.url}")
                
                # Test element detection
                print("\nTesting element detection...")
                elements = browser_service.find_calculator_elements()
                
                if elements:
                    print(f"Found {len(elements)} calculator elements:")
                    for name, info in elements.items():
                        screen_coords = browser_service.calculate_screen_coordinates(info)
                        print(f"  {name}: Page({info['center_x']:.0f}, {info['center_y']:.0f}) -> Screen{screen_coords}")
                else:
                    print("No calculator elements found")
                
                # Test finding specific elements
                print("\nTesting specific element detection...")
                plus_button = browser_service.find_element_by_text("+", "button")
                if plus_button:
                    screen_coords = browser_service.calculate_screen_coordinates(plus_button)
                    print(f"Plus button: {screen_coords}")
                
            else:
                print("Failed to initialize page in BrowserService.")
                
    except Exception as e:
        print(f"An error occurred during BrowserService test: {e}")
    
    print("\nEnhanced BrowserService test finished.") 