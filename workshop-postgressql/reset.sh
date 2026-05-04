#!/bin/bash
# Resets PostgreSQL workshop to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting PostgreSQL workshop..."
git checkout -- workshop-postgressql/
git clean -fd workshop-postgressql/
echo "✅ PostgreSQL workshop ready!"