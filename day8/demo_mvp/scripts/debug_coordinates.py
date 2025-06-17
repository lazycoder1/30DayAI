#!/usr/bin/env python3
"""
Coordinate Debugging Script

This script helps debug coordinate scaling issues by:
1. Taking a screenshot
2. Capturing current mouse position
3. Marking the mouse position on the screenshot
4. Showing both logical and physical coordinates
5. Using Gemini AI to detect button coordinates
"""

import pyautogui
import time
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from pathlib import Path
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_gemini():
    """Initialize Gemini AI client."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables!")
        return None
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

def countdown(seconds=5):
    """Countdown timer to give user time to position mouse."""
    print(f"\n🎯 Position your mouse where you want to test coordinates...")
    for i in range(seconds, 0, -1):
        print(f"⏰ Screenshot in {i} seconds...")
        time.sleep(1)
    print("📸 Taking screenshot NOW!")

def get_mouse_and_screenshot():
    """Capture mouse position and take screenshot simultaneously."""
    # Get mouse position first
    mouse_x, mouse_y = pyautogui.position()
    print(f"🖱️  Mouse position: ({mouse_x}, {mouse_y})")
    
    # Take screenshot of Monitor 0 only (4K: 3840x2160)
    screenshot = ImageGrab.grab(bbox=(0, 0, 3840, 2160))
    print(f"📸 Screenshot size: {screenshot.size}")
    
    return mouse_x, mouse_y, screenshot

def draw_crosshair(image, x, y, color='red', size=20, label=None):
    """Draw a crosshair at the specified coordinates."""
    draw = ImageDraw.Draw(image)
    
    # Convert logical coordinates to physical coordinates for drawing on screenshot
    # Screenshot is 3840x2160 (physical), mouse coords are 2560x1440 (logical)
    # Scale factor is 1.5 (3840/2560 = 1.5, 2160/1440 = 1.5)
    physical_x = int(x * 1.5)  # Scale logical to physical
    physical_y = int(y * 1.5)  # Scale logical to physical
    
    print(f"🎯 Drawing crosshair at logical ({x}, {y}) -> physical ({physical_x}, {physical_y})")
    
    # Draw crosshair lines
    draw.line([(physical_x - size, physical_y), (physical_x + size, physical_y)], fill=color, width=3)
    draw.line([(physical_x, physical_y - size), (physical_x, physical_y + size)], fill=color, width=3)
    
    # Draw circle at center
    draw.ellipse([
        physical_x - 5, physical_y - 5,
        physical_x + 5, physical_y + 5
    ], outline=color, width=3)
    
    # Add label if provided
    if label:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw label with background
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        label_x = physical_x + 15
        label_y = physical_y - 10
        
        draw.rectangle([
            label_x - 2, label_y - 2,
            label_x + text_width + 2, label_y + text_height + 2
        ], fill='white', outline=color)
        
        draw.text((label_x, label_y), label, fill=color, font=font)
    
    return physical_x, physical_y

def add_coordinate_text(image, mouse_x, mouse_y, physical_x, physical_y):
    """Add coordinate information as text on the image."""
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Create coordinate text
    text_lines = [
        f"Mouse Position (Logical): ({mouse_x}, {mouse_y})",
        f"Screenshot Size (Physical): {image.size}",
        f"Crosshair Position (Physical): ({physical_x}, {physical_y})",
        f"Scale Factors: X={image.width/2560:.3f}, Y={image.height/1440:.3f}"
    ]
    
    # Draw text with background
    y_offset = 30
    for line in text_lines:
        # Get text size
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw background rectangle
        draw.rectangle([
            10, y_offset - 5,
            20 + text_width, y_offset + text_height + 5
        ], fill='white', outline='black')
        
        # Draw text
        draw.text((15, y_offset), line, fill='black', font=font)
        y_offset += text_height + 10

def ask_gemini_for_coordinates(model, screenshot_path):
    """Ask Gemini to detect button coordinates from screenshot."""
    print("\n🤖 Asking Gemini to analyze screenshot for button coordinates...")
    
    try:
        # Upload the screenshot
        screenshot_file = genai.upload_file(screenshot_path)
        
        prompt = """
        Please analyze this calculator screenshot and provide the exact pixel coordinates for these buttons:
        1. The "1" button
        2. The "+" button  
        3. The "=" button

        Look carefully at the calculator interface and identify these specific buttons.
        
        Return your response as a JSON object with this exact format:
        {
            "1": {"x": <x_coordinate>, "y": <y_coordinate>},
            "+": {"x": <x_coordinate>, "y": <y_coordinate>},
            "=": {"x": <x_coordinate>, "y": <y_coordinate>}
        }
        
        Important: 
        - Provide coordinates in the screenshot's native resolution
        - Be as precise as possible with the center of each button
        - Only return the JSON, no additional text
        """
        
        response = model.generate_content([screenshot_file, prompt])
        
        # Clean up the response - remove any markdown formatting
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON response
        coordinates = json.loads(response_text)
        print("✅ Gemini analysis complete!")
        return coordinates
        
    except Exception as e:
        print(f"❌ Error asking Gemini: {e}")
        return None

def test_gemini_coordinates():
    """Test Gemini's coordinate detection against manual findings."""
    print("\n" + "=" * 60)
    print("🤖 GEMINI COORDINATE DETECTION TEST")
    print("=" * 60)
    
    # Initialize Gemini
    model = setup_gemini()
    if not model:
        print("❌ Cannot initialize Gemini. Skipping this test.")
        return
    
    print("📸 Taking screenshot for Gemini analysis...")
    screenshot = ImageGrab.grab(bbox=(0, 0, 3840, 2160))
    
    # Save screenshot for Gemini
    screenshot_path = "gemini_analysis_screenshot.png"
    screenshot.save(screenshot_path)
    print(f"💾 Screenshot saved: {screenshot_path}")
    
    # Ask Gemini for coordinates
    gemini_coords = ask_gemini_for_coordinates(model, screenshot_path)
    
    if not gemini_coords:
        print("❌ Failed to get coordinates from Gemini")
        return
    
    print("\n🎯 Gemini detected these coordinates:")
    for button, coords in gemini_coords.items():
        print(f"   {button}: ({coords['x']}, {coords['y']})")
    
    # Create visualization with Gemini's coordinates
    marked_image = screenshot.copy()
    
    colors = ['red', 'green', 'blue']
    for i, (button, coords) in enumerate(gemini_coords.items()):
        color = colors[i % len(colors)]
        draw_crosshair(
            marked_image, 
            coords['x'], 
            coords['y'], 
            color=color, 
            size=25, 
            label=f"Gemini: {button}"
        )
    
    # Save marked image
    output_path = "gemini_coordinate_analysis.png"
    marked_image.save(output_path)
    print(f"💾 Gemini analysis visualization saved: {output_path}")
    
    # First, capture monitor boundary to determine coordinate space
    print("\n" + "=" * 60)
    print("🖥️  MONITOR BOUNDARY DETECTION")
    print("=" * 60)
    print("First, let's determine if PIL returns physical or logical coordinates.")
    print("Please position your mouse at the BOTTOM-RIGHT corner of your monitor")
    print("(as close to the edge as possible)")
    
    input("Press ENTER when your mouse is at the bottom-right corner...")
    
    # Give a short countdown for monitor corner
    for i in range(3, 0, -1):
        print(f"Capturing monitor corner in {i}...")
        time.sleep(1)
    
    # Capture monitor corner position
    corner_x, corner_y = pyautogui.position()
    print(f"✅ Monitor corner captured at: ({corner_x}, {corner_y})")
    
    # Determine coordinate space
    if corner_x >= 3800 and corner_y >= 2100:  # Close to 4K physical
        coord_space = "Physical (4K)"
        expected_resolution = "3840x2160"
    elif corner_x >= 2500 and corner_y >= 1400:  # Close to logical
        coord_space = "Logical (Scaled)"
        expected_resolution = "2560x1440"
    else:
        coord_space = "Unknown"
        expected_resolution = f"{corner_x+1}x{corner_y+1}"
    
    print(f"📊 Detected coordinate space: {coord_space}")
    print(f"📏 Estimated resolution: {expected_resolution}")
    
    # Prompt user to position mouse over buttons
    print("\n" + "=" * 60)
    print("🖱️  BUTTON POSITION CAPTURE")
    print("=" * 60)
    print("Now position your mouse over each calculator button when prompted:")
    print("The script will capture your mouse coordinates automatically.")
    
    manual_coords = {}
    
    # Store monitor info
    manual_coords["monitor_corner"] = {"x": corner_x, "y": corner_y, "space": coord_space}
    
    for button in ['1', '+', '=']:
        print(f"\n📍 Please position your mouse over the '{button}' button")
        input("Press ENTER when your mouse is positioned over the button...")
        
        # Give a short countdown
        for i in range(3, 0, -1):
            print(f"Capturing in {i}...")
            time.sleep(1)
        
        # Capture mouse position
        mouse_x, mouse_y = pyautogui.position()
        manual_coords[button] = {"x": mouse_x, "y": mouse_y}
        print(f"✅ Captured '{button}' button at: ({mouse_x}, {mouse_y})")
    
    # Test if pyautogui.moveTo() expects logical or physical coordinates
    print("\n" + "=" * 60)
    print("🖱️  PYAUTOGUI COORDINATE SPACE TEST")
    print("=" * 60)
    print("Now testing if pyautogui.moveTo() uses logical or physical coordinates...")
    print("The mouse will automatically move to each captured position.")
    print("Watch to see if it moves to the correct button locations!")
    
    input("\nPress ENTER to start the coordinate test...")
    
    for button in ['1', '+', '=']:
        coords = manual_coords[button]
        print(f"\n🎯 Moving mouse to captured '{button}' button position: ({coords['x']}, {coords['y']})")
        
        # Give user time to see where mouse will move
        for i in range(3, 0, -1):
            print(f"Moving in {i}...")
            time.sleep(1)
        
        # Move mouse to captured position
        pyautogui.moveTo(coords['x'], coords['y'])
        print(f"✅ Mouse moved to ({coords['x']}, {coords['y']})")
        
        # Ask user for verification
        correct = input(f"Is the mouse now positioned over the '{button}' button? (y/n): ").strip().lower()
        manual_coords[button]["pyautogui_accurate"] = correct == 'y'
        
        if correct == 'y':
            print(f"✅ PyAutoGUI coordinates are ACCURATE for '{button}' button")
        else:
            print(f"❌ PyAutoGUI coordinates are INACCURATE for '{button}' button")
    
    # Determine if pyautogui uses logical or physical coordinates
    accurate_count = sum(1 for button in ['1', '+', '='] if manual_coords[button].get("pyautogui_accurate", False))
    
    if accurate_count >= 2:
        pyautogui_coord_space = "Logical (Matches mouse capture)"
        print(f"\n✅ CONCLUSION: PyAutoGUI uses LOGICAL coordinates ({accurate_count}/3 accurate)")
    else:
        pyautogui_coord_space = "Physical or Different Scale"
        print(f"\n❌ CONCLUSION: PyAutoGUI may use PHYSICAL coordinates or different scaling ({accurate_count}/3 accurate)")
    
    manual_coords["pyautogui_analysis"] = {
        "coordinate_space": pyautogui_coord_space,
        "accuracy_count": f"{accurate_count}/3"
    }
    
    # Create comparison visualization
    comparison_image = screenshot.copy()
    
    # Draw Gemini coordinates (solid lines)
    for i, (button, coords) in enumerate(gemini_coords.items()):
        color = colors[i % len(colors)]
        draw_crosshair(
            comparison_image, 
            coords['x'], 
            coords['y'], 
            color=color, 
            size=25, 
            label=f"AI: {button}"
        )
    
    # Draw manual coordinates (dashed effect with smaller crosshairs)
    for i, (button, coords) in enumerate(manual_coords.items()):
        color = colors[i % len(colors)]
                 # Offset slightly for visibility
        draw_crosshair(
            comparison_image, 
            coords['x'] + 5, 
            coords['y'] + 5, 
            color=color, 
            size=15, 
            label=f"Mouse: {button}"
        )
    
    # Add comparison text
    draw = ImageDraw.Draw(comparison_image)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Get monitor info
    monitor_info = manual_coords.get("monitor_corner", {})
    monitor_corner = f"({monitor_info.get('x', 'N/A')}, {monitor_info.get('y', 'N/A')})"
    coord_space = monitor_info.get('space', 'Unknown')
    
    # Get PyAutoGUI analysis
    pyautogui_info = manual_coords.get("pyautogui_analysis", {})
    pyautogui_space = pyautogui_info.get('coordinate_space', 'Unknown')
    pyautogui_accuracy = pyautogui_info.get('accuracy_count', 'N/A')
    
    comparison_text = [
        "COORDINATE COMPARISON:",
        f"Screenshot: {screenshot.size} (Physical)",
        f"Monitor Corner: {monitor_corner} (Logical)",
        f"Mouse Coordinate Space: {coord_space}",
        f"PyAutoGUI Space: {pyautogui_space}",
        f"PyAutoGUI Accuracy: {pyautogui_accuracy}",
        f"Scale Factor: 1.5x (Physical/Logical)",
        ""
    ]
    
    for button in ['1', '+', '=']:
        gemini_coord = gemini_coords[button]
        mouse_coord = manual_coords[button]
        diff_x = abs(gemini_coord['x'] - mouse_coord['x'])
        diff_y = abs(gemini_coord['y'] - mouse_coord['y'])
        
        comparison_text.extend([
            f"{button} Button:",
            f"  Gemini: ({gemini_coord['x']}, {gemini_coord['y']})",
            f"  Mouse: ({mouse_coord['x']}, {mouse_coord['y']})",
            f"  Diff: ({diff_x}, {diff_y})",
            ""
        ])
    
    # Draw comparison text
    y_offset = comparison_image.height - (len(comparison_text) * 25) - 10
    for line in comparison_text:
        if line:  # Skip empty lines for spacing
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            draw.rectangle([
                10, y_offset - 2,
                15 + text_width, y_offset + text_height + 2
            ], fill='white', outline='black')
            
            draw.text((12, y_offset), line, fill='black', font=font)
        
        y_offset += 25
    
    # Save comparison image
    comparison_path = "coordinate_comparison.png"
    comparison_image.save(comparison_path)
    print(f"\n💾 Comparison visualization saved: {comparison_path}")
    print("🔍 Open the image to see Gemini vs Manual coordinates side by side!")

def test_specific_coordinates():
    """Test specific coordinates that the AI system provided."""
    print("\n" + "=" * 60)
    print("🧪 TESTING SPECIFIC COORDINATES FROM AI SYSTEM")
    print("=" * 60)
    
    # Coordinates from the last run
    test_coords = [
        (100, 540, "CE/C button"),
        (100, 480, "1 button"),
        (180, 480, "+ button"),
        (260, 480, "= button")
    ]
    
    screenshot = ImageGrab.grab(bbox=(0, 0, 3840, 2160))
    
    for i, (x, y, description) in enumerate(test_coords):
        print(f"\n📍 Testing {description}: AI suggested ({x}, {y})")
        
        # Create a copy of screenshot for each test
        test_image = screenshot.copy()
        
        # Draw crosshair at AI-suggested coordinates
        physical_x, physical_y = draw_crosshair(test_image, x, y, color='red', size=30)
        
        # Add text
        add_coordinate_text(test_image, x, y, physical_x, physical_y)
        
        # Save test image
        filename = f"coordinate_test_{i+1}_{description.replace(' ', '_')}.png"
        test_image.save(filename)
        print(f"💾 Saved test image: {filename}")

def main():
    print("=" * 60)
    print("🐛 COORDINATE DEBUGGING SCRIPT")
    print("=" * 60)
    print("This script will help debug coordinate scaling issues.")
    print("It will take a screenshot and show where your mouse actually is.")
    
    # Interactive coordinate testing
    while True:
        print("\n" + "=" * 60)
        print("Choose an option:")
        print("1. Test current mouse position (5 second delay)")
        print("2. Test AI-suggested coordinates")
        print("3. Gemini coordinate detection & comparison")
        print("4. Exit")
        print("=" * 60)
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            countdown(5)
            mouse_x, mouse_y, screenshot = get_mouse_and_screenshot()
            
            # Draw crosshair at mouse position
            marked_image = screenshot.copy()
            physical_x, physical_y = draw_crosshair(marked_image, mouse_x, mouse_y)
            
            # Add coordinate information
            add_coordinate_text(marked_image, mouse_x, mouse_y, physical_x, physical_y)
            
            # Save the marked image
            timestamp = int(time.time())
            filename = f"mouse_position_debug_{timestamp}.png"
            marked_image.save(filename)
            
            print(f"💾 Saved debug image: {filename}")
            print(f"🔍 Open the image to see if the crosshair is where your mouse was!")
            
        elif choice == '2':
            test_specific_coordinates()
            
        elif choice == '3':
            test_gemini_coordinates()
            
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main() 