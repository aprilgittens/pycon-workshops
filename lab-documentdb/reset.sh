#!/bin/bash
# Resets DocumentDB workshop to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting DocumentDB workshop..."
git checkout -- lab-documentdb/
git clean -fd lab-documentdb/
echo "✅ DocumentDB workshop ready!"