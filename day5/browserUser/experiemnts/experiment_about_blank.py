import os
import sys
from langchain_openai import ChatOpenAI
import asyncio

# Adjust the path to import browser_use if experiments is a sub-folder of browserUser
# Assuming browserUser is the parent of experiments, and browser_use is alongside or in sys.path
# If browserUser is /path/to/browserUser, and this file is /path/to/browserUser/experiments/experiment_about_blank.py
# And browser_use is in /path/to/browserUser (or installed in the environment)
# The following sys.path.append might need adjustment based on your exact structure
# For simplicity, if browser_use is installed, this might not be strictly needed.
# If browser-use is a local directory at the same level as 'experiments' parent, this is needed.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Agent, Browser

async def main():
    print("Starting experiment_about_blank.py")
    browser = Browser()
    try:
        async with await browser.new_context() as context:
            print("Browser context created.")
            model = ChatOpenAI(model='gpt-4o')
            agent_that_just_ran = None

            async def get_task_from_user():
                return await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input('Enter task (or "exit" to quit): ')
                )

            while True:
                task_description = await get_task_from_user()

                if task_description.lower() == 'exit':
                    if agent_that_just_ran:
                        print(f"Stopping agent from last task ('{agent_that_just_ran.task}') before exiting...")
                        try:
                            agent_that_just_ran.stop()
                        except Exception as e:
                            print(f"Error stopping agent on exit: {e}")
                    break

                if agent_that_just_ran:
                    print(f"Stopping agent from previous task ('{agent_that_just_ran.task}')...")
                    try:
                        agent_that_just_ran.stop()
                    except Exception as e:
                        print(f"Error stopping agent from previous task: {e}")
                    
                    print("Navigating to a blank page before starting the new agent...")
                    try:
                        if context.pages:
                            page_to_reset = context.pages[0]
                            await page_to_reset.goto("about:blank")
                            print(f"Successfully navigated page to about:blank. Current URL: {page_to_reset.url}")
                        else:
                            print("No active pages in context to reset. New agent will create a page.")
                    except Exception as e:
                        print(f"Error navigating to about:blank: {e}")
                
                print(f"Creating and running agent for task: '{task_description}'")
                current_agent = Agent(
                    task=task_description,
                    llm=model,
                    browser_context=context,
                )
                
                try:
                    await current_agent.run(max_steps=3)
                    print(f"Agent for task '{task_description}' has finished.")
                    agent_that_just_ran = current_agent
                except Exception as e:
                    print(f"Error during agent run for task '{task_description}': {e}")
                    # Decide if you want to stop the loop or the agent on error
                    agent_that_just_ran = None # Or try to stop current_agent

    except Exception as e:
        print(f"An unexpected error occurred in main execution: {e}")
    finally:
        print("Closing browser...")
        if browser:
            await browser.close()
        print("experiment_about_blank.py finished.")

if __name__ == "__main__":
    asyncio.run(main())
