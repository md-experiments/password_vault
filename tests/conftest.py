import importlib.metadata
import werkzeug

# Flask 2.2.x references werkzeug.__version__ but Werkzeug >=3.0 removed it.
# Restore it so Flask's test client initialises correctly.
if not hasattr(werkzeug, '__version__'):
    werkzeug.__version__ = importlib.metadata.version('werkzeug')
