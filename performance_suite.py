#!/usr/bin/env python3
"""
Command-line script to run the Performance Suite application.
"""

import os
import sys
import logging
from src.main import main

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/performance_suite.log"),
            logging.StreamHandler(),
        ]
    )
    
    # Run the main application
    sys.exit(main())
