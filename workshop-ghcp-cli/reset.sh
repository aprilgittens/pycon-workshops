#!/bin/bash
# Resets GitHub Copilot CLI workshop to its original state.
# Called by reset-all.sh on codespace reload.

echo "🔄 Resetting GitHub Copilot CLI workshop..."
git checkout -- workshop-ghcp-cli/
git clean -fd workshop-ghcp-cli/
echo "✅ GitHub Copilot CLI workshop ready!"
