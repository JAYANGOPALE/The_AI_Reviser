import sys
import os

# Add the project root/backend directory to sys.path to find the 'app' package
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, 'backend'))

from app import create_app

app = create_app()
