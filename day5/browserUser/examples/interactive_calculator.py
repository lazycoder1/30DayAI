#!/usr/bin/env python
import sys
import os

# Add the parent directory to sys.path to allow imports from multi_step_browser
# This is for running the example directly without installing the package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from multi_step_browser.automator import BrowserAutomator # type: ignore

# NOTE: Selectors are specific to Google's calculator (search "calculator" on Google).
# You may need to inspect the calculator website you choose and update these selectors.
# Common selectors for Google Calculator (may change):
# - Numbers: //div[text()="1"] (for '1'), etc.
# - Operators: //div[text()="+"] (for '+'), etc.
# - Equals: //div[text()="="]
# - Result display: #cwos
# - Clear/AC: //div[text()="AC"]

CALCULATOR_URL = "https://www.google.com/search?q=calculator"

def print_help():
    print("\nInteractive Calculator Commands:")
    print("  navigate <url>         - Navigate to a new URL (default is Google Calculator)")
    print("  click <selector>       - Click an element (e.g., 'click //div[text()=\"7\"]')")
    print("  fill <selector> <text> - Fill an input field (less common for this calculator)")
    print("  text <selector>        - Get text from an element (e.g., 'text #cwos')")
    print("  clear                  - Clicks the 'AC' (All Clear) button on Google's calculator")
    print("  eval <js_expression>   - Evaluate JavaScript in the page context and print the result.")
    print("                           (e.g., 'eval document.title')")
    print("  help                   - Show this help message")
    print("  quit                   - Exit the interactive session")
    print("\nExample Google Calculator Selectors:")
    print("  Numbers: //div[text()='1'] (for '1'), //div[text()='2'] (for '2'), etc.")
    print("  Operators: //div[text()='+'] (for '+'), //div[text()='−'] (for '-'), //div[text()='×'] (for '*'), //div[text()='÷'] (for '/')")
    print("  Equals: //div[text()='=']")
    print("  Result display: #cwos")
    print("  Clear (AC): //div[text()='AC']")

def run_interactive_calculator():
    print("Starting interactive browser session...")
    # Using headless=False and slow_mo to see the browser actions.
    # You can change these settings as needed.
    with BrowserAutomator(browser_type="chromium", headless=False, slow_mo=100) as automator:
        agent = automator.new_agent()
        print(f"Navigating to Google Calculator: {CALCULATOR_URL}")
        agent.navigate(CALCULATOR_URL)
        print("Calculator loaded. Type 'help' for commands.")

        while True:
            try:
                command_input = input("Enter command: ").strip()
                if not command_input:
                    continue

                parts = command_input.split(maxsplit=2)
                action = parts[0].lower()

                if action == "quit":
                    print("Exiting...")
                    break
                elif action == "help":
                    print_help()
                elif action == "navigate":
                    if len(parts) > 1:
                        url = parts[1]
                        print(f"Navigating to: {url}")
                        agent.navigate(url)
                    else:
                        print("Usage: navigate <url>")
                elif action == "click":
                    if len(parts) > 1:
                        selector = parts[1]
                        print(f"Clicking: {selector}")
                        agent.click(selector)
                    else:
                        print("Usage: click <selector>")
                elif action == "fill":
                    if len(parts) > 2:
                        selector = parts[1]
                        text_to_fill = parts[2]
                        print(f"Filling '{selector}' with '{text_to_fill}'")
                        agent.fill(selector, text_to_fill)
                    else:
                        print("Usage: fill <selector> <text>")
                elif action == "text":
                    if len(parts) > 1:
                        selector = parts[1]
                        retrieved_text = agent.get_text(selector)
                        print(f"Text from '{selector}': {retrieved_text}")
                    else:
                        print("Usage: text <selector>")
                elif action == "clear":
                    # Specific to Google Calculator's AC button
                    clear_selector = "//div[text()='AC']"
                    print(f"Clicking AC button: {clear_selector}")
                    agent.click(clear_selector)
                elif action == "eval":
                    if len(parts) > 1:
                        js_expression = parts[1]
                        print(f"Evaluating JavaScript: {js_expression}")
                        result = agent.page.evaluate(js_expression)
                        print(f"JS Result: {result}")
                    else:
                        print("Usage: eval <js_expression>")
                else:
                    print(f"Unknown command: {action}. Type 'help' for options.")
            
            except Exception as e:
                print(f"An error occurred: {e}")
                print("You can try 'clear' or check your selector.")

if __name__ == "__main__":
    run_interactive_calculator() 