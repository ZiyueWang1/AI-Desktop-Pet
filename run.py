#!/usr/bin/env python3
"""
Main entry point for AI Desktop Pet application
Supports dual modes:
- GUI mode: Desktop application (client, calls backend API)
- API mode: FastAPI server (backend, for K8s deployment)
"""
import os
import sys

# Check running mode
if os.getenv('API_MODE') == 'true' or '--api' in sys.argv:
    # API mode: Start FastAPI server (backend)
    from backend.app.main import app
    import uvicorn
    
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Starting API server mode on {host}:{port}")
    print(f"📝 API docs available at http://{host}:{port}/docs")
    
    # Check if Mock mode is explicitly enabled
    use_mock_env = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'
    if use_mock_env:
        print("⚠ Mock mode enabled via USE_MOCK_AI environment variable")
    else:
        print("✓ Mock mode disabled - will use real AI providers if API keys are configured")
    
    uvicorn.run(app, host=host, port=port)
else:
    # GUI mode: Start desktop application (client)
    # Add client/src and subdirectories to path (support absolute imports)
    client_src_path = os.path.join(os.path.dirname(__file__), 'client', 'src')
    client_presentation_path = os.path.join(client_src_path, 'presentation')
    client_infrastructure_path = os.path.join(client_src_path, 'infrastructure')
    
    # Add all necessary paths
    sys.path.insert(0, client_presentation_path)
    sys.path.insert(0, client_infrastructure_path)
    sys.path.insert(0, client_src_path)
    
    # Direct import (main.py already handles relative import compatibility)
    from main import DesktopPetApp
    
    app = DesktopPetApp()
    app.run()
