#!/bin/bash
# Runs the three pipeline scripts in order.
# Stops immediately if any one of them fails (non-zero exit code).
#chmod +x RunFull.sh
#./RunFull.sh

set -e
echo "=== Running merge listings Fran ==="
python3 "D7_MergeData.py"

echo "=== Running deliverable4 Fran ==="
python3 "D4_airbnb_Clean.py"

echo "=== Running deliverable5 Fran ==="
python3 "D5_GetAreaCodes.py"

echo "=== Running combining datasets ==="
python3 "combining datasets and plots"

echo "=== All 4 scripts finished successfully ==="
