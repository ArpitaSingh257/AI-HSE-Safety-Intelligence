"""
run_test_direct.py - Directly executes pytest for test_lsr_trend_analytics.py and prints output.
"""
import pytest
import sys

if __name__ == "__main__":
    res = pytest.main(["-v", "tests/test_lsr_trend_analytics.py"])
    sys.exit(res)
