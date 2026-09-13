#!/bin/bash
# Usage: ./run_patch_custom_fields.sh [site]
SITE="${1:-erp.local}"
bench --site "$SITE" execute erpnext_ec.patches.v16_0.custom_fields.rename_old_columns
