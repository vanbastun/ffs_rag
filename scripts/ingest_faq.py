#!/usr/bin/env python3
"""Script to ingest FAQ data into Qdrant"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.workers.ingest import main

if __name__ == "__main__":
    print("Starting FAQ ingestion...")
    main()
