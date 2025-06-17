#!/usr/bin/env python3

"""
MacOS Visual Mouse Movement Demo
Uses PyAutoGUI to move the actual system cursor + Playwright to find elements
"""

import asyncio
import pyautogui
from playwright.async_api import async_playwright

# Configure PyAutoGUI for macOS
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1      # Small pause between commands

async def test_real_mouse_movement():
    """
    Uses PyAutoGUI to move the actual mouse cursor on macOS
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500,
        )
        
        page = await browser.new_page()
        
        print("🚀 Opening example.com...")
        await page.goto('https://example.com')
        await page.wait_for_load_state('networkidle')
        
        # Bring browser to front
        await page.bring_to_front()
        await asyncio.sleep(1)
        
        # Target XPath
        xpath = '/html/body/div/p[2]/a'
        print(f"🎯 Looking for element: {xpath}")
        
        element = page.locator(f'xpath={xpath}')
        
        if await element.count() > 0:
            print("✅ Found the target link!")
            
            # Get element position relative to page
            box = await element.bounding_box()
            
            # Get browser window position on screen
            # Note: This gets the viewport position within the browser window
            browser_bounds = await page.evaluate("""
                () => ({
                    x: window.screenX,
                    y: window.screenY,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY
                })
            """)
            
            # Calculate absolute screen coordinates
            # Adjust for browser chrome (typically ~80px for address bar, etc.)
            chrome_height = 100  # Approximate browser chrome height
            
            screen_x = browser_bounds['x'] + box['x'] + (box['width'] / 2)
            screen_y = browser_bounds['y'] + box['y'] + (box['height'] / 2) + chrome_height
            
            print(f"📍 Moving real mouse to screen position: ({screen_x:.0f}, {screen_y:.0f})")
            
            # Move the REAL system cursor using PyAutoGUI
            pyautogui.moveTo(screen_x, screen_y, duration=2.0)  # 2 second smooth movement
            
            print("🎯 Mouse moved! Pausing for 2 seconds...")
            await asyncio.sleep(2)
            
            # Click using PyAutoGUI (real click)
            print("👆 Clicking with real mouse...")
            pyautogui.click()
            
            print("✅ Successfully clicked with real mouse movement!")
            
        else:
            print("❌ Element not found!")
        
        # Keep browser open
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    print("""
🎯 MacOS Real Mouse Movement Demo

📋 SETUP:
1. pip install playwright pyautogui
2. playwright install chromium
3. Grant accessibility permissions to Terminal/Python when prompted

⚠️  IMPORTANT FOR MACOS:
- You'll be prompted to grant accessibility permissions
- The mouse will actually move on your screen
- Move mouse to top-left corner to emergency stop
    """)
    
    try:
        asyncio.run(test_real_mouse_movement())
    except Exception as e:
        print(f"❌ Error: {e}")
        if "accessibility" in str(e).lower():
            print("\n🔐 You need to grant accessibility permissions:")
            print("System Preferences > Security & Privacy > Accessibility")
            print("Add Terminal or your Python executable")