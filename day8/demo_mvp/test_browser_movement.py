#!/usr/bin/env python3

"""
Test script to verify coordinate calculations work correctly when browser window is moved.
"""

import time
import logging
from src.services.browser_service import BrowserService
from src.services.mouse_service import MouseService
from src.utils import helpers

def test_browser_movement_handling():
    """Test coordinate accuracy when browser window is moved."""
    
    helpers.setup_logging()
    logger = logging.getLogger("browser_movement_test")
    
    print("🧪 Testing Browser Window Movement Handling")
    print("=" * 50)
    
    try:
        # Initialize services
        print("🔄 Initializing browser service...")
        browser_service = BrowserService()
        
        if not browser_service.page or browser_service.page.is_closed():
            print("❌ Failed to initialize browser")
            return
            
        print("✅ Browser initialized successfully")
        
        mouse_service = MouseService(browser_service)
        print("✅ Mouse service initialized")
        
        # Wait for user to observe initial position
        print("\n📍 INITIAL BROWSER POSITION TEST")
        print("-" * 40)
        input("Press Enter to test clicking on the '5' button at current position...")
        
        # Test initial position
        success1 = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
        if success1:
            print("✅ First click succeeded")
        else:
            print("❌ First click failed")
        
        # Prompt user to move browser
        print("\n🖱️  BROWSER MOVEMENT TEST")
        print("-" * 40)
        print("Now, please MOVE the browser window to a different position on your screen.")
        print("You can drag it by the title bar or use window management.")
        input("After moving the browser, press Enter to test coordinate recalculation...")
        
        # Test after movement with force refresh
        print("🎯 Testing click after browser movement (with position refresh)...")
        success2 = mouse_service.click_element(
            "button.btn-number:has-text('5')", 
            duration=1.5, 
            force_refresh_position=True  # This should handle the moved window
        )
        
        if success2:
            print("✅ Click after movement succeeded!")
            print("🎉 Coordinate recalculation is working correctly.")
        else:
            print("❌ Click after movement failed")
            print("🔧 The coordinate system may need further adjustment.")
        
        # Test without force refresh for comparison
        print("\n🧪 COMPARISON TEST (without position refresh)")
        print("-" * 40)
        input("Press Enter to test clicking WITHOUT position refresh...")
        
        success3 = mouse_service.click_element(
            "button.btn-number:has-text('1')", 
            duration=1.5, 
            force_refresh_position=False  # This might fail if window was moved
        )
        
        if success3:
            print("✅ Click without refresh also succeeded")
        else:
            print("❌ Click without refresh failed (expected if window was moved significantly)")
        
        # Test multiple elements to verify consistency
        print("\n🎯 MULTI-ELEMENT CONSISTENCY TEST")
        print("-" * 40)
        test_buttons = [
            ("button.btn-number:has-text('2')", "number 2"),
            ("button.btn-operator:has-text('+')", "plus operator"),
            ("button.btn-number:has-text('3')", "number 3"),
            ("button.btn-operator:has-text('=')", "equals operator")
        ]
        
        for selector, description in test_buttons:
            print(f"Testing {description}...")
            success = mouse_service.click_element(selector, duration=1.0, force_refresh_position=True)
            if success:
                print(f"  ✅ {description} clicked successfully")
            else:
                print(f"  ❌ {description} click failed")
            time.sleep(0.5)  # Small delay between clicks
        
        print("\n📊 TEST SUMMARY")
        print("-" * 40)
        results = [success1, success2, success3]
        successful_clicks = sum(results)
        
        print(f"Initial position click: {'✅' if success1 else '❌'}")
        print(f"After movement (with refresh): {'✅' if success2 else '❌'}")
        print(f"After movement (without refresh): {'✅' if success3 else '❌'}")
        print(f"\nTotal successful clicks: {successful_clicks}/3")
        
        if success2:  # Most important test
            print("\n🎉 SUCCESS: Browser movement handling is working!")
            print("The coordinate system correctly adapts to window movement.")
        else:
            print("\n⚠️  ISSUE: Browser movement handling needs improvement.")
            print("Consider adjusting chrome height calculations or position detection.")
        
        # Close browser
        browser_service.close()
        
    except Exception as e:
        logger.error(f"Error during browser movement test: {e}")
        print(f"❌ Test failed with error: {e}")
        return

if __name__ == "__main__":
    test_browser_movement_handling() 