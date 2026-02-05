#!/usr/bin/env python3
"""
Start the Agentic Honeypot Server
Ensures proper environment setup and starts the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the Python path and environment variables."""
    # Get the project root directory
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # Add src to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(src_path) not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{src_path}{os.pathsep}{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = str(src_path)
    
    print(f"✅ Python path configured: {src_path}")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"✅ Environment file found: {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'), 
        ('pydantic', 'pydantic'),
        ('python-dotenv', 'dotenv'),
        ('google-generativeai', 'google.generativeai'),
        ('openai', 'openai'),
        ('anthropic', 'anthropic'),
        ('requests', 'requests')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Missing packages: {missing}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies are installed")
    return True

def test_app_creation():
    """Test if the app can be created successfully."""
    try:
        from honeypot.main import create_app
        app = create_app()
        print("✅ Application created successfully")
        
        # List available routes
        print("\n📋 Available endpoints:")
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  {methods} {route.path}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create application: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_server():
    """Start the FastAPI server using uvicorn."""
    print("\n🚀 Starting Agentic Honeypot Server...")
    print("=" * 50)
    
    try:
        # Import and run the server
        import uvicorn
        from honeypot.main import create_app
        
        app = create_app()
        
        print("Server starting on http://0.0.0.0:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Health Check: http://localhost:8000/health")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production-like behavior
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to set up and start the server."""
    print("🍯 AGENTIC HONEYPOT SERVER STARTUP 🍯")
    print("=" * 50)
    
    # Step 1: Setup environment
    setup_environment()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return 1
    
    # Step 3: Test app creation
    if not test_app_creation():
        print("\n❌ Application setup failed")
        return 1
    
    # Step 4: Start the server
    start_server()
    
    return 0

if __name__ == "__main__":
    exit(main())