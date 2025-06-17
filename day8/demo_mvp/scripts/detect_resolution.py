#!/usr/bin/env python3
"""
Resolution Detection Script for Mac Retina Display Scaling (Multi-Monitor Support)

This script helps you detect your Mac's screen resolution settings across multiple monitors
and generates the appropriate .env configuration for accurate mouse control.
"""

import pyautogui
import subprocess
import sys
import os
from pathlib import Path

def get_mac_display_info():
    """Get detailed display information on Mac using system_profiler."""
    try:
        result = subprocess.run([
            'system_profiler', 'SPDisplaysDataType'
        ], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Could not get display info: {e}")
        return None

def get_monitor_info():
    """Get information about all connected monitors."""
    try:
        # Try to get monitor info using system_profiler
        display_info = get_mac_display_info()
        if display_info:
            print("🖥️  Display Information from system_profiler:")
            print("-" * 50)
            # Look for resolution information in the output
            lines = display_info.split('\n')
            current_display = None
            for line in lines:
                line = line.strip()
                if 'Display' in line and ':' in line:
                    current_display = line
                    print(f"📺 {line}")
                elif 'Resolution:' in line:
                    print(f"   📐 {line}")
                elif 'UI Looks like:' in line:
                    print(f"   🎯 {line}")
                elif 'Framebuffer Depth:' in line:
                    print(f"   🎨 {line}")
            print("-" * 50)
    except Exception as e:
        print(f"Could not get detailed monitor info: {e}")

def detect_multi_monitor_setup():
    """Detect multi-monitor setup and provide guidance."""
    print("🔍 Detecting multi-monitor setup...")
    
    # Get total virtual screen size
    try:
        # This might give us the combined resolution across all monitors
        all_monitors_size = pyautogui.size()
        print(f"📱 Total virtual screen size: {all_monitors_size.width} x {all_monitors_size.height}")
        
        # Take a screenshot to see what resolution we actually capture
        print("📸 Taking test screenshot to detect actual capture resolution...")
        test_screenshot = pyautogui.screenshot()
        screenshot_width, screenshot_height = test_screenshot.size
        print(f"🖥️  Screenshot resolution: {screenshot_width} x {screenshot_height}")
        
        # Check if they match
        if (all_monitors_size.width == screenshot_width and 
            all_monitors_size.height == screenshot_height):
            print("✅ Virtual screen size matches screenshot size")
        else:
            print("⚠️  Virtual screen size differs from screenshot size!")
            print("   This suggests complex multi-monitor scaling")
        
        return {
            'virtual_width': all_monitors_size.width,
            'virtual_height': all_monitors_size.height,
            'screenshot_width': screenshot_width,
            'screenshot_height': screenshot_height,
        }
    except Exception as e:
        print(f"Error detecting monitor setup: {e}")
        return None

def detect_resolutions():
    """Detect both physical and logical screen resolutions with multi-monitor awareness."""
    print("🔍 Detecting screen resolutions...")
    
    # First, get monitor information
    get_monitor_info()
    
    # Detect multi-monitor setup
    monitor_info = detect_multi_monitor_setup()
    
    if not monitor_info:
        print("❌ Could not detect monitor configuration")
        return None
    
    # Get logical screen size (what pyautogui uses for mouse coordinates)
    logical_width = monitor_info['virtual_width']
    logical_height = monitor_info['virtual_height']
    print(f"\n📱 Logical resolution (mouse coordinates): {logical_width} x {logical_height}")
    
    # Get physical screen size (what screenshot captures)
    physical_width = monitor_info['screenshot_width']
    physical_height = monitor_info['screenshot_height']
    print(f"🖥️  Physical resolution (screenshot): {physical_width} x {physical_height}")
    
    # Calculate scaling factors
    scale_x = logical_width / physical_width if physical_width > 0 else 1.0
    scale_y = logical_height / physical_height if physical_height > 0 else 1.0
    
    print(f"📐 Calculated scaling factors: X={scale_x:.3f}, Y={scale_y:.3f}")
    
    # Determine if scaling is needed
    needs_scaling = abs(scale_x - 1.0) > 0.001 or abs(scale_y - 1.0) > 0.001
    print(f"🎯 Coordinate scaling needed: {'YES' if needs_scaling else 'NO'}")
    
    # Multi-monitor warnings
    if logical_width > 4000 or logical_height > 3000:
        print("\n⚠️  MULTI-MONITOR DETECTED:")
        print("   Your total screen resolution suggests multiple monitors.")
        print("   Make sure to test the mouse clicks on the monitor where")
        print("   the calculator browser window is located!")
    
    return {
        'logical_width': logical_width,
        'logical_height': logical_height,
        'physical_width': physical_width,
        'physical_height': physical_height,
        'scale_x': scale_x,
        'scale_y': scale_y,
        'needs_scaling': needs_scaling,
        'multi_monitor_detected': logical_width > 4000 or logical_height > 3000
    }

def generate_env_config(resolution_info):
    """Generate .env configuration lines."""
    config_lines = [
        "# Screen Resolution & Scaling Settings (Generated by detect_resolution.py)",
        f"PHYSICAL_SCREEN_WIDTH={resolution_info['physical_width']}",
        f"PHYSICAL_SCREEN_HEIGHT={resolution_info['physical_height']}",
        f"LOGICAL_SCREEN_WIDTH={resolution_info['logical_width']}",
        f"LOGICAL_SCREEN_HEIGHT={resolution_info['logical_height']}",
        f"ENABLE_COORDINATE_SCALING={'true' if resolution_info['needs_scaling'] else 'false'}",
        "",
        "# Alternative: Use manual scaling factors if auto-detection fails",
        f"# MANUAL_SCALE_FACTOR_X={resolution_info['scale_x']:.6f}",
        f"# MANUAL_SCALE_FACTOR_Y={resolution_info['scale_y']:.6f}",
    ]
    
    if resolution_info['multi_monitor_detected']:
        config_lines.extend([
            "",
            "# MULTI-MONITOR SETUP DETECTED:",
            "# If mouse clicks are inaccurate, you may need to:",
            "# 1. Move your browser to monitor 1 (leftmost/primary)",
            "# 2. Or manually set scaling factors for your target monitor",
            "# 3. Or disable scaling: ENABLE_COORDINATE_SCALING=false"
        ])
    
    return config_lines

def test_mouse_position():
    """Interactive test to help verify monitor setup."""
    print("\n" + "=" * 60)
    print("🎯 MOUSE POSITION TEST")
    print("=" * 60)
    print("This test will help verify which monitor your mouse coordinates reference.")
    print("\n1. Move your mouse to the TOP-LEFT corner of the monitor where")
    print("   your calculator browser window is located.")
    print("2. Press Enter when ready...")
    
    input("Press Enter when your mouse is at TOP-LEFT of calculator monitor: ")
    
    x, y = pyautogui.position()
    print(f"📍 Mouse position: ({x}, {y})")
    
    if x == 0 and y == 0:
        print("✅ Perfect! You're on the primary monitor (0,0 origin)")
    elif x > 0:
        print(f"⚠️  X={x} suggests your calculator is on monitor 2 or right monitor")
        print("   The coordinate system includes monitor 1 to the left")
    elif x < 0:
        print(f"⚠️  X={x} suggests your calculator is on a monitor to the left")
    
    print("\n3. Now move your mouse to the CENTER of the calculator display")
    print("   (where the numbers and buttons are shown)")
    input("Press Enter when your mouse is at the CENTER of calculator: ")
    
    center_x, center_y = pyautogui.position()
    print(f"📍 Calculator center position: ({center_x}, {center_y})")
    
    return {
        'top_left': (x, y),
        'center': (center_x, center_y)
    }

def main():
    print("=" * 60)
    print("🍎 Mac Multi-Monitor Resolution Detection for AI Calculator Assistant")
    print("=" * 60)
    
    # Detect resolutions
    resolution_info = detect_resolutions()
    
    if not resolution_info:
        print("❌ Failed to detect resolution information")
        return
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if resolution_info['multi_monitor_detected']:
        print("🖥️🖥️ MULTI-MONITOR SETUP DETECTED")
        print("    Your setup spans multiple monitors.")
    
    if resolution_info['needs_scaling']:
        print("⚠️  Your Mac has different physical and logical resolutions.")
        print("   This is common with Retina displays or custom scaling settings.")
        print("   Coordinate scaling is RECOMMENDED for accurate mouse control.")
    else:
        print("✅ Your physical and logical resolutions match.")
        print("   No coordinate scaling needed.")
    
    print(f"\n🔢 Resolution Details:")
    print(f"   • Physical (Screenshot): {resolution_info['physical_width']} x {resolution_info['physical_height']}")
    print(f"   • Logical (Mouse):       {resolution_info['logical_width']} x {resolution_info['logical_height']}")
    print(f"   • Scale Factors:         X={resolution_info['scale_x']:.3f}, Y={resolution_info['scale_y']:.3f}")
    
    # Interactive mouse test for multi-monitor setups
    if resolution_info['multi_monitor_detected']:
        response = input("\n🎯 Run interactive mouse position test? (y/n): ").strip().lower()
        if response == 'y':
            mouse_info = test_mouse_position()
            print(f"\n📊 Mouse Test Results:")
            print(f"   • Monitor top-left: {mouse_info['top_left']}")
            print(f"   • Calculator center: {mouse_info['center']}")
    
    # Generate configuration
    print("\n" + "=" * 60)
    print("⚙️  RECOMMENDED .ENV CONFIGURATION")
    print("=" * 60)
    
    config_lines = generate_env_config(resolution_info)
    for line in config_lines:
        print(line)
    
    # Offer to append to .env file
    print("\n" + "=" * 60)
    print("💾 SAVE CONFIGURATION")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        response = input(f"\n📁 Found .env file at: {env_file}\n   Replace previous resolution settings? (y/n): ").strip().lower()
        if response == 'y':
            # Read existing .env file and remove old resolution settings
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter out old resolution settings
            filtered_lines = []
            skip_block = False
            for line in lines:
                if "# Screen Resolution & Scaling Settings" in line:
                    skip_block = True
                elif line.strip() == "" and skip_block:
                    continue
                elif skip_block and (line.startswith("PHYSICAL_SCREEN_") or 
                                   line.startswith("LOGICAL_SCREEN_") or
                                   line.startswith("ENABLE_COORDINATE_") or
                                   line.startswith("MANUAL_SCALE_") or
                                   line.startswith("# MANUAL_SCALE_") or
                                   line.startswith("# MULTI-MONITOR") or
                                   line.startswith("# If mouse clicks") or
                                   line.startswith("# 1. Move your browser") or
                                   line.startswith("# 2. Or manually") or
                                   line.startswith("# 3. Or disable")):
                    continue
                else:
                    skip_block = False
                    filtered_lines.append(line)
            
            # Write back the filtered content with new settings
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(filtered_lines)
                f.write("\n# Resolution settings added by detect_resolution.py\n")
                for line in config_lines:
                    f.write(line + "\n")
            print("✅ Configuration updated in .env file!")
        else:
            print("⏭️  Configuration not saved. You can copy the lines above manually.")
    else:
        print(f"⚠️  No .env file found at: {env_file}")
        print("   You can create one and add the configuration above.")
    
    print("\n" + "=" * 60)
    print("🚀 NEXT STEPS")
    print("=" * 60)
    print("1. Ensure your calculator browser is on the correct monitor")
    print("2. Run your AI calculator assistant: rye run python -m src.main")
    print("3. Test with: 'can you do 1 plus 1 on the calculator'")
    print("4. Watch the logs to see coordinate scaling in action!")
    
    if resolution_info['multi_monitor_detected']:
        print("\n🖥️🖥️ MULTI-MONITOR TIPS:")
        print("• If clicks are off, try moving browser to monitor 1 (primary)")
        print("• Or set ENABLE_COORDINATE_SCALING=false for testing")
        print("• Check that browser is fullscreen or maximized on target monitor")
    
    print("\n🎯 The mouse should now click exactly where Gemini indicates!")

if __name__ == "__main__":
    main() 