# Browser-Use Debugging Experiments

This folder contains scripts to debug connection errors when reusing browser contexts for sequential agent tasks.

## Experiments:

1.  **`experiment_about_blank.py`**:
    *   Tests if navigating to `about:blank` between agent tasks resolves the connection error.
    *   This ensures each new agent starts with a clean page state within the shared context.

2.  **`experiment_context_reuse_test.py`**:
    *   A minimal test to verify basic Playwright-level browser context reuse (creating pages, navigating) without the full `Agent` complexity.
    *   Helps determine if the issue is with fundamental context operations or with how the `Agent` class interacts with a reused context.

## Further Investigation (Idea #4):

*   Examine the `multiple_agents_same_browser.py` example (and other relevant examples) directly from the `browser-use` GitHub repository: [https://github.com/browser-use/browser-use/tree/main/examples](https://github.com/browser-use/browser-use/tree/main/examples)
*   Pay close attention to how they manage the lifecycle of agents and contexts when tasks are run sequentially using the same browser context.
*   They might employ specific patterns for "resetting" an agent or context that are not immediately obvious.
