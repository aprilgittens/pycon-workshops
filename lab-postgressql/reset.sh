#!/bin/bash
# Resets PostgreSQL workshop to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting PostgreSQL workshop..."
git checkout -- lab-postgressql/
git clean -fd lab-postgressql/
echo "✅ PostgreSQL workshop ready!"