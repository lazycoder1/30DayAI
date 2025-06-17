#!/usr/bin/env python3

"""
Test script to verify coordinate calculations work correctly when the page is scrolled.
"""

import time
import logging
from src.services.browser_service import BrowserService
from src.services.mouse_service import MouseService
from src.utils import helpers

def test_scroll_handling():
    """Test coordinate accuracy when page is scrolled."""
    
    helpers.setup_logging()
    logger = logging.getLogger("scroll_test")
    
    print("📜 Testing Page Scroll Handling")
    print("=" * 50)
    
    try:
        # Initialize services
        browser_service = BrowserService()
        
        if not browser_service.page or browser_service.page.is_closed():
            print("❌ Failed to initialize browser")
            return
            
        mouse_service = MouseService(browser_service)
        
        # Test 1: Click before any scrolling
        print("\n📍 TEST 1: NO SCROLL (baseline)")
        print("-" * 40)
        
        # Get initial scroll position
        scroll_info = browser_service.get_current_scroll_position()
        print(f"Initial scroll position: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
        
        input("Press Enter to test clicking '5' button with no scroll...")
        success1 = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
        print(f"No scroll click: {'✅ Success' if success1 else '❌ Failed'}")
        
        # Test 2: Scroll down and test
        print("\n📜 TEST 2: SCROLL DOWN")
        print("-" * 40)
        print("Scrolling page down...")
        
        # Scroll the page down
        browser_service.page.evaluate("window.scrollBy(0, 100)")
        time.sleep(0.5)  # Wait for scroll to complete
        
        # Get new scroll position
        scroll_info = browser_service.get_current_scroll_position()
        print(f"After scroll down: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
        
        input("Press Enter to test clicking '5' button after scrolling down...")
        success2 = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
        print(f"Scroll down click: {'✅ Success' if success2 else '❌ Failed'}")
        
        # Test 3: Scroll up and test
        print("\n📜 TEST 3: SCROLL UP")
        print("-" * 40)
        print("Scrolling page up...")
        
        # Scroll the page up (more than the original scroll)
        browser_service.page.evaluate("window.scrollBy(0, -150)")
        time.sleep(0.5)  # Wait for scroll to complete
        
        # Get new scroll position
        scroll_info = browser_service.get_current_scroll_position()
        print(f"After scroll up: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
        
        input("Press Enter to test clicking '5' button after scrolling up...")
        success3 = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
        print(f"Scroll up click: {'✅ Success' if success3 else '❌ Failed'}")
        
        # Test 4: Reset scroll and test different elements
        print("\n📜 TEST 4: RESET AND MULTI-ELEMENT TEST")
        print("-" * 40)
        print("Resetting scroll to top...")
        
        # Reset scroll to top
        browser_service.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        
        scroll_info = browser_service.get_current_scroll_position()
        print(f"After reset: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
        
        # Test multiple elements after scroll reset
        test_elements = [
            ("button.btn-number:has-text('1')", "Number 1"),
            ("button.btn-operator:has-text('+')", "Plus operator"),
            ("button.btn-number:has-text('2')", "Number 2"),
            ("button.btn-operator:has-text('=')", "Equals")
        ]
        
        print("\nTesting multiple elements after scroll reset...")
        for selector, description in test_elements:
            print(f"Testing {description}...")
            success = mouse_service.click_element(selector, duration=0.8)
            if success:
                print(f"  ✅ {description} clicked successfully")
            else:
                print(f"  ❌ {description} click failed")
            time.sleep(0.3)  # Small delay between clicks
        
        # Test 5: Horizontal scroll (if possible)
        print("\n📜 TEST 5: HORIZONTAL SCROLL TEST")
        print("-" * 40)
        
        # Try horizontal scroll (might not work if page doesn't have horizontal scroll)
        browser_service.page.evaluate("window.scrollBy(50, 0)")
        time.sleep(0.5)
        
        scroll_info = browser_service.get_current_scroll_position()
        print(f"After horizontal scroll: X={scroll_info['scrollX']}, Y={scroll_info['scrollY']}")
        
        if scroll_info['scrollX'] > 0:
            input("Press Enter to test clicking after horizontal scroll...")
            success5 = mouse_service.click_element("button.btn-number:has-text('5')", duration=1.5)
            print(f"Horizontal scroll click: {'✅ Success' if success5 else '❌ Failed'}")
        else:
            print("No horizontal scroll available on this page")
        
        # Summary
        print(f"\n📊 SCROLL TEST SUMMARY")
        print("-" * 40)
        results = [success1, success2, success3]
        successful_tests = sum(results)
        
        print(f"No scroll: {'✅' if success1 else '❌'}")
        print(f"Scroll down: {'✅' if success2 else '❌'}")
        print(f"Scroll up: {'✅' if success3 else '❌'}")
        print(f"\nSuccessful scroll tests: {successful_tests}/3")
        
        if successful_tests == 3:
            print("\n🎉 SUCCESS: Scroll handling is working perfectly!")
            print("The coordinate system correctly accounts for page scrolling.")
        elif successful_tests >= 2:
            print("\n⚠️  PARTIAL SUCCESS: Most scroll tests passed.")
            print("Minor scroll handling issues may need attention.")
        else:
            print("\n❌ SCROLL HANDLING NEEDS WORK")
            print("Coordinate calculations are not properly accounting for scroll.")
        
        # Reset scroll for cleanup
        browser_service.page.evaluate("window.scrollTo(0, 0)")
        browser_service.close()
        
    except Exception as e:
        logger.error(f"Error during scroll test: {e}")
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_scroll_handling() 