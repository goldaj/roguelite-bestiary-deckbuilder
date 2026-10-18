# tests/conftest.py
import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))