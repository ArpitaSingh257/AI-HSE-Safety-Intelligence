"""
run_audit.py - Scratch runner to execute audit_lsr_data_coverage.py and capture output.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.audit_lsr_data_coverage import run_full_lsr_audit

if __name__ == "__main__":
    run_full_lsr_audit()
