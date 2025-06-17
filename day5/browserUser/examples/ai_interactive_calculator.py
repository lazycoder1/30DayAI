#!/usr/bin/env python
import sys
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow imports from multi_step_browser
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from multi_step_browser.automator import BrowserAutomator # type: ignore # noqa
from multi_step_browser.agent import AgentSession # type: ignore # noqa

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not found in .env file.")
    print("Please create a .env file in the project root with your OpenAI API key.")
    print("Example: OPENAI_API_KEY=\"your_openai_api_key_here\"")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)
AI_MODEL = "gpt-4o" # Or "gpt-4" or other compatible chat model

CALCULATOR_URL = "https://www.google.com/search?q=calculator"

# --- Prompts and AI Interaction ---

SYSTEM_PROMPT = f"""
You are an AI assistant that translates natural language commands into a sequence of specific actions for controlling a web browser focused on a calculator page.
The user is interacting with the Google Calculator ({CALCULATOR_URL}).

You MUST respond with a JSON object containing a single key "commands", which is a list of action objects.
Each action object in the list will be executed sequentially.
Possible actions and their parameters for each object in the "commands" list are:

1.  "click": Requires a "selector" (string, CSS or XPath).
    Example for a single command: {{\"action\": "click", "selector": "//div[text()=\\\'7\\\']"}}
2.  "text": Requires a "selector" (string, CSS or XPath). This is used to read text from an element.
    Example: {{\"action\": "text", "selector": "#cwos"}}
3.  "navigate": Requires a "url" (string).
    Example: {{\"action\": "navigate", "url": "https://www.google.com/search?q=scientific+calculator"}}
    (Note: Google Calculator might dynamically show scientific buttons. Navigating might not always be needed if it's already on the main calculator page).
4.  "fill": Requires a "selector" (string) and "text_to_fill" (string). (Less common for this calculator)
    Example: {{\"action\": "fill", "selector": "#someInput", "text_to_fill": "hello"}}
5.  "eval": Requires a "js_expression" (string).
    Example: {{\"action\": "eval", "js_expression": "document.title"}}
6.  "noop": If the user's command is unclear, a greeting, or doesn't map to any actions.
    The "commands" list can be empty or contain a single noop action.
    Example: {{\"action\": "noop", "reason": "User said hello."}}
7.  "quit": If the user wants to exit. This should be the only command in the list.
    Example: {{\"action\": "quit"}}

Example of a multi-step user command "add 1 + 1 and show result":
{{
  "commands": [
    {{"action": "click", "selector": "//div[text()=\\\'1\\\']"}},
    {{"action": "click", "selector": "//div[text()=\\\'+\\\']"}},
    {{"action": "click", "selector": "//div[text()=\\\'1\\\']"}},
    {{"action": "click", "selector": "//div[text()=\\\'=\\\']"}},
    {{"action": "text", "selector": "#cwos"}}
  ]
}}

Common Selectors for Google Calculator (use these if applicable):
- Numbers '0' through '9': //div[@role='button' and text()="0"], ..., //div[@role='button' and text()="9"]
- Decimal point '.': //div[@role='button' and text()="." ]
- Operators:
    - Add: //div[@role='button' and text()="+"]
    - Subtract: //div[@role='button' and text()="−"] (Note: this is a minus sign, not a hyphen)
    - Multiply: //div[@role='button' and text()="×"]
    - Divide: //div[@role='button' and text()="÷"]
- Equals: //div[@role='button' and text()="="]
- Result display: #cwos (preferred), or .XHsqValues span.vUGUtc, or //span[@id='cwos']
- Clear (AC - All Clear): //div[@role='button' and text()="AC"]
- Clear Entry (CE): //div[@role='button' and text()="CE"]

Scientific Functions (Google calculator often shows these when relevant, or in a wider layout):
- Parentheses: //div[@role='button' and text()="("] and //div[@role='button' and text()=")"]
- Square root: //div[@role='button' and text()="√"]
- Pi (π): //div[@role='button' and text()="π"]
- Euler's number (e): //div[@role='button' and text()="e"]
- Power (x^y): //div[@role='button' and text()="xy"]
- sin, cos, tan: //div[@role='button' and text()="sin"], //div[@role='button' and text()="cos"], //div[@role='button' and text()="tan"]
- ln (natural log): //div[@role='button' and text()="ln"]
- log (base 10 log): //div[@role='button' and text()="log"]
- Inverse (1/x): //div[@role='button' and text()="1/x"]
- Percentage (%): //div[@role='button' and text()="%"]

Interpret complex commands by breaking them into a sequence of these actions.
For "what's the result?" or "get the display", use the "text" action with selector "#cwos".
For "clear" or "AC", use the "click" action with selector for "AC".
If the user asks to use a "scientific calculator", the current page ({CALCULATOR_URL}) should suffice as it dynamically shows scientific buttons. You can directly use selectors for scientific functions if needed.
If the user says "quit", "exit", or "bye", respond with a "commands" list containing a single "quit" action.
Always respond with a valid JSON object with the "commands" key. If no action is to be taken, "commands" can be an empty list or contain one "noop" action.
"""

def get_ai_commands_list(user_input: str) -> list[dict]:
    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2, # Lower temperature for more deterministic output
            response_format={"type": "json_object"}
        )
        response_content = completion.choices[0].message.content
        if response_content:
            # print(f"AI Raw Response: {response_content}") # For debugging
            data = json.loads(response_content)
            return data.get("commands", []) # Expect a list under "commands"
        return [{"action": "noop", "reason": "Empty response from AI."}]
    except json.JSONDecodeError as e:
        print(f"Error decoding AI response: {e}")
        print(f"AI Raw Output: {response_content if 'response_content' in locals() else 'Unavailable'}")
        return [{"action": "noop", "reason": "AI response was not valid JSON."}]
    except Exception as e:
        print(f"Error getting command from AI: {e}")
        return [{"action": "noop", "reason": f"API error: {str(e)}"}]

def run_ai_calculator():
    print("Starting AI-powered interactive browser session...")
    print(f"Make sure your OPENAI_API_KEY is set in a .env file and the model '{AI_MODEL}' is accessible.")
    
    with BrowserAutomator(browser_type="chromium", headless=False, slow_mo=200) as automator:
        agent: AgentSession = automator.new_agent()
        print(f"Navigating to Google Calculator: {CALCULATOR_URL}")
        agent.navigate(CALCULATOR_URL)
        print("Calculator loaded. Type your commands in natural language (e.g., 'press 7', 'add 5', 'what is the result?', 'quit').")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("Exiting...")
                    break

                ai_commands = get_ai_commands_list(user_input)
                print(f"AI Plan: {ai_commands}")

                if not ai_commands:
                    print("AI: No actions planned.")
                    continue

                for command_index, ai_command_data in enumerate(ai_commands):
                    action = ai_command_data.get("action", "noop").lower()
                    selector = ai_command_data.get("selector")
                    
                    print(f"Executing step {command_index + 1}/{len(ai_commands)}: {action.upper()} {selector if selector else ''}")

                    try:
                        if action == "quit":
                            print("Exiting as per AI suggestion...")
                            return
                        elif action == "noop":
                            reason = ai_command_data.get("reason", "AI decided no action needed.")
                            print(f"AI: {reason}")
                            continue
                        elif action == "navigate":
                            url = ai_command_data.get("url")
                            if url:
                                print(f"  Navigating to: {url}")
                                agent.navigate(url)
                            else:
                                print("  AI suggested navigation but no URL provided.")
                                raise ValueError("Missing URL for navigate action")
                        elif action == "click":
                            if selector:
                                print(f"  Clicking: {selector}")
                                agent.click(selector)
                            else:
                                print("  AI suggested click but no selector provided.")
                                raise ValueError("Missing selector for click action")
                        elif action == "fill":
                            text_to_fill = ai_command_data.get("text_to_fill")
                            if selector and text_to_fill is not None:
                                print(f"  Filling '{selector}' with '{text_to_fill}'")
                                agent.fill(selector, text_to_fill)
                            else:
                                print("  AI suggested fill but selector or text was missing.")
                                raise ValueError("Missing selector or text for fill action")
                        elif action == "text":
                            if selector:
                                retrieved_text = agent.get_text(selector)
                                print(f"  Text from '{selector}': {retrieved_text}")
                                # TODO: Optionally, feed this result back to the AI for context in subsequent LLM calls if needed.
                            else:
                                print("  AI suggested text but no selector provided.")
                                raise ValueError("Missing selector for text action")
                        elif action == "eval":
                            js_expression = ai_command_data.get("js_expression")
                            if js_expression:
                                print(f"  Evaluating JavaScript: {js_expression}")
                                result = agent.page.evaluate(js_expression)
                                print(f"  JS Result: {result}")
                            else:
                                print("  AI suggested eval but no expression provided.")
                                raise ValueError("Missing expression for eval action")
                        else:
                            print(f"  Unknown action from AI: {action}")
                            # Potentially raise an error or just skip
                    except Exception as e:
                        print(f"Error executing AI step: {ai_command_data}")
                        print(f"Error details: {e}")
                        print("Stopping current sequence of AI commands.")
                        break
                
            except Exception as e:
                print(f"An error occurred in the main loop: {e}")
                print("You can try again, or type 'quit' to exit.")

if __name__ == "__main__":
    run_ai_calculator() 