#!/usr/bin/env python3
"""
Screenshot Capture Script

This script uses PIL ImageGrab to capture a screenshot and save it in the scripts folder.
"""

from PIL import ImageGrab
import time
from pathlib import Path

def capture_and_save_screenshot():
    """Capture screenshot using PIL and save it with timestamp."""
    
    # Get the scripts directory (where this script is located)
    scripts_dir = Path(__file__).parent
    
    # Create timestamp for filename
    timestamp = int(time.time())
    formatted_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    
    # Screenshot filename
    screenshot_path = scripts_dir / f"screenshot_{formatted_time}.png"
    
    print("📸 Taking screenshot...")
    print("Position your windows as needed - capturing in 3 seconds...")
    
    # Give user time to prepare
    for i in range(3, 0, -1):
        print(f"⏰ Capturing in {i}...")
        time.sleep(1)
    
    try:
        # Capture screenshot using PIL ImageGrab
        screenshot = ImageGrab.grab()
        
        # Save screenshot
        screenshot.save(screenshot_path)
        
        print(f"✅ Screenshot captured successfully!")
        print(f"📁 Saved to: {screenshot_path}")
        print(f"📏 Size: {screenshot.size}")
        print(f"💾 File size: {screenshot_path.stat().st_size / 1024:.1f} KB")
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Error capturing screenshot: {e}")
        return None

def capture_region_screenshot(x, y, width, height):
    """Capture a specific region of the screen."""
    
    scripts_dir = Path(__file__).parent
    formatted_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    screenshot_path = scripts_dir / f"region_screenshot_{formatted_time}.png"
    
    print(f"📸 Capturing region: ({x}, {y}) with size {width}x{height}")
    
    try:
        # Capture specific region
        # PIL ImageGrab uses (left, top, right, bottom) format
        region = (x, y, x + width, y + height)
        screenshot = ImageGrab.grab(bbox=region)
        
        # Save screenshot
        screenshot.save(screenshot_path)
        
        print(f"✅ Region screenshot captured!")
        print(f"📁 Saved to: {screenshot_path}")
        print(f"📏 Size: {screenshot.size}")
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Error capturing region screenshot: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("📷 PIL Screenshot Capture Tool")
    print("=" * 50)
    
    print("\nChoose an option:")
    print("1. Capture full screen")
    print("2. Capture region (you'll need to specify coordinates)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        result = capture_and_save_screenshot()
        if result:
            print(f"\n🎉 Success! Screenshot saved to scripts folder.")
        else:
            print(f"\n💥 Failed to capture screenshot.")
            
    elif choice == "2":
        try:
            print("\nEnter region coordinates:")
            x = int(input("X (left): "))
            y = int(input("Y (top): "))
            width = int(input("Width: "))
            height = int(input("Height: "))
            
            result = capture_region_screenshot(x, y, width, height)
            if result:
                print(f"\n🎉 Success! Region screenshot saved to scripts folder.")
            else:
                print(f"\n💥 Failed to capture region screenshot.")
                
        except ValueError:
            print("❌ Invalid coordinates. Please enter numbers only.")
            
    elif choice == "3":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice. Please run the script again.") 