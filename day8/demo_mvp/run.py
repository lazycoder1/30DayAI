#!/usr/bin/env python3

"""
Entry point script for the AI Financial Calculator Assistant.
Run this from the demo_mvp directory to start the application.
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import and run the main function
from src.main import main

if __name__ == "__main__":
    main() 