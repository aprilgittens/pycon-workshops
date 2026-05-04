#!/bin/bash
# Resets workshop 1 to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting workshop 1..."
git checkout -- workshop-1-quiz/
git clean -fd workshop-1-quiz/
echo "✅ Workshop 1 ready!"
