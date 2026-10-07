#!/bin/bash
# Runs the three pipeline scripts in order.
# Stops immediately if any one of them fails (non-zero exit code).
#chmod +x run_all.sh
#./run_all.sh

set -e
echo "=== Running merge listings Fran ==="
python3 "merge listings"

echo "=== Running Cleaning Fran ==="
python3 "Cleaning"

echo "=== Running Get area codes Fran ==="
python3 "Get Area Codes"

echo "=== Running combining datasets ==="
python3 "combining datasets and plots"

echo "=== All three scripts finished successfully ==="
