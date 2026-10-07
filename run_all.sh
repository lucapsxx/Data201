#!/bin/bash
# Runs the three pipeline scripts in order.
# Stops immediately if any one of them fails (non-zero exit code).
set -e

echo "=== Running deliverable4 Fran ==="
python3 "deliverable4 Fran"

echo "=== Running deliverable5 Fran ==="
python3 "deliverable5 Fran"

echo "=== Running combining datasets ==="
python3 "combining datasets"

echo "=== All three scripts finished successfully ==="
