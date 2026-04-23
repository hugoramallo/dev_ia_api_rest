#!/bin/bash
INPUT=$(cat)
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('input','')))" 2>/dev/null)

LOG_FILE=".github/hooks/logs/audit.log"
mkdir -p .github/hooks/logs
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$TIMESTAMP | INPUT: $TOOL_INPUT" >> "$LOG_FILE"

# Bloquear git push
if echo "$TOOL_INPUT" | grep -q "git push"; then
  echo '{"decision": "deny", "reason": "git push bloqueado. Revisa el diff antes de hacer push."}'
  exit 0
fi

echo '{"decision": "approve"}'