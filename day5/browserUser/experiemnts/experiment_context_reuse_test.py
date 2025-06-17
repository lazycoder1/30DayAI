import asyncio
import os
import sys

# Adjust path if necessary, similar to experiment_about_blank.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_use import Browser # Assuming Browser is the main entry point from browser_use

async def test_context_reuse():
    print("Starting experiment_context_reuse_test.py")
    browser = Browser()
    try:
        async with await browser.new_context() as context:
            print("Browser context created for initial use.")
            page1 = await context.new_page()
            await page1.goto("https://www.google.com")
            print(f"Initial page (page1) URL: {page1.url}")
            print(f"Number of pages in context: {len(context.pages)}")

            # Simulate first operation finishing
            print("Simulating first operation finishing.")
            # await page1.close() # Optional: Test closing the page

            # Simulate second operation reusing the same context
            print("Simulating second operation reusing the context.")
            
            if context.pages:
                # Try to use an existing page if available
                page2 = context.pages[0] 
                print(f"Reusing existing page (page2). Current URL: {page2.url}")
                await page2.goto("https://www.bing.com")
                print(f"Navigated reused page (page2) to Bing. New URL: {page2.url}")
            else:
                # If no pages (e.g., if page1 was closed and it was the only one)
                print("No existing pages in context, creating a new one for second operation.")
                page2_new = await context.new_page()
                await page2_new.goto("https://www.bing.com")
                print(f"Created new page (page2_new) in context. URL: {page2_new.url}")
            
            print(f"Number of pages in context after second operation: {len(context.pages)}")
            print("Context reuse test appears successful.")

    except Exception as e:
        print(f"Error during context reuse test: {e}")
    finally:
        print("Closing browser...")
        if browser:
            await browser.close()
        print("experiment_context_reuse_test.py finished.")

if __name__ == "__main__":
    asyncio.run(test_context_reuse())
