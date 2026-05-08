#!/bin/bash
# Resets all workshops to their original state.
# Triggered automatically on codespace reload via postStartCommand.

echo "🔄 Resetting all workshops to clean state..."

bash lab-ghcp-cli/reset.sh
bash lab-documentdb/reset.sh
bash lab-postgressql/reset.sh

echo "✅ All workshops ready to go!"