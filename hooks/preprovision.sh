#!/usr/bin/env bash
set -euo pipefail

# ── Pre-provision hook ──────────────────────────────────────────────
# 1. Purges soft-deleted Cognitive Services accounts that block quota.
# 2. Queries Azure OpenAI quota and sets DEPLOYMENT_CAPACITY to the
#    max available value before Bicep deployment begins.

LOCATION="${AZURE_LOCATION:-eastus}"
MODEL="gpt-4o"
QUOTA_NAME="OpenAI.Standard.${MODEL}"

# ── Purge soft-deleted Cognitive Services accounts ──────────────────
# After `azd down` or `az group delete`, accounts enter a soft-delete
# state that still consumes quota. Purge them to reclaim capacity.
echo "==> Pre-provision: purging soft-deleted Cognitive Services accounts in ${LOCATION}..."

DELETED=$(az cognitiveservices account list-deleted \
  --query "[?location=='${LOCATION}'].{name:name, group:resourceGroup}" \
  -o json 2>/dev/null)

COUNT=$(echo "${DELETED}" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

if [ "${COUNT}" -gt 0 ]; then
  echo "==> Found ${COUNT} soft-deleted account(s), purging..."
  echo "${DELETED}" | python3 -c "
import sys, json, subprocess
for acct in json.load(sys.stdin):
    name, rg = acct['name'], acct['group']
    print(f'    Purging {name} (resource group: {rg})...')
    subprocess.run([
        'az', 'cognitiveservices', 'account', 'purge',
        '--name', name, '--resource-group', rg, '--location', '${LOCATION}'
    ], capture_output=True)
print('    Done.')
"
else
  echo "==> No soft-deleted accounts found."
fi

# ── Check quota and set capacity ───────────────────────────────────
echo "==> Pre-provision: checking ${MODEL} quota in ${LOCATION}..."

QUOTA_JSON=$(az cognitiveservices usage list \
  --location "${LOCATION}" \
  --query "[?name.value=='${QUOTA_NAME}']" \
  -o json 2>/dev/null)

LIMIT=$(echo "${QUOTA_JSON}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(int(d[0]['limit']) if d else 0)")
USED=$(echo "${QUOTA_JSON}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(int(d[0]['currentValue']) if d else 0)")
AVAILABLE=$((LIMIT - USED))

if [ "${AVAILABLE}" -le 0 ]; then
  echo "ERROR: No available ${MODEL} quota in ${LOCATION} (limit=${LIMIT}, used=${USED})."
  exit 1
fi

echo "==> Quota: limit=${LIMIT}, used=${USED}, available=${AVAILABLE}"
echo "==> Setting DEPLOYMENT_CAPACITY=${AVAILABLE}"

azd env set DEPLOYMENT_CAPACITY "${AVAILABLE}"
