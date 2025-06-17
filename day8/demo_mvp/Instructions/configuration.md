# Configuration Guide

This document explains all the environment variables used by the AI Financial Calculator Assistant.

## Required Settings

Create a `.env` file in the `demo_mvp` directory with these settings:

```bash
# REQUIRED: Your Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

## Coordinate Calibration Settings (NEW!)

If mouse clicks are not hitting the calculator buttons correctly, adjust these settings:

```bash
# Browser Chrome Height Settings
BROWSER_CHROME_HEIGHT_OFFSET=35          # Default: 35px
ENABLE_DYNAMIC_CHROME_CALCULATION=true   # Default: true

# Troubleshooting:
# - If clicks are TOO LOW (below buttons): Reduce BROWSER_CHROME_HEIGHT_OFFSET (try 20 or 10)
# - If clicks are TOO HIGH (above buttons): Increase BROWSER_CHROME_HEIGHT_OFFSET (try 50 or 70)
# - Set ENABLE_DYNAMIC_CHROME_CALCULATION=false to use only the fixed offset
```

## Complete Configuration Options

```bash
# =============================================================================
# AI Financial Calculator Assistant - Environment Configuration
# =============================================================================

# --- REQUIRED: API Keys ---
GEMINI_API_KEY=your_gemini_api_key_here

# --- General Settings ---
LOG_LEVEL=INFO

# --- Gemini Model Names ---
TEXT_MODEL_NAME=gemini-1.5-flash-latest
MULTIMODAL_MODEL_NAME=gemini-1.5-flash-latest
TTS_MODEL_NAME=gemini-2.5-flash-preview-tts

# --- External Resource URLs ---
CALCULATOR_URL=https://baiiplus.com/

# --- Mouse Control Settings ---
DEFAULT_ACTION_DELAY=0.5

# --- Browser Chrome Height Settings ---
# Fine-tune coordinate calculations if clicks are off-target
BROWSER_CHROME_HEIGHT_OFFSET=35
ENABLE_DYNAMIC_CHROME_CALCULATION=true

# --- Screen Resolution & Scaling Settings (Mac Retina Display Support) ---
PHYSICAL_SCREEN_WIDTH=0  # 0 = auto-detect
PHYSICAL_SCREEN_HEIGHT=0  # 0 = auto-detect
LOGICAL_SCREEN_WIDTH=0  # 0 = auto-detect
LOGICAL_SCREEN_HEIGHT=0  # 0 = auto-detect
MANUAL_SCALE_FACTOR_X=0.0  # 0.0 = auto-calculate
MANUAL_SCALE_FACTOR_Y=0.0  # 0.0 = auto-calculate
ENABLE_COORDINATE_SCALING=true

# --- Multi-Monitor Settings ---
TARGET_MONITOR=0  # 0 = primary monitor
MONITOR_CAPTURE_REGION=  # Format: "x,y,width,height" or empty for auto-detect

# --- Gemini File API URIs (Optional) ---
GUIDEBOOK_FILE_URI=
CALCULATOR_HTML_FILE_URI=

# --- File Paths ---
GUIDEBOOK_PDF_PATH=documents/BAIIPlus_Guidebook_EN.pdf
```

## Quick Setup Guide

1. **Create .env file:**
   ```bash
   cd demo_mvp
   touch .env
   ```

2. **Add your Gemini API key:**
   ```bash
   echo "GEMINI_API_KEY=your_actual_api_key_here" >> .env
   ```

3. **Test coordinate accuracy:**
   ```bash
   rye run python coordinate_test.py
   ```

4. **If coordinates are off, adjust chrome height:**
   ```bash
   # For clicks that are too low:
   echo "BROWSER_CHROME_HEIGHT_OFFSET=20" >> .env
   
   # For clicks that are too high:
   echo "BROWSER_CHROME_HEIGHT_OFFSET=50" >> .env
   ```

5. **Test again until coordinates are accurate.**

## Troubleshooting Coordinate Issues

### Symptom: Mouse clicks below calculator buttons
**Solution:** Reduce chrome height offset
```bash
BROWSER_CHROME_HEIGHT_OFFSET=20  # or 10, 15
```

### Symptom: Mouse clicks above calculator buttons  
**Solution:** Increase chrome height offset
```bash
BROWSER_CHROME_HEIGHT_OFFSET=50  # or 60, 70
```

### Symptom: Inconsistent coordinate calculation
**Solution:** Disable dynamic calculation
```bash
ENABLE_DYNAMIC_CHROME_CALCULATION=false
BROWSER_CHROME_HEIGHT_OFFSET=40  # Set a fixed value that works
```

## Testing Coordinates

Use the coordinate test script to debug issues:

```bash
cd demo_mvp
rye run python coordinate_test.py
```

This will:
- Show you current chrome height calculations
- Test coordinate accuracy on different buttons
- Provide specific adjustment recommendations
- Allow interactive testing of mouse clicks 