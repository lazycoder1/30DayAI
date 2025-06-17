#!/usr/bin/env python3

"""
Coordinate Calibration Test Script

This script helps debug and calibrate mouse coordinate calculations
by testing the browser service coordinate calculation methods.

Run this script using: rye run python -m coordinate_test
"""

import sys
import os
import logging
import json

def test_coordinate_calibration():
    """Test coordinate calculation and provide calibration information."""
    
    # Import here to avoid module-level import issues
    from src.services.browser_service import BrowserService
    from src.services.mouse_service import MouseService
    from src.utils import config, helpers
    
    helpers.setup_logging()
    logger = logging.getLogger("coordinate_test")
    
    print("🧪 Starting Coordinate Calibration Test")
    print("=" * 50)
    
    try:
        # Create browser service but handle timeout issues
        browser_service = BrowserService()
        
        # Check if page loaded successfully
        if not browser_service.page or browser_service.page.is_closed():
            print("❌ Failed to initialize browser or page is closed")
            print("🔄 This might be due to network timeout or website being slow")
            print("💡 Try running the main application instead: rye run python -m src.main")
            return
        
        print(f"✅ Browser initialized: {browser_service.page.url}")
        
        # Wait a bit more for page to fully load
        print("⏳ Waiting for page to fully load...")
        try:
            browser_service.page.wait_for_load_state('networkidle', timeout=10000)  # 10 seconds
            print("✅ Page loaded successfully")
        except Exception as e:
            print(f"⚠️ Page load warning: {e}")
            print("🔄 Continuing with current page state...")
        
        # Run calibration test
        print("\n🔍 Running coordinate calibration...")
        calibration = browser_service.calibrate_coordinates()
        
        if "error" in calibration:
            print(f"❌ Calibration failed: {calibration['error']}")
            print("💡 Try running a basic test first:")
            print("   rye run python -m src.main")
            print("   Then type: 'show me 1 + 1'")
            return
        
        # Display calibration results
        print("\n📊 CALIBRATION RESULTS:")
        print("-" * 30)
        print(f"Test Element: {calibration['test_element']}")
        print(f"Page Coordinates: ({calibration['element_page_coords']['x']:.0f}, {calibration['element_page_coords']['y']:.0f})")
        print(f"Screen Coordinates: ({calibration['calculated_screen_coords']['x']}, {calibration['calculated_screen_coords']['y']})")
        print(f"Chrome Height Used: {calibration['chrome_height_calculated']}px")
        print(f"Device Pixel Ratio: {calibration['viewport_info']['devicePixelRatio']}")
        
        print(f"\n🖥️  Browser Window Info:")
        print(f"  Position: ({calibration['browser_window']['x']}, {calibration['browser_window']['y']})")
        print(f"  Viewport: {calibration['viewport_info']['viewportWidth']}x{calibration['viewport_info']['viewportHeight']}")
        print(f"  Window: {calibration['viewport_info']['windowWidth']}x{calibration['viewport_info']['windowHeight']}")
        
        # Test a few different elements
        test_elements = [
            "button.btn-number:has-text('1')",
            "button.btn-operator:has-text('+')",
            "button.btn-operator:has-text('=')",
            "button.btn-operator:has-text('CE/C')"
        ]
        
        print(f"\n🎯 Testing Multiple Elements:")
        print("-" * 30)
        
        for selector in test_elements:
            element_info = browser_service.find_element_by_selector(selector)
            if element_info:
                screen_coords = browser_service.calculate_screen_coordinates(element_info)
                print(f"  {selector[:30]:30} -> Page({element_info['center_x']:.0f}, {element_info['center_y']:.0f}) Screen{screen_coords}")
            else:
                print(f"  {selector[:30]:30} -> ❌ Not found")
        
        # Provide adjustment suggestions
        print(f"\n💡 TROUBLESHOOTING SUGGESTIONS:")
        print("-" * 30)
        print("If clicks are happening:")
        print("  📍 TOO LOW (below buttons): Reduce BROWSER_CHROME_HEIGHT_OFFSET in .env")
        print("  📍 TOO HIGH (above buttons): Increase BROWSER_CHROME_HEIGHT_OFFSET in .env") 
        print("  📍 TOO LEFT/RIGHT: Check window position calculation")
        print(f"\nCurrent chrome offset: {calibration['config_settings']['chrome_height_offset']}px")
        print(f"Dynamic calculation: {calibration['config_settings']['dynamic_chrome_calculation']}")
        
        # Interactive test option
        print(f"\n🖱️  INTERACTIVE TEST:")
        print("You can now run a demonstration to see if coordinates are accurate.")
        print("Watch where the mouse clicks relative to the calculator buttons.")
        
        response = input("\nDo you want to test a mouse click? (y/n): ").lower().strip()
        if response == 'y':
            # Initialize mouse service and test
            mouse_service = MouseService(browser_service)
            print("\n🔄 Testing mouse click on number '5' button...")
            print("Watch your screen to see where the click happens!")
            
            import time
            time.sleep(2)  # Give user time to watch
            
            success = mouse_service.click_element("button.btn-number:has-text('5')")
            if success:
                print("✅ Click executed! Did it hit the button correctly?")
                print("\n📝 Adjustment Guide:")
                print("  - If click was TOO LOW: Add this to .env -> BROWSER_CHROME_HEIGHT_OFFSET=20")
                print("  - If click was TOO HIGH: Add this to .env -> BROWSER_CHROME_HEIGHT_OFFSET=50")
                print("  - If click was PERFECT: No changes needed!")
            else:
                print("❌ Click failed")
        
        # Close browser
        browser_service.close()
        
    except Exception as e:
        logger.error(f"Error during coordinate test: {e}")
        print(f"❌ Test failed: {e}")
        print("\n🔄 Alternative approach:")
        print("1. Run the main application: rye run python -m src.main")
        print("2. Try a demonstration: 'show me 1 + 1'")
        print("3. Watch where the mouse clicks to see if coordinates are accurate")
        return

if __name__ == "__main__":
    test_coordinate_calibration() 