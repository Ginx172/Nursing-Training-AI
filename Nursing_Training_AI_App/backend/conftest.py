import sys
import os

# Ensure the backend directory is in sys.path so imports like
# "from main import app" and "from core.xxx import yyy" work
sys.path.insert(0, os.path.dirname(__file__))
