#!/bin/bash
# Resets DocumentDB workshop to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting DocumentDB workshop..."
git checkout -- workshop-documentdb/
git clean -fd workshop-documentdb/
echo "✅ DocumentDB workshop ready!"