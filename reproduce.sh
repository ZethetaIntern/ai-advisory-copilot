#!/usr/bin/env bash
set -euo pipefail
echo "=== Zeckathon PS04: AI Advisory Co-pilot ==="
echo "=== Reproducing all results ==="

# Install dependencies
pip install -r requirements.txt

# Download data (uses cache if available)
python scripts/download_data.py

# Run all tests
pytest tests/ -v --tb=short

# Generate all reports and numbers
python scripts/reproduce.py

echo "=== All results reproduced. See reports/ directory ==="
