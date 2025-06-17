#!/usr/bin/env python3
"""
Simple script to move mouse to specific coordinates and hover for 5 seconds each.
Coordinates extracted from the demonstration output.
"""

import pyautogui
import time

def hover_at_coordinates():
    """Move mouse to each coordinate and hover for 5 seconds."""
    
    # Coordinates from the demonstration output
    coordinates = [
        (265, 627, "the '7' button"),
        (319, 585, "the '+' button"), 
        (319, 627, "the '8' button"),
        (353, 627, "the '=' button"),
    ]
    
    print("🖱️ Starting coordinate hover test...")
    print("Press Ctrl+C to stop if needed\n")
    
    # Give user time to prepare
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    for i, (x, y, description) in enumerate(coordinates, 1):
        print(f"Step {i}/4: Moving to ({x}, {y}) - {description}")
        
        # Move mouse to coordinates
        pyautogui.moveTo(x, y, duration=1.0)
        
        # Show current position
        current_pos = pyautogui.position()
        print(f"  Current position: {current_pos}")
        
        # Hover for 5 seconds
        print(f"  Hovering for 5 seconds...")
        time.sleep(5)
        
        print(f"  ✅ Completed hover at {description}\n")
    
    print("🎯 All coordinates tested!")

if __name__ == "__main__":
    # Safety check - allow user to cancel
    print("This script will move your mouse to specific coordinates.")
    print("Make sure you have the calculator visible on screen.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        hover_at_coordinates()
    except KeyboardInterrupt:
        print("\n❌ Script cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}") 