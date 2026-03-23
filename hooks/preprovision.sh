#!/usr/bin/env bash
set -euo pipefail

# ── Pre-provision hook ──────────────────────────────────────────────
# Queries Azure OpenAI quota and sets DEPLOYMENT_CAPACITY to the max
# available value before Bicep deployment begins.

LOCATION="${AZURE_LOCATION:-eastus}"
MODEL="gpt-4o"
QUOTA_NAME="OpenAI.Standard.${MODEL}"

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
