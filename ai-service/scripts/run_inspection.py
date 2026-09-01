"""
run_inspection.py - Runs inspect_lsr_data.py and prints output.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.inspect_lsr_data import inspect_lsr

if __name__ == "__main__":
    inspect_lsr()
