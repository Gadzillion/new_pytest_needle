import os
from pathlib import Path

PROJECT_DIR = str(Path(__file__).parent.parent.parent.parent.parent.parent)
PJ = os.path.realpath(os.path.join(os.getcwd()))
STAND_CONFIG_DIR = os.path.join(PROJECT_DIR, "config")
