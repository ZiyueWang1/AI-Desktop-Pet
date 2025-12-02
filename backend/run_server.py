#!/usr/bin/env python3
"""
Backend entry point
Run backend server independently
"""
import os
import sys
from pathlib import Path

# Add project root directory to path (for importing src directory)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from app.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Starting API server on {host}:{port}")
    print(f"📝 API docs available at http://{host}:{port}/docs")
    
    if os.getenv('USE_MOCK_AI', 'false').lower() == 'true':
        print("✓ Using Mock AI Provider (no API tokens consumed)")
    
    uvicorn.run(app, host=host, port=port)

