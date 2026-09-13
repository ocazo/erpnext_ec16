#!/bin/bash
# Usage: ./run_imports.sh [site]
SITE="${1:-erp.local}"
bench --site "$SITE" execute erpnext_ec.patches.v16_0.import_tools.execute
