#!/usr/bin/env python3

"""
Screen utilities for coordinate handling and scaling.
Simplified for element-based interactions with minimal screenshot dependencies.
"""

import pyautogui
import logging
from typing import Tuple
from ..utils.config import config

logger = logging.getLogger(__name__)

def get_screen_size() -> Tuple[int, int]:
    """
    Get the logical screen size that PyAutoGUI uses for mouse coordinates.
    
    Returns:
        Tuple of (width, height) in logical pixels
    """
    try:
        size = pyautogui.size()
        logger.debug(f"Screen size: {size.width}x{size.height}")
        return (size.width, size.height)
    except Exception as e:
        logger.error(f"Error getting screen size: {e}")
        return (0, 0)

def scale_coordinates(x: int, y: int) -> Tuple[int, int]:
    """
    Scale coordinates if needed (mostly for legacy compatibility).
    
    Args:
        x, y: Input coordinates
        
    Returns:
        Tuple of (scaled_x, scaled_y) coordinates
    """
    if not config.enable_coordinate_scaling:
        logger.debug(f"Coordinate scaling disabled, using original coordinates: ({x}, {y})")
        return x, y
    
    # For most modern setups with element-based detection, no scaling is needed
    # This is kept for backward compatibility
    scale_x = getattr(config, 'manual_scale_factor_x', 1.0)
    scale_y = getattr(config, 'manual_scale_factor_y', 1.0)
    
    if scale_x != 1.0 or scale_y != 1.0:
        scaled_x = int(x / scale_x)
        scaled_y = int(y / scale_y)
        logger.debug(f"Scaled coordinates from ({x}, {y}) to ({scaled_x}, {scaled_y})")
        return scaled_x, scaled_y
    else:
        return x, y

def validate_coordinates(x: int, y: int) -> bool:
    """
    Validate that coordinates are within screen bounds.
    
    Args:
        x, y: Coordinates to validate
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    try:
        screen_width, screen_height = get_screen_size()
        
        if screen_width == 0 or screen_height == 0:
            logger.warning("Could not get screen size for validation")
            return True  # Assume valid if we can't check
        
        valid = 0 <= x <= screen_width and 0 <= y <= screen_height
        
        if not valid:
            logger.warning(f"Coordinates ({x}, {y}) are outside screen bounds ({screen_width}x{screen_height})")
        
        return valid
        
    except Exception as e:
        logger.error(f"Error validating coordinates: {e}")
        return True  # Assume valid if validation fails

# Legacy functions kept for compatibility but deprecated
def capture_screen_to_image(*args, **kwargs):
    """
    DEPRECATED: Use BrowserService for element-based interactions instead.
    """
    logger.warning("capture_screen_to_image is deprecated. Use BrowserService for element detection.")
    return None

def capture_monitor_zero(*args, **kwargs):
    """
    DEPRECATED: Use BrowserService for element-based interactions instead.
    """
    logger.warning("capture_monitor_zero is deprecated. Use BrowserService for element detection.")
    return None

# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    
    print("--- Testing Screen Utils ---")
    
    # Test screen size detection
    width, height = get_screen_size()
    print(f"Screen size: {width}x{height}")
    
    # Test coordinate validation
    test_coords = [(100, 100), (width + 100, height + 100), (-10, 50)]
    for x, y in test_coords:
        valid = validate_coordinates(x, y)
        print(f"Coordinates ({x}, {y}): {'Valid' if valid else 'Invalid'}")
    
    # Test coordinate scaling
    test_x, test_y = 500, 300
    scaled_x, scaled_y = scale_coordinates(test_x, test_y)
    print(f"Coordinates ({test_x}, {test_y}) scaled to ({scaled_x}, {scaled_y})")
    
    print("Screen utils test completed.") 