import sys
import os

# Add the src directory to the system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set environment variables for serverless
os.environ.setdefault('PYTHONPATH', os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from honeypot.main import create_app
    app = create_app()
    
    # For Vercel, we need to expose the app as 'app'
    # This is the ASGI application that Vercel will use
    
except ImportError as e:
    import traceback
    print(f"Import error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def fallback():
        return {"error": "Failed to import main application", "details": str(e)}
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": "Import failed"}

except Exception as e:
    import traceback
    print("Error starting app:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
    # Create a minimal fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def fallback():
        return {"error": "Failed to start application", "details": str(e)}
    
    @app.get("/health")
    async def health():
        return {"status": "error", "message": "Startup failed"}

