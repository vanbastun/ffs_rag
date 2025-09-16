#!/usr/bin/env python3
"""Simple test runner for the project."""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests using pytest."""
    project_root = Path(__file__).parent.parent
    
    try:
        # Run pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], cwd=project_root, check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
