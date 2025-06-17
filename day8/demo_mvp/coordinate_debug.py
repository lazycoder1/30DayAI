#!/usr/bin/env python3

"""
Coordinate debugging script to help visualize and adjust coordinate accuracy.
"""

import time
import logging
from src.services.browser_service import BrowserService
from src.services.mouse_service import MouseService
from src.utils import helpers, config

def debug_coordinate_accuracy():
    """Debug coordinate calculations with detailed visual feedback."""
    
    helpers.setup_logging()
    logger = logging.getLogger("coordinate_debug")
    
    print("🔧 Coordinate Accuracy Debugging")
    print("=" * 50)
    
    try:
        # Initialize services
        browser_service = BrowserService()
        
        if not browser_service.page or browser_service.page.is_closed():
            print("❌ Failed to initialize browser")
            return
            
        mouse_service = MouseService(browser_service)
        
        # Test specific elements with detailed feedback
        test_elements = [
            ("button.btn-number:has-text('5')", "Number 5 (center button)"),
            ("button.btn-number:has-text('1')", "Number 1 (bottom row)"),
            ("button.btn-operator:has-text('+')", "Plus operator"),
            ("button.btn-operator:has-text('=')", "Equals button")
        ]
        
        print("📏 COORDINATE ANALYSIS")
        print("-" * 40)
        
        for selector, description in test_elements:
            print(f"\n🎯 Testing: {description}")
            print(f"Selector: {selector}")
            
            # Get element info
            element_info = browser_service.find_element_by_selector(selector)
            if not element_info:
                print(f"❌ Could not find element: {selector}")
                continue
                
            # Get screen coordinates
            screen_x, screen_y = browser_service.calculate_screen_coordinates(element_info, force_refresh=True)
            
            # Get browser position for reference
            browser_bounds = browser_service.get_browser_window_position()
            
            print(f"📍 Element Details:")
            print(f"  Page coordinates: ({element_info['center_x']:.0f}, {element_info['center_y']:.0f})")
            print(f"  Element size: {element_info['width']:.0f}x{element_info['height']:.0f}")
            print(f"  Screen coordinates: ({screen_x}, {screen_y})")
            print(f"  Browser position: ({browser_bounds.get('x', 'unknown')}, {browser_bounds.get('y', 'unknown')})")
            
            # Ask user if they want to test click
            response = input(f"Test click on {description}? (y/n/s for skip all): ").lower().strip()
            
            if response == 's':
                break
            elif response == 'y':
                print(f"🖱️  Clicking {description}...")
                print("👀 Watch carefully where the click happens!")
                
                # Add a countdown so user can watch
                for i in range(3, 0, -1):
                    print(f"   Clicking in {i}...")
                    time.sleep(1)
                
                success = mouse_service.click_element(selector, duration=1.0, force_refresh_position=True)
                
                if success:
                    print("✅ Click executed")
                else:
                    print("❌ Click failed")
                
                # Get user feedback on accuracy
                feedback = input("How was the click accuracy? (p=perfect, h=too high, l=too low, left=too left, right=too right): ").lower().strip()
                
                if feedback == 'p':
                    print("🎉 Perfect! This coordinate is accurate.")
                elif feedback == 'h':
                    print("⬆️  Click was too HIGH - need to reduce chrome height")
                    print(f"   Current total chrome height: likely around {115 - 15 + config.browser_chrome_height_offset}px")
                    print(f"   Try reducing BROWSER_CHROME_HEIGHT_OFFSET in .env")
                elif feedback == 'l':
                    print("⬇️  Click was too LOW - need to increase chrome height")
                    print(f"   Current total chrome height: likely around {115 - 15 + config.browser_chrome_height_offset}px")
                    print(f"   Try increasing BROWSER_CHROME_HEIGHT_OFFSET in .env")
                elif feedback == 'left':
                    print("⬅️  Click was too LEFT - browser X position issue")
                elif feedback == 'right':
                    print("➡️  Click was too RIGHT - browser X position issue")
                else:
                    print("📝 Thanks for the feedback")
        
        # Provide configuration suggestions
        print(f"\n🛠️  CONFIGURATION SUGGESTIONS")
        print("-" * 40)
        print(f"Current config:")
        print(f"  BROWSER_CHROME_HEIGHT_OFFSET: {config.browser_chrome_height_offset}px")
        print(f"  ENABLE_DYNAMIC_CHROME_CALCULATION: {config.enable_dynamic_chrome_calculation}")
        
        print(f"\nIf clicks are consistently:")
        print(f"  📍 TOO HIGH: Add to .env -> BROWSER_CHROME_HEIGHT_OFFSET=20")
        print(f"  📍 TOO LOW: Add to .env -> BROWSER_CHROME_HEIGHT_OFFSET=60") 
        print(f"  📍 PERFECT: No changes needed!")
        
        print(f"\nFor fine-tuning, adjust BROWSER_CHROME_HEIGHT_OFFSET in 5px increments.")
        
        # Test the actual problem case
        print(f"\n🧪 TESTING THE REPORTED ISSUE")
        print("-" * 40)
        print("Testing the specific case where clicks happen 15px below buttons...")
        
        response = input("Test the '5' button click that was reported as 15px low? (y/n): ").lower().strip()
        if response == 'y':
            print("🎯 Testing button '5' with current settings...")
            print("👀 Watch to see if click is still 15px below the button!")
            
            time.sleep(2)
            success = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
            
            if success:
                feedback = input("Was this click accurate now? (y/n): ").lower().strip()
                if feedback == 'y':
                    print("✅ Great! The coordinate fix is working.")
                else:
                    print("❌ Still needs adjustment. Try modifying BROWSER_CHROME_HEIGHT_OFFSET in .env")
            else:
                print("❌ Click failed")
        
        browser_service.close()
        
    except Exception as e:
        logger.error(f"Error during coordinate debugging: {e}")
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_coordinate_accuracy() 