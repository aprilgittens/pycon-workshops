#!/bin/bash
# Resets all workshops to their original state.
# Triggered automatically on codespace reload via postStartCommand.

echo "🔄 Resetting all workshops to clean state..."

bash workshop-1-quiz/reset.sh
# bash workshop-2-xxx/reset.sh
# bash workshop-3-xxx/reset.sh

echo "✅ All workshops ready to go!"