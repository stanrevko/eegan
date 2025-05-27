#!/bin/bash

# Script to get all content from project files
echo "=== PROJECT CONTENT DUMP ==="
echo "Project: $(basename $(pwd))"
echo "Date: $(date)"
echo "================================"
echo

# Find all relevant files, excluding common ignore patterns
find . -type f \
  -not -path './.git/*' \
  -not -path './.eeg_data/*' \
  -not -path './__pycache__/*' \
  -not -path './venv/*' \
  -not -path './env/*' \
  -not -path './.venv/*' \
  -not -path './node_modules/*' \
  -not -path './.pytest_cache/*' \
  -not -path './build/*' \
  -not -path './dist/*' \
  -not -name '*.pyc' \
  -not -name '*.pyo' \
  -not -name '*.egg-info' \
  -not -name '.DS_Store' \
  -not -name '*.swp' \
  -not -name '*.swo' \
  -not -name '*~' \
  | sort | while read -r file; do
    echo "=== FILE: $file ==="
    if file "$file" | grep -q "text\|empty"; then
        cat "$file"
        echo
        echo "=== END OF $file ==="
        echo
    else
        echo "[Binary file - skipped]"
        echo "=== END OF $file ==="
        echo
    fi
done
