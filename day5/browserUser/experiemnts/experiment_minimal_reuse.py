import os
import sys
from langchain_openai import ChatOpenAI
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser

async def main():
    print("Starting experiment_minimal_reuse.py")
    browser = Browser()
    try:
        async with await browser.new_context() as context: # Single context for the whole session
            print("Browser context created.")
            model = ChatOpenAI(model='gpt-4o')
            
            # --- First Agent ---
            task1_description = "open online calculator"
            print(f"Creating and running agent for task 1: '{task1_description}'")
            agent1 = Agent(
                task=task1_description,
                llm=model,
                browser_context=context,
            )
            try:
                await agent1.run()
                print(f"Agent for task 1 '{task1_description}' has finished.")
            except Exception as e:
                print(f"Error during agent 1 run: {e}")
                return # Exit if first task fails

            # Attempt to stop agent1, as this seems to be the recommended practice
            print("Stopping agent 1...")
            try:
                agent1.stop() 
                print("Agent 1 stopped.")
            except Exception as e:
                print(f"Error stopping agent 1: {e}")

            print("-" * 30)
            input("Press Enter to start the second task (allows you to observe browser state)...")
            print("-" * 30)

            # --- Second Agent ---
            task2_description = "calculate 1 + 1 using the calculator" # Assuming calculator is open
            print(f"Creating and running agent for task 2: '{task2_description}'")
            agent2 = Agent(
                task=task2_description,
                llm=model,
                browser_context=context, # Reusing the same context
            )
            try:
                await agent2.run()
                print(f"Agent for task 2 '{task2_description}' has finished.")
            except Exception as e:
                print(f"Error during agent 2 run: {e}")
            
            # Attempt to stop agent2
            print("Stopping agent 2...")
            try:
                agent2.stop()
                print("Agent 2 stopped.")
            except Exception as e:
                print(f"Error stopping agent 2: {e}")

    except Exception as e:
        print(f"An unexpected error occurred in main execution: {e}")
    finally:
        print("Closing browser...")
        if browser:
            await browser.close()
        print("experiment_minimal_reuse.py finished.")

if __name__ == "__main__":
    asyncio.run(main())
