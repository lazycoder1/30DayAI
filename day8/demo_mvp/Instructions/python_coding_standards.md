# Python Coding Standards and Best Practices

## 1. Introduction

This document outlines the Python coding standards, best practices, and conventions to be followed for the AI Financial Calculator Assistant project. Adhering to these guidelines will ensure code quality, consistency, maintainability, and facilitate effective collaboration, particularly with AI-assisted development.

## 2. Project Structure

A clear and consistent project structure is crucial. We will adopt the following layout:

```
demo_mvp/
├── src/                     # Main source code
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── core/                # Core logic (orchestrator, intent detection)
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   ├── modules/             # Distinct functional modules
│   │   ├── __init__.py
│   │   ├── qa_module.py
│   │   ├── demonstration_module.py
│   │   ├── tts_module.py
│   │   └── mouse_control_module.py
│   ├── services/            # External service integrations (e.g., Gemini API client)
│   │   ├── __init__.py
│   │   └── gemini_service.py
│   │   └── browser_service.py
│   └── utils/               # Common utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                   # Unit and integration tests
│   ├── __init__.py
│   ├── core/
│   └── modules/
├── docs/                    # Project documentation (design docs, API docs if any)
│   └── ...
├── Instructions/            # Project-specific instructions, scope, standards
│   ├── mvp_scope.md
│   └── python_coding_standards.md
├── .env.example             # Example environment variables file
├── .gitignore
├── ruff.toml                # Ruff configuration
├── pyproject.toml           # Project metadata and dependencies (managed by Rye)
└── README.md                # Project overview and setup instructions
```

## 3. Modular Design

*   **Separation of Concerns:** Code will be organized into distinct modules and files based on functionality.
    *   `main.py`: Application entry point, basic setup.
    *   `core/`: Central logic like the orchestrator and intent detection.
    *   `modules/`: Specific functionalities like Q&A, demonstration control, TTS, mouse actions.
    *   `services/`: Wrappers or clients for external APIs (e.g., Gemini).
    *   `utils/`: Reusable helper functions that don't belong to a specific module.
*   **Encapsulation:** Modules should expose a clear API and hide internal implementation details.
*   **High Cohesion, Low Coupling:** Each module should have a single, well-defined responsibility, and dependencies between modules should be minimized.

## 4. Configuration Management

*   **Environment Variables:** All configuration parameters (API keys, model names, file paths, etc.) will be managed using environment variables.
*   **`.env` files:** A `.env` file (added to `.gitignore`) will be used for local development to store these variables.
*   **`.env.example`:** A `.env.example` file will be committed to the repository, listing all required environment variables with placeholder values.
*   **Loading Configuration:** Use a library like `python-dotenv` to load these variables at runtime, or access them directly using `os.environ`.

## 5. Error Handling and Logging

*   **Robust Error Handling:**
    *   Use `try-except` blocks to handle potential exceptions gracefully.
    *   Catch specific exceptions rather than generic `Exception`.
    *   Provide meaningful error messages.
    *   Define custom exceptions for application-specific errors if needed.
*   **Comprehensive Logging:**
    *   Use the built-in `logging` module.
    *   Configure log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    *   Log important events, decisions, errors, and context.
    *   Include timestamps, module names, and function names in log messages.
    *   **Context Capture:** When logging errors, include relevant contextual information (e.g., input parameters, state variables) to aid in debugging. This is especially important for AI to understand the failure.

## 6. Testing

*   **Framework:** `pytest` will be the standard testing framework.
*   **Test Coverage:** Aim for high test coverage for all critical components.
*   **Test Types:**
    *   **Unit Tests:** Test individual functions and classes in isolation.
    *   **Integration Tests:** Test the interaction between different modules.
*   **Test Location:** Tests will reside in the `tests/` directory, mirroring the `src/` structure.
*   **Assertions:** Use clear and descriptive assertions.
*   **Fixtures:** Utilize `pytest` fixtures for setting up and tearing down test resources.
*   **Mocking:** Use `unittest.mock` or `pytest-mock` for mocking external dependencies and services.

## 7. Documentation

*   **Docstrings:**
    *   All modules, classes, functions, and methods must have comprehensive docstrings.
    *   Follow a standard format (e.g., Google style, NumPy style, or reStructuredText). Specify argument types and return types.
    *   Example (Google Style):
        ```python
        def my_function(param1: int, param2: str) -> bool:
            """Does something interesting.

            Args:
                param1: The first parameter.
                param2: The second parameter.

            Returns:
                True if successful, False otherwise.

            Raises:
                ValueError: If param1 is negative.
            """
            if param1 < 0:
                raise ValueError("param1 cannot be negative")
            # ... function logic ...
            return True
        ```
*   **`README.md`:** The main `README.md` file should provide:
    *   A project overview.
    *   Setup and installation instructions (including Rye).
    *   Instructions on how to run the application.
    *   Information on running tests.
*   **Other Documentation:**
    *   Design documents, architectural decisions, and other relevant information can be stored in the `docs/` directory.
    *   The `Instructions/` directory will hold project planning documents like `mvp_scope.md` and this `python_coding_standards.md`.

## 8. Dependency Management

*   **Tool:** `Rye` (https://github.com/astral-sh/rye) will be used for managing Python versions, project dependencies, and virtual environments. It utilizes `uv` internally for fast packaging operations.
*   **`pyproject.toml`:** All project dependencies (direct and development) will be declared in `pyproject.toml` and managed by Rye (e.g., `google-generativeai`, `pyautogui`, `pyaudio`, `python-dotenv`, `playwright`).
*   **Virtual Environments:** Rye automatically manages virtual environments, ensuring isolated and reproducible builds.
*   **Lock File:** Rye uses a lock file (`requirements.lock`) to pin exact versions of all transitive dependencies, ensuring deterministic builds.

## 9. Code Style and Linting

*   **Linter/Formatter:** `Ruff` (https://github.com/astral-sh/ruff) will be used for linting and formatting to ensure code style consistency and identify potential issues.
*   **Configuration:** `Ruff` will be configured via `ruff.toml` (or `pyproject.toml` if preferred by Rye's integration).
*   **PEP 8:** Code should generally adhere to PEP 8, the style guide for Python code. Ruff will help enforce this.
*   **Line Length:** Aim for a maximum line length of 88-100 characters (configurable in Ruff).
*   **Imports:**
    *   Organize imports clearly: standard library, third-party, then local application imports.
    *   Ruff can automatically sort and group imports.

<!-- ## 10. CI/CD (Continuous Integration / Continuous Deployment)

*   **Platform:** GitHub Actions will be used for CI/CD.
*   **Workflow:** A basic CI workflow will be set up to:
    1.  Checkout code.
    2.  Set up Python using Rye.
    3.  Install dependencies.
    4.  Run Ruff for linting and formatting checks.
    5.  Run `pytest` for automated tests.
*   **Triggers:** The CI workflow will run on every push and pull request to the main branches. -->

## 11. AI-Friendly Coding Practices

To maximize the effectiveness of AI-assisted development (like with Gemini in Cursor):

*   **Descriptive Names:** Use clear, explicit, and descriptive names for variables, functions, classes, and modules. Avoid overly short or ambiguous names.
    *   Good: `user_input_text`, `calculate_net_present_value`
    *   Less Good: `txt`, `calc_npv`
*   **Type Hints:** Consistently use Python type hints for function arguments, return values, and variables. This significantly helps AI understand data structures and function signatures.
    ```python
    from typing import List, Dict

    def process_data(records: List[Dict[str, any]], threshold: float) -> List[str]:
        # ...
        pass
    ```
*   **Detailed Comments for Complex Logic:** While code should be self-documenting as much as possible, add comments to explain:
    *   Non-obvious logic or algorithms.
    *   Business rules or assumptions.
    *   The "why" behind a particular implementation choice if it's not clear.
*   **Rich Error Context:** As mentioned in Error Handling, ensure that exceptions and log messages provide enough context. This helps both humans and AI quickly understand the state of the program when an error occurred.
    ```python
    try:
        # ... some operation ...
    except KeyError as e:
        logging.error(f"Failed to find key '{e}' in configuration. Available keys: {config.keys()}")
        raise ConfigurationError(f"Missing required configuration key: {e}") from e
    ```
*   **Small, Focused Functions/Methods:** Break down complex operations into smaller, manageable functions that do one thing well. This makes the code easier for AI to analyze and modify.
*   **Explicit is Better than Implicit:** Make data flow and control flow as explicit as possible.

## 12. Version Control (Git)

*   **Commit Messages:** Write clear, concise, and informative commit messages. Follow conventional commit message formats if possible (e.g., `feat: add user login functionality`).
*   **Branching Strategy:** Use a feature branching strategy (e.g., Gitflow-lite). Create new branches for new features or bug fixes.
*   **Pull Requests:** Use pull requests for code reviews before merging into main branches.

## 13. Conclusion

These guidelines are intended to be a living document and may evolve as the project progresses. The primary goal is to write clean, understandable, and maintainable Python code that facilitates efficient development and collaboration. 