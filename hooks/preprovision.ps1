# ── Pre-provision hook ──────────────────────────────────────────────
# 1. Purges soft-deleted Cognitive Services accounts that block quota.
# 2. Queries Azure OpenAI quota and sets DEPLOYMENT_CAPACITY to the
#    max available value before Bicep deployment begins.

$ErrorActionPreference = "Stop"

$Location = if ($env:AZURE_LOCATION) { $env:AZURE_LOCATION } else { "eastus2" }
$Model = "gpt-4o"
$QuotaName = "OpenAI.GlobalStandard.$Model"

# ── Purge soft-deleted Cognitive Services accounts ──────────────────
Write-Host "==> Pre-provision: purging soft-deleted Cognitive Services accounts in $Location..."

$DeletedJson = az cognitiveservices account list-deleted `
    --query "[?location=='$Location'].{name:name, group:resourceGroup}" `
    -o json 2>$null

$Deleted = $DeletedJson | ConvertFrom-Json
$Count = if ($Deleted) { $Deleted.Count } else { 0 }

if ($Count -gt 0) {
    Write-Host "==> Found $Count soft-deleted account(s), purging..."
    foreach ($acct in $Deleted) {
        Write-Host "    Purging $($acct.name) (resource group: $($acct.group))..."
        az cognitiveservices account purge `
            --name $acct.name `
            --resource-group $acct.group `
            --location $Location 2>$null | Out-Null
    }
    Write-Host "    Done."
} else {
    Write-Host "==> No soft-deleted accounts found."
}

# ── Check quota and set capacity ───────────────────────────────────
Write-Host "==> Pre-provision: checking $Model quota in $Location..."

$QuotaJson = az cognitiveservices usage list `
    --location $Location `
    --query "[?name.value=='$QuotaName']" `
    -o json 2>$null

$QuotaData = $QuotaJson | ConvertFrom-Json

if ($QuotaData -and $QuotaData.Count -gt 0) {
    $Limit = [int]$QuotaData[0].limit
    $Used = [int]$QuotaData[0].currentValue
} else {
    $Limit = 0
    $Used = 0
}

$Available = $Limit - $Used

if ($Available -le 0) {
    Write-Host "ERROR: No available $Model quota in $Location (limit=$Limit, used=$Used)."
    exit 1
}

Write-Host "==> Quota: limit=$Limit, used=$Used, available=$Available"
Write-Host "==> Setting DEPLOYMENT_CAPACITY=$Available"

azd env set DEPLOYMENT_CAPACITY "$Available"
