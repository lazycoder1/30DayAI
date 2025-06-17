# AI Financial Calculator Assistant - Implementation Plan

## 1. Introduction

This document outlines the step-by-step plan for implementing the MVP of the AI Financial Calculator Assistant. It references the `mvp_scope.md` for feature details and `python_coding_standards.md` for development guidelines.

**Key Prerequisites (User to provide):**
*   BA II Plus PDF guidebook.
*   Gemini API Key (to be set as `GEMINI_API_KEY` environment variable).
*   Confirmation that `https://baiiplus.com/` is accessible.
*   **MacOS Accessibility Permissions** for Terminal/Python to control mouse cursor.

## 2. Phase 1: Project Setup & Foundations

*   **Task 2.1: Initialize Project with Rye**
    *   Action: Use `rye init demo_mvp` (if not already done) and `rye sync`.
    *   Outcome: Basic project structure with `pyproject.toml`.
*   **Task 2.2: Establish Directory Structure**
    *   Action: Create directories as outlined in `python_coding_standards.md` (e.g., `src/core`, `src/modules`, `src/services`, `src/utils`, `tests`, `docs`).
    *   Outcome: Organized project folders.
*   **Task 2.3: Initial Dependency Installation**
    *   Action: Add core dependencies using Rye:
        *   `rye add google-generativeai`
        *   `rye add pyautogui`
        *   `rye add pyaudio`
        *   `rye add python-dotenv` (for loading `.env` files)
        *   `rye add playwright`
        *   `rye add --dev pytest pytest-mock ruff`
    *   Run `rye run playwright install chromium` to install Chromium browser.
    *   Outcome: Dependencies listed in `pyproject.toml` and available in the virtual environment. Browser binaries for Playwright installed.
*   **Task 2.4: Configure PyAutoGUI for MacOS**
    *   Action: Configure PyAutoGUI settings for reliable MacOS operation:
        *   `pyautogui.FAILSAFE = True` (emergency stop by moving mouse to corner)
        *   `pyautogui.PAUSE = 0.1` (small pause between commands)
        *   Document the need for Accessibility permissions in setup instructions.
    *   Outcome: PyAutoGUI configured for safe operation on MacOS.
*   **Task 2.5: Configure Ruff**
    *   Action: Create/configure `ruff.toml` (or use `pyproject.toml [tool.ruff]`) with basic rules (e.g., line length, PEP 8 adherence).
    *   Outcome: Linter configured.
*   **Task 2.6: Setup `.gitignore` and `.env.example`**
    *   Action: Create a comprehensive `.gitignore` (including `.env`, `__pycache__`, Rye's `.venv`, etc.). Create `.env.example` listing `GEMINI_API_KEY` and any other anticipated config variables.
    *   Outcome: Project ready for version control and secure configuration.
*   **Task 2.7: Basic Logging Setup**
    *   Action: Create a utility function in `src/utils/helpers.py` for basic logging configuration (e.g., setting log level from an environment variable, basic formatter).
    *   Outcome: Centralized logging setup.

## 3. Phase 2: Core Service Wrappers & Utilities

*   **Task 3.1: Gemini API Service Wrapper (`src/services/gemini_service.py`)**
    *   Action:
        *   Create a class `GeminiService`.
        *   Initialize the `genai.Client` using the API key from environment variables.
        *   Implement a method for basic text generation (for Q&A responses).
        *   Implement a method for structured instruction planning (accepting text prompts and returning structured response for element selectors).
        *   Implement a method for invoking Gemini TTS and retrieving audio data.
    *   Reference: `python_coding_standards.md` (services), `mvp_scope.md` (Gemini usage).
    *   Outcome: A dedicated service to interact with the Gemini API.
*   **Task 3.2: Enhanced Browser Service (`src/services/browser_service.py`)**
    *   Action:
        *   Create a class `BrowserService`.
        *   Implement methods to:
            *   Initialize Playwright with browser launch options (`headless=False`, `slow_mo=500`).
            *   Launch a browser instance (Chromium) and create a new page.
            *   Navigate to `https://baiiplus.com/` and wait for load state.
            *   Bring browser to front for visibility.
            *   **Element Detection**: Find calculator elements using CSS selectors, XPath, or text content.
            *   **Coordinate Calculation**: Get element bounding box and calculate screen coordinates accounting for browser chrome.
            *   Get browser window position (`window.screenX`, `window.screenY`) via JavaScript evaluation.
            *   Get the full HTML content of the page.
            *   Ensure proper browser closing.
    *   Outcome: Service to manage browser interaction and provide precise element coordinates.
*   **Task 3.3: Mouse Control Service (`src/services/mouse_service.py`)**
    *   Action:
        *   Create a class `MouseService`.
        *   Implement methods:
            *   `move_to_element(element_coords: dict, duration: float = 2.0)` - smooth mouse movement using PyAutoGUI.
            *   `click_element(element_coords: dict)` - click at calculated coordinates.
            *   `type_text(text: str)` - type text using PyAutoGUI.
            *   Helper method to calculate absolute screen coordinates from browser-relative coordinates.
    *   Outcome: Service for precise mouse control using PyAutoGUI.
*   **Task 3.4: Configuration Loading (`src/utils/config.py` or in `main.py` initially)**
    *   Action: Implement logic to load environment variables (e.g., API key, model names) using `python-dotenv` and `os.environ`.
    *   Outcome: Centralized configuration access.

## 4. Phase 3: Input and Output Modules

*   **Task 4.1: Text-to-Speech Module (`src/modules/tts_module.py`)**
    *   Action:
        *   Create a function `speak_text(text_to_speak: str)`.
        *   This function will use `GeminiService` to get audio data from Gemini TTS.
        *   Use `pyaudio` to play the received audio data.
        *   Handle `pyaudio` stream setup (format, channels, rate based on Gemini TTS output, typically 24kHz).
    *   Reference: `python_coding_standards.md` (modules), `mvp_scope.md` (Gemini TTS and `pyaudio`).
    *   Outcome: Application can speak text.

## 5. Phase 4: Q&A Module Development

*   **Task 5.1: PDF Context Management (Initial)**
    *   Action:
        *   Focus on using the Gemini File API. Upload the BA II Plus PDF.
        *   Develop a mechanism within `GeminiService` or `QAModule` to reference this uploaded file in prompts to Gemini.
    *   Reference: `mvp_scope.md` (PDF usage), Gemini File API documentation.
    *   Outcome: Ability to use PDF content with Gemini.
*   **Task 5.2: HTML Context**
    *   Action: Use the `BrowserService` to fetch the HTML content of the current calculator page.
    *   Outcome: HTML context is now sourced via Playwright.
*   **Task 5.3: Q&A Module Logic (`src/modules/qa_module.py`)**
    *   Action:
        *   Create a class `QAModule`.
        *   Method `answer_question(question: str, pdf_file_uri: str, html_content: Optional[str]) -> str`.
        *   Construct a prompt for Gemini incorporating the user's question, the PDF reference, and HTML context.
        *   Use `GeminiService` to get the answer.
        *   Incorporate the "AE Sales Rep" persona in the system prompt or user instructions to Gemini.
    *   Outcome: Core Q&A functionality.

## 6. Phase 5: Demonstration Module Development

*   **Task 6.1: Element Mapping and Selection Strategy (`src/modules/element_mapper.py`)**
    *   Action:
        *   Create a class `ElementMapper`.
        *   Define common calculator element selectors (buttons, display, input fields).
        *   Method `map_instruction_to_elements(instruction: str, html_content: str) -> List[Dict]` to identify which elements are needed for a given instruction.
        *   Use Gemini to help identify appropriate selectors based on instruction context and HTML structure.
    *   Outcome: Intelligent mapping between user instructions and calculator elements.
*   **Task 6.2: Demonstration Planning Logic (`src/modules/demonstration_module.py`)**
    *   Action:
        *   Create a class `DemonstrationModule`.
        *   Method `get_demonstration_plan(instruction: str, pdf_context: Optional[str], html_content: str) -> List[Dict]`.
        *   Prepare prompts for Gemini to:
            *   Analyze the user's instruction (e.g., "show me how to calculate IRR").
            *   Reference relevant PDF/HTML context.
            *   Return a structured JSON plan specifying:
                *   `type`: "voice" or "element_interaction".
                *   `content` (for voice): The text to be spoken.
                *   `action` (for element_interaction): "click" or "type".
                *   `element_selector`: CSS selector, XPath, or element description for `BrowserService` to locate.
                *   `value` (for type actions): The string to be typed.
                *   `timing`: Sequencing hints.
        *   Validate/parse the JSON response.
    *   Reference: `mvp_scope.md` (structured JSON output, but using element selectors instead of coordinates).
    *   Outcome: Ability to get a step-by-step plan with element selectors from Gemini.

## 7. Phase 6: Orchestrator and Main Application Loop

*   **Task 7.1: Orchestrator Logic (`src/core/orchestrator.py`)**
    *   Action:
        *   Create a class `Orchestrator`.
        *   Method `handle_user_request(user_input: str)`.
        *   Implement basic intent detection (e.g., keyword-based: "show me", "calculate" -> demonstration; "what is", "explain" -> Q&A).
        *   Instantiate and call appropriate modules (`QAModule`, `DemonstrationModule`).
    *   Outcome: Central control flow logic.
*   **Task 7.2: Main Application Loop (`src/main.py`)**
    *   Action:
        *   Initialize logging, configuration, `GeminiService`, and `BrowserService` (launch browser).
        *   Create instances of the `Orchestrator`, `TTSService`, `MouseService`, etc.
        *   Implement a loop to:
            *   Accept text input from the user (terminal).
            *   Pass input to the `Orchestrator`.
            *   If Q&A: Call `QAModule` (which uses `BrowserService` for HTML if needed), get answer, speak it.
            *   If Demonstration:
                *   Ensure `BrowserService` has the page loaded and ready.
                *   Get HTML content from `BrowserService`.
                *   Get demonstration plan (structured JSON with element selectors) from `DemonstrationModule`.
                *   Implement the "Output Execution Engine": 
                    *   Iterate through the plan.
                    *   For voice actions: Call `TTSService`.
                    *   For element interactions: Use `BrowserService` to locate elements and get coordinates, then `MouseService` to perform the actual mouse movements and clicks.
                    *   Respect timing hints and add appropriate delays.
    *   Outcome: A runnable MVP application with precise element-based mouse control.

## 8. Phase 7: Testing and Refinement

*   **Task 8.1: Unit Tests**
    *   Action: Write unit tests for key functions in `utils`, `services`, and `modules`. Mock external dependencies (especially `GeminiService` calls and `pyautogui`).
    *   Tool: `pytest`.
    *   Outcome: Core components are unit-tested.
*   **Task 8.2: Integration Tests (Basic)**
    *   Action: Write simple integration tests for the orchestrator flow (mocking actual Gemini calls but testing module interactions).
    *   Test the coordinate calculation logic with mock browser bounds and element positions.
    *   Outcome: Basic end-to-end flow tested.
*   **Task 8.3: Manual Testing and Iteration**
    *   Action: Thoroughly test various Q&A and demonstration scenarios. Refine prompts to Gemini for better element selector generation. Test coordinate accuracy and browser chrome offset calculations across different screen sizes.
    *   Outcome: MVP functionality verified and improved.

## 9. Phase 8: Documentation & Cleanup

*   **Task 9.1: Update `README.md`**
    *   Action: Add detailed setup, configuration, and usage instructions to the main `README.md`. Include MacOS accessibility permissions setup instructions.
    *   Outcome: Project is well-documented for users/developers.
*   **Task 9.2: Code Review and Refactoring**
    *   Action: Review code against `python_coding_standards.md`. Refactor for clarity, efficiency, and robustness. Ensure all type hints and docstrings are in place.
    *   Outcome: High-quality codebase.

## 10. Key Improvements Over Screenshot-Based Approach

*   **Precision**: Element coordinates are calculated exactly using Playwright's element detection rather than AI guessing from screenshots.
*   **Reliability**: No dependency on Gemini's visual analysis accuracy for coordinate detection.
*   **Robustness**: Element selectors can be more resilient to minor UI changes than pixel-perfect coordinates.
*   **Performance**: Faster execution without the need to capture, process, and analyze screenshots.
*   **Maintainability**: Element selectors can be updated/refined more easily than coordinate mappings.

## 11. Timeline (High-Level Estimate)

*   Phase 1-2: 2-3 days (Setup & Core Services)
*   Phase 3-4: 2-3 days (I/O Modules & Q&A)
*   Phase 5-6: 3-4 days (Demonstration Logic & Integration)
*   Phase 7-8: 2-3 days (Testing & Documentation)
*   **Total: ~10-13 days**

## 12. Future Enhancements (Post-MVP)

*   Whisper STT for voice input.
*   More sophisticated intent detection (e.g., using an NLU model).
*   Pure Playwright element interaction (clicking elements directly without PyAutoGUI).
*   Advanced context management for PDF/HTML (e.g., RAG with vector embeddings).
*   CI/CD pipeline (uncommented from `python_coding_standards.md`).
*   More complex conversational abilities.
*   Cross-platform support (Windows, Linux) with appropriate mouse control adaptations. 