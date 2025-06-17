# Project: AI Financial Calculator Assistant - MVP Scope

## 1. Core Objective

To develop an MVP of an AI-powered assistant that can:
    1.  Answer user questions about the BA II Plus calculator using its PDF guidebook.
    2.  Demonstrate calculator operations on the `https://baiiplus.com/` website by:
        *   Using `playwright` to launch and manage a browser instance with the target website.
        *   Using `playwright` to detect and locate calculator elements via selectors (CSS, XPath, text content).
        *   Calculating precise screen coordinates by combining `playwright` element positions with browser window positioning.
        *   Using `pyautogui` to control the actual system mouse cursor for smooth, visible demonstrations.
        *   Having Gemini AI generate step-by-step plans with element selectors instead of guessing coordinates from screenshots.
        *   Providing voice narration for both answers and demonstrations using Gemini's native Text-to-Speech (TTS).

## 2. Input Methods (MVP)

*   **User Queries:** Text input via the terminal.
*   **Calculator State:**
    *   Browser context (HTML, page structure, element selectors) managed by `playwright`.
    *   Precise element positioning via `playwright` element detection and coordinate calculation.
*   **Knowledge Base:** BA II Plus PDF guidebook.

## 3. AI Persona & Output Strategy

*   **Persona:** The AI will adopt the persona of an "AE Sales Rep," aiming to convincingly demonstrate how the calculator meets the user's requirements.
*   **Output Format from Gemini for Demonstrations:** Gemini will be prompted to return a structured JSON list of commands. Each command will specify:
    *   `type`: "voice" or "element_interaction".
    *   `content` (for voice): The text to be spoken.
    *   `action` (for element_interaction): "click" or "type".
    *   `element_selector`: CSS selector, XPath, or descriptive text for element identification.
    *   `value` (for type actions): The string to be typed.
    *   `timing`: Hints for sequencing (e.g., "before_interaction", "after_interaction", "pause").

    **Example JSON Output Structure:**
    ```json
    [
        {"type": "voice", "content": "First, we need to access the cash flow register. I'll click the CF button now.", "timing": "before_interaction"},
        {"type": "element_interaction", "action": "click", "element_selector": "button[data-key='CF']", "timing": "immediate"},
        {"type": "voice", "content": "Great! Now the cash flow register is active. Let's enter your initial investment.", "timing": "after_interaction"},
        {"type": "element_interaction", "action": "type", "element_selector": "input.calculator-display", "value": "1000", "timing": "immediate"},
        {"type": "element_interaction", "action": "click", "element_selector": "button[data-key='ENTER']", "timing": "immediate"},
        {"type": "voice", "content": "Perfect! The initial investment of 1000 has been registered.", "timing": "after_interaction"}
    ]
    ```

## 4. Key Modules & Technologies

*   **Orchestrator:**
    *   Manages the flow of user interaction.
    *   Performs intent detection (Q&A vs. Demonstration).
*   **Q&A Module:**
    *   Utilizes Gemini (e.g., `gemini-2.5-pro` or a similar powerful model) with access to the BA II Plus PDF (via Gemini File API) and HTML content from the calculator.
    *   Generates textual answers in the "AE Sales Rep" persona.
*   **Demonstration Module:**
    *   Ensures `playwright` has the correct page loaded and ready.
    *   Gets HTML content and available element selectors via `playwright`.
    *   Sends user instruction and relevant context (PDF snippets, HTML structure, available elements) to Gemini.
    *   Prompts Gemini to generate the structured JSON plan of voice and element interaction actions.
*   **Element Mapper:**
    *   Maps user instructions to specific calculator elements using intelligent analysis.
    *   Provides fallback strategies for element detection.
*   **Browser Service:**
    *   Manages `playwright` browser instance and page navigation.
    *   Locates elements using selectors and calculates absolute screen coordinates.
    *   Accounts for browser chrome (address bar, etc.) in coordinate calculations.
*   **Mouse Service:**
    *   Uses `pyautogui` for smooth, visible mouse movements to calculated coordinates.
    *   Provides precise clicking and typing capabilities.
*   **Output Execution Engine:**
    *   Parses the structured JSON plan from Gemini.
    *   Orchestrates the sequence of voice narration and mouse interactions.
    *   Uses Gemini's native TTS (e.g., `gemini-2.5-flash-preview-tts`) for voice output, played via `pyaudio`.
*   **Core Libraries:**
    *   `google-generativeai` (for Gemini API access, including File API and TTS).
    *   `playwright` (for browser automation, element detection, and coordinate calculation).
    *   `pyautogui` (for visible mouse control and smooth movements).
    *   `pyaudio` (for audio playback).

## 5. Workflow Overview

1.  User provides a text command in the terminal.
2.  Orchestrator determines if it's a question or a demonstration request.
3.  **For Q&A:**
    *   Relevant context (PDF, HTML) is provided to Gemini along with the question.
    *   Gemini generates an answer.
    *   Answer is spoken via TTS.
4.  **For Demonstrations:**
    *   `playwright` ensures the browser is open to `https://baiiplus.com/`.
    *   HTML content and available element structure are analyzed via `playwright`.
    *   User request, HTML context, and PDF context are sent to Gemini.
    *   Gemini returns a structured JSON plan of voice and element interaction actions.
    *   The Output Execution Engine iterates through the plan:
        *   Speaks voice commands using TTS.
        *   Uses `playwright` to locate elements and calculate screen coordinates.
        *   Uses `pyautogui` to perform smooth, visible mouse movements and interactions.
        *   Manages timing and sequencing based on the plan.

## 6. Key Advantages & MVP Benefits

*   **Precision**: Element coordinates are calculated exactly using `playwright`'s element detection rather than AI guessing from screenshots.
*   **Reliability**: No dependency on Gemini's visual analysis accuracy for coordinate detection.
*   **Visibility**: Real mouse movements provide clear visual feedback to users.
*   **Robustness**: Element selectors can adapt to minor UI changes better than fixed coordinates.
*   **Performance**: Faster execution without screenshot capture and analysis overhead.
*   **MacOS Compatibility**: Designed specifically for MacOS with appropriate accessibility permissions and PyAutoGUI configuration.

## 7. Key Assumptions & MVP Limitations

*   The `https://baiiplus.com/` website is accessible and its HTML structure contains identifiable element selectors.
*   **MacOS Accessibility Permissions** must be granted to Terminal/Python for mouse control.
*   Element-based interaction (`playwright` + `pyautogui`) is sufficient for the MVP. Pure `playwright` clicking is a future enhancement.
*   Sequential processing of voice and element interaction actions from the plan is sufficient for MVP.
*   PDF content will be primarily accessed via the Gemini File API.
*   Coordinate calculations account for standard browser chrome heights (can be adjusted if needed).

## 8. Next Steps (Development)

1.  Acquire BA II Plus PDF.
2.  Set up Python environment with necessary libraries.
3.  Configure MacOS accessibility permissions for PyAutoGUI.
4.  Implement Gemini API key management.
5.  Develop the Browser Service with element detection and coordinate calculation.
6.  Develop the Mouse Service for smooth PyAutoGUI control.
7.  Develop the TTS module (`generate_and_play_speech` using Gemini TTS and `pyaudio`).
8.  Draft and test the core prompt for the Demonstration Module to achieve the desired structured JSON output with element selectors.
9.  Implement the Q&A module with PDF and HTML context.
10. Build the Output Execution Engine to process the structured plan with element interactions.
11. Integrate all modules into the main application loop. 