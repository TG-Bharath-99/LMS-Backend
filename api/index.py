import sys
import os

# Add project root to path so Backend package can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.main import app