#!/usr/bin/env python3
"""
Client entry point
Run client independently
"""
import os
import sys
from pathlib import Path

# Add src directory to path
client_src = Path(__file__).parent / "src"
sys.path.insert(0, str(client_src))

# Now can import
from main import DesktopPetApp

if __name__ == "__main__":
    # Set default API address
    if not os.getenv("API_BASE_URL"):
        os.environ["API_BASE_URL"] = "http://localhost:8080"
    
    app = DesktopPetApp()
    app.run()

