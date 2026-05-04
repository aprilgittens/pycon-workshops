#!/bin/bash
# Resets all workshops to their original state.
# Triggered automatically on codespace reload via postStartCommand.

echo "🔄 Resetting all workshops to clean state..."

bash workshop-ghcp-cli/reset.sh
bash workshop-documentdb/reset.sh
bash workshop-postgressql/reset.sh

echo "✅ All workshops ready to go!"