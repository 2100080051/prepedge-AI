# PrepEdge AI - Azure Deployment PowerShell Script for Windows

# ============================================================================
# Azure Deployment Script for PrepEdge AI
# ============================================================================
# Usage: powershell -ExecutionPolicy Bypass -File azure-deploy.ps1

param(
    [string]$Environment = "prod",
    [string]$Location = "eastus",
    [string]$SkipDeploy = $false
)

# Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# ============================================================================
# Configuration
# ============================================================================

$ResourceGroup = "prepedge-ai-$Environment"
$ProjectName = "prepedge"
$BackendAppName = "prepedge-api"
$FrontendAppName = "prepedge-web"
$AppPlanName = "prepedge-plan-$Environment"
$DBName = "prepedge-db-$Environment"
$RedisName = "prepedge-cache-$Environment"
$VaultName = "prepedge-kv-$Environment"
$InsightsName = "prepedge-insights-$Environment"

# ============================================================================
# Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "$Blue========================================$Reset"
    Write-Host "$Blue$Message$Reset"
    Write-Host "$Blue========================================$Reset"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Green✓ $Message$Reset"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$Yellow→ $Message$Reset"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "$Red✗ $Message$Reset"
}

function Check-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Azure CLI
    $azExist = $null -ne (Get-Command az -ErrorAction SilentlyContinue)
    if (-not $azExist) {
        Write-Error-Custom "Azure CLI is not installed"
        Write-Host "Download from: https://docs.microsoft.com/cli/azure/install-azure-cli-windows"
        exit 1
    }
    
    Write-Success "Azure CLI installed"
    
    # Check Git
    $gitExist = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    if (-not $gitExist) {
        Write-Error-Custom "Git is not installed"
        exit 1
    }
    
    Write-Success "Git installed"
}

function Login-To-Azure {
    Write-Info "Logging in to Azure..."
    az login | Out-Null
    
    $account = az account show --query "name" -o tsv
    Write-Success "Logged in as: $account"
}

function Create-ResourceGroup {
    Write-Info "Creating resource group: $ResourceGroup..."
    
    $exists = az group exists --name $ResourceGroup --query "value" -o tsv
    
    if ($exists -eq "true") {
        Write-Success "Resource group already exists"
    } else {
        az group create `
            --name $ResourceGroup `
            --location $Location `
            --tags "Environment=$Environment" "Project=PrepEdgeAI" | Out-Null
        
        Write-Success "Resource group created"
    }
}

function Deploy-Infrastructure {
    Write-Info "Deploying infrastructure..."
    
    az deployment group create `
        --resource-group $ResourceGroup `
        --template-file "azure-infrastructure.json" `
        --parameters `
            environment=$Environment `
            location=$Location `
            appServicePlanSku="B2" `
            databaseSku="Standard_B2s" `
            redisSku="Basic" | Out-Null
    
    Write-Success "Infrastructure deployed"
}

function Setup-KeyVault {
    Write-Info "Setting up Key Vault..."
    
    # Generate secret key
    $bytes = [System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)
    $secretKey = [Convert]::ToBase64String($bytes)
    
    # Store secrets
    az keyvault secret set `
        --vault-name $VaultName `
        --name "secret-key" `
        --value $secretKey | Out-Null
    
    Write-Success "Key Vault configured"
    
    Write-Host ""
    Write-Host "$Yellow⚠️  IMPORTANT: Add these secrets to Key Vault:$Reset"
    Write-Host "  - openai-api-key"
    Write-Host "  - sendgrid-api-key"
    Write-Host "  - razorpay-key-id"
    Write-Host "  - razorpay-key-secret"
    Write-Host ""
}

function Get-AppIdentity {
    param([string]$AppName)
    
    $identity = az webapp identity show `
        --resource-group $ResourceGroup `
        --name $AppName `
        --query "principalId" -o tsv
    
    return $identity
}

function Grant-KeyVaultAccess {
    Write-Info "Granting Key Vault access to App Services..."
    
    # Backend
    $backendId = Get-AppIdentity -AppName $BackendAppName
    az keyvault set-policy `
        --vault-name $VaultName `
        --object-id $backendId `
        --secret-permissions get list | Out-Null
    
    # Frontend
    $frontendId = Get-AppIdentity -AppName $FrontendAppName
    az keyvault set-policy `
        --vault-name $VaultName `
        --object-id $frontendId `
        --secret-permissions get list | Out-Null
    
    Write-Success "Key Vault access granted"
}

function Configure-AppServices {
    Write-Info "Configuring App Services..."
    
    # Backend
    az webapp config appsettings set `
        --resource-group $ResourceGroup `
        --name $BackendAppName `
        --settings `
            ENVIRONMENT=$Environment `
            DEBUG="false" `
            WEBSITES_PORT="8000" | Out-Null
    
    # Frontend
    az webapp config appsettings set `
        --resource-group $ResourceGroup `
        --name $FrontendAppName `
        --settings `
            NEXT_TELEMETRY_DISABLED="1" `
            NODE_ENV="production" `
            NEXT_PUBLIC_API_URL="https://$BackendAppName.azurewebsites.net/api/v1" | Out-Null
    
    Write-Success "App Services configured"
}

function Output-Summary {
    Write-Header "Deployment Summary"
    
    $backendHost = az webapp show `
        --resource-group $ResourceGroup `
        --name $BackendAppName `
        --query "defaultHostName" -o tsv
    
    $frontendHost = az webapp show `
        --resource-group $ResourceGroup `
        --name $FrontendAppName `
        --query "defaultHostName" -o tsv
    
    Write-Host "$Green✓ Backend API:$Reset https://$backendHost"
    Write-Host "$Green✓ Frontend Web:$Reset https://$frontendHost"
    Write-Host "$Green✓ Resource Group:$Reset $ResourceGroup"
    Write-Host ""
    
    Write-Host "$Yellow📋 Next Steps:$Reset"
    Write-Host "  1. Update GoDaddy DNS records"
    Write-Host "  2. Configure custom domains in Azure Portal"
    Write-Host "  3. Add secrets to Key Vault"
    Write-Host "  4. Setup GitHub secrets for CI/CD"
    Write-Host "  5. Push code to deploy"
    Write-Host ""
}

# ============================================================================
# Main Execution
# ============================================================================

Write-Header "PrepEdge AI - Azure Deployment"
Write-Host "Environment: $Yellow$Environment$Reset"
Write-Host "Location: $Yellow$Location$Reset"
Write-Host ""

# Run checks
Check-Prerequisites
Login-To-Azure

if ($SkipDeploy -ne $true) {
    # Deploy
    Create-ResourceGroup
    Deploy-Infrastructure
    Setup-KeyVault
    Grant-KeyVaultAccess
    Configure-AppServices
    
    # Output results
    Output-Summary
    
    Write-Success "Azure deployment completed successfully!"
} else {
    Write-Info "Deployment skipped (SkipDeploy = true)"
}
