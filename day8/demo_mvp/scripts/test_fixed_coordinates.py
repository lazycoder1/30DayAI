#!/usr/bin/env python3
"""
Test script to verify that the fixed demonstration module returns accurate coordinates.
This script tests the coordinate detection after removing misleading examples from the prompt.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path so we can import the modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.gemini_service import GeminiService
from src.modules.demonstration_module import DemonstrationModule
from src.utils import screen_utils
from PIL import ImageGrab
import json

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def capture_screenshot():
    """Capture screenshot using the same method as the main application."""
    try:
        screenshot = screen_utils.capture_single_monitor(0)  # Monitor 0
        if screenshot:
            logger.info(f"Screenshot captured: {screenshot.size}")
            return screenshot
        else:
            logger.error("Failed to capture screenshot using screen_utils")
            return None
    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        # Fallback to direct PIL ImageGrab
        logger.info("Trying direct PIL ImageGrab fallback...")
        try:
            screenshot = ImageGrab.grab(bbox=(0, 0, 3840, 2160))
            logger.info(f"Fallback screenshot captured: {screenshot.size}")
            return screenshot
        except Exception as e2:
            logger.error(f"Fallback screenshot also failed: {e2}")
            return None

def test_coordinate_accuracy():
    """Test if the fixed demonstration module returns accurate coordinates."""
    print("=" * 60)
    print("🧪 TESTING FIXED COORDINATE DETECTION")
    print("=" * 60)
    
    try:
        # Initialize services
        logger.info("Initializing Gemini service...")
        gemini_service = GeminiService()
        demo_module = DemonstrationModule(gemini_service)
        
        # Capture screenshot
        logger.info("Capturing screenshot...")
        screenshot = capture_screenshot()
        if not screenshot:
            print("❌ Failed to capture screenshot")
            return
            
        # Convert to bytes
        from io import BytesIO
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        screenshot_bytes = img_byte_arr.getvalue()
        
        # Test with a simple calculation instruction
        instruction = "Show me how to calculate 1 + 2 = on the calculator"
        
        print(f"\n📝 Testing instruction: '{instruction}'")
        print("🤖 Asking Gemini for demonstration plan...")
        
        # Get demonstration plan
        plan = demo_module.get_demonstration_plan(
            instruction=instruction,
            screenshot_image_bytes=screenshot_bytes
        )
        
        if not plan:
            print("❌ Failed to get demonstration plan")
            return
            
        print(f"✅ Got demonstration plan with {len(plan)} steps")
        
        # Extract and display coordinates
        print("\n🎯 COORDINATES FROM FIXED DEMO MODULE:")
        for i, step in enumerate(plan, 1):
            if step.get('action') == 'click' and 'coordinates' in step:
                coords = step['coordinates']
                target = step.get('target_description', 'unknown')
                print(f"   Step {i}: {target} → ({coords['x']}, {coords['y']})")
        
        # Compare with expected ranges (updated for 1512x982 logical resolution)
        print("\n📊 COORDINATE ANALYSIS:")
        expected_ranges = {
            "1": {"x_min": 750, "x_max": 850, "y_min": 750, "y_max": 850},
            "+": {"x_min": 830, "x_max": 930, "y_min": 650, "y_max": 750},
            "2": {"x_min": 830, "x_max": 930, "y_min": 750, "y_max": 850},
            "=": {"x_min": 900, "x_max": 1000, "y_min": 750, "y_max": 850}
        }
        
        accurate_coords = 0
        total_coords = 0
        
        for step in plan:
            if step.get('action') == 'click' and 'coordinates' in step:
                coords = step['coordinates']
                target = step.get('target_description', '')
                total_coords += 1
                
                # Check if coordinates are in expected ranges
                is_accurate = False
                for button, ranges in expected_ranges.items():
                    if button in target.lower():
                        if (ranges["x_min"] <= coords['x'] <= ranges["x_max"] and 
                            ranges["y_min"] <= coords['y'] <= ranges["y_max"]):
                            is_accurate = True
                            break
                
                if is_accurate:
                    accurate_coords += 1
                    status = "✅ ACCURATE"
                else:
                    status = "❌ INACCURATE"
                    
                print(f"   {target}: ({coords['x']}, {coords['y']}) - {status}")
        
        # Overall accuracy assessment
        if total_coords > 0:
            accuracy_percent = (accurate_coords / total_coords) * 100
            print(f"\n📈 OVERALL ACCURACY: {accurate_coords}/{total_coords} ({accuracy_percent:.1f}%)")
            
            if accuracy_percent >= 70:
                print("🎉 COORDINATES LOOK GOOD! The fix appears to be working.")
            else:
                print("⚠️  Coordinates still need improvement. May need further prompt refinement.")
        else:
            print("⚠️  No clickable coordinates found in the plan.")
            
        # Save full plan for inspection
        with open("fixed_demo_plan.json", "w") as f:
            json.dump(plan, f, indent=2)
        print(f"\n💾 Full demonstration plan saved to: fixed_demo_plan.json")
        
        return plan
        
    except Exception as e:
        logger.error(f"Error during coordinate accuracy test: {e}", exc_info=True)
        print(f"❌ Test failed with error: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Testing coordinate detection after prompt fix...")
    print("Make sure your calculator is visible on screen!")
    
    input("Press ENTER when ready to test...")
    
    result = test_coordinate_accuracy()
    
    if result:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed. Check the logs for details.") 