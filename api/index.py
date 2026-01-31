import sys
import os

# Add the src directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from honeypot.main import create_app
    app = create_app()
except Exception as e:
    import traceback
    print("Error starting app:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise e

