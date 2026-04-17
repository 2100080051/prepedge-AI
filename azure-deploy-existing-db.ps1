# PrepEdge AI - Azure Deployment for Existing Database
# This script deploys to Azure using your EXISTING database
# No new database will be created

param(
    [string]$Environment = "prod",
    [string]$Location = "southeastasia"
)

# ============================================================================
# Configuration - USING EXISTING DATABASE
# ============================================================================

# NEW Resource Group for App Services only
$ResourceGroupApps = "prepedge-ai-prod-services"
$ProjectName = "prepedge"
$BackendAppName = "prepedge-api-prod"
$FrontendAppName = "prepedge-web-prod"
$AppPlanName = "prepedge-appservice-plan"

# EXISTING Database Details (DO NOT CHANGE)
$ExistingDBHost = "prepedge-db-primary-sea.postgres.database.azure.com"
$ExistingDBUser = "prepedge_admin"
$ExistingDBPassword = "Nani2906#"
$ExistingDBName = "postgres"

# Other settings from .env
$ResendAPIKey = "re_5arQBmoM_BMnmLy6N9dzWEQoUbJ4WTYio"
$ResendFromEmail = "noreply@prepedge.io"
$PollinationsAPIKey = "pk_EbH2wym2aXzDZkfl"

# ============================================================================
# Colors for Output
# ============================================================================

$Colors = @{
    Green = "`e[32m"
    Yellow = "`e[33m"
    Red = "`e[31m"
    Blue = "`e[34m"
    Reset = "`e[0m"
}

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "$($Colors.Blue)========================================$($Colors.Reset)"
    Write-Host "$($Colors.Blue)$Message$($Colors.Reset)"
    Write-Host "$($Colors.Blue)========================================$($Colors.Reset)"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "$($Colors.Green)✓ $Message$($Colors.Reset)"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$($Colors.Yellow)→ $Message$($Colors.Reset)"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "$($Colors.Red)✗ $Message$($Colors.Reset)"
}

function Verify-Prerequisites {
    Write-Info "Verifying prerequisites..."
    
    $azExist = $null -ne (Get-Command az -ErrorAction SilentlyContinue)
    if (-not $azExist) {
        Write-Error-Custom "Azure CLI is not installed"
        exit 1
    }
    
    Write-Success "Azure CLI installed"
}

function Login-Azure {
    Write-Info "Logging in to Azure..."
    az login | Out-Null
    
    $account = az account show --query "name" -o tsv
    Write-Success "Logged in as: $account"
}

function Create-AppServiceResourceGroup {
    Write-Info "Creating App Service resource group: $ResourceGroupApps..."
    
    $exists = az group exists --name $ResourceGroupApps --query "value" -o tsv
    
    if ($exists -eq "true") {
        Write-Success "Resource group already exists"
    } else {
        az group create `
            --name $ResourceGroupApps `
            --location $Location `
            --tags "Environment=$Environment" "Project=PrepEdgeAI" | Out-Null
        
        Write-Success "Resource group created"
    }
}

function Create-AppServicePlan {
    Write-Info "Creating App Service Plan: $AppPlanName..."
    
    az appservice plan create `
        --name $AppPlanName `
        --resource-group $ResourceGroupApps `
        --sku B2 `
        --is-linux | Out-Null
    
    Write-Success "App Service Plan created"
}

function Create-BackendAppService {
    Write-Info "Creating Backend App Service: $BackendAppName..."
    
    # Create app
    az webapp create `
        --resource-group $ResourceGroupApps `
        --plan $AppPlanName `
        --name $BackendAppName `
        --runtime "python|3.11" | Out-Null
    
    # Build connection string with escaped password
    $escapedPassword = [System.Web.HttpUtility]::UrlEncode($ExistingDBPassword)
    $databaseUrl = "postgresql://${ExistingDBUser}:${escapedPassword}@${ExistingDBHost}:5432/${ExistingDBName}?sslmode=require"
    
    # Configure settings
    Write-Info "Configuring Backend app settings..."
    
    az webapp config appsettings set `
        --resource-group $ResourceGroupApps `
        --name $BackendAppName `
        --settings `
            ENVIRONMENT=$Environment `
            DEBUG="false" `
            WEBSITES_PORT="8000" `
            DATABASE_URL=$databaseUrl `
            RESEND_API_KEY=$ResendAPIKey `
            RESEND_FROM_EMAIL=$ResendFromEmail `
            POLLINATIONS_API_KEY=$PollinationsAPIKey | Out-Null
    
    # Enable HTTPS
    az webapp update `
        --resource-group $ResourceGroupApps `
        --name $BackendAppName `
        --set httpsOnly=true | Out-Null
    
    Write-Success "Backend App Service configured"
}

function Create-FrontendAppService {
    Write-Info "Creating Frontend App Service: $FrontendAppName..."
    
    # Create app
    az webapp create `
        --resource-group $ResourceGroupApps `
        --plan $AppPlanName `
        --name $FrontendAppName `
        --runtime "node|18-lts" | Out-Null
    
    # Configure settings
    Write-Info "Configuring Frontend app settings..."
    
    $backendUrl = "https://${BackendAppName}.azurewebsites.net/api/v1"
    
    az webapp config appsettings set `
        --resource-group $ResourceGroupApps `
        --name $FrontendAppName `
        --settings `
            NEXT_TELEMETRY_DISABLED="1" `
            NODE_ENV="production" `
            NEXT_PUBLIC_API_URL=$backendUrl | Out-Null
    
    # Enable HTTPS
    az webapp update `
        --resource-group $ResourceGroupApps `
        --name $FrontendAppName `
        --set httpsOnly=true | Out-Null
    
    Write-Success "Frontend App Service configured"
}

function Test-DatabaseConnection {
    Write-Info "Testing connection to EXISTING database..."
    
    $escapedPassword = [System.Web.HttpUtility]::UrlEncode($ExistingDBPassword)
    $psqlConnString = "postgresql://${ExistingDBUser}:${escapedPassword}@${ExistingDBHost}:5432/${ExistingDBName}?sslmode=require"
    
    Write-Host ""
    Write-Host "$($Colors.Yellow)To test database connection manually, use:$($Colors.Reset)"
    Write-Host "psql -h $ExistingDBHost -U $ExistingDBUser -d $ExistingDBName -c 'SELECT version();'"
    Write-Host ""
    Write-Host "$($Colors.Yellow)After you have psql installed and connected, type password: Nani2906#$($Colors.Reset)"
    Write-Host ""
    
    Write-Success "Database connection string configured in App Service"
}

function Output-Summary {
    Write-Header "Deployment Summary"
    
    $backendHost = az webapp show `
        --resource-group $ResourceGroupApps `
        --name $BackendAppName `
        --query "defaultHostName" -o tsv
    
    $frontendHost = az webapp show `
        --resource-group $ResourceGroupApps `
        --name $FrontendAppName `
        --query "defaultHostName" -o tsv
    
    Write-Host "$($Colors.Green)✓ Backend API:$($Colors.Reset) https://$backendHost"
    Write-Host "$($Colors.Green)✓ Frontend Web:$($Colors.Reset) https://$frontendHost"
    Write-Host "$($Colors.Green)✓ Resource Group:$($Colors.Reset) $ResourceGroupApps"
    Write-Host "$($Colors.Green)✓ Using Existing Database:$($Colors.Reset) $ExistingDBHost"
    Write-Host ""
    
    Write-Host "$($Colors.Yellow)IMPORTANT - Next Steps:$($Colors.Reset)"
    Write-Host "  1. Verify database firewall allows Azure Services:"
    Write-Host "     - Check: https://portal.azure.com → Your existing database → Networking"
    Write-Host ""
    Write-Host "  2. Update GoDaddy DNS records (prepedgeAI.in):"
    Write-Host "     - api CNAME → $backendHost"
    Write-Host "     - www CNAME → $frontendHost"
    Write-Host "     - @ (root) CNAME → $frontendHost"
    Write-Host ""
    Write-Host "  3. Wait for DNS propagation (10-30 minutes)"
    Write-Host ""
    Write-Host "  4. Configure custom domains in Azure Portal:"
    Write-Host "     - Backend: api.prepedgeai.in"
    Write-Host "     - Frontend: prepedgeai.in"
    Write-Host ""
    Write-Host "  5. Deploy application code:"
    Write-Host "     - Push to GitHub or use 'git push azure main'"
    Write-Host ""
    Write-Host "  6. Verify deployment:"
    Write-Host "     - curl https://api.prepedgeai.in/api/v1/health"
    Write-Host "     - curl https://prepedgeai.in"
    Write-Host ""
}

# ============================================================================
# Main Execution
# ============================================================================

Write-Header "PrepEdge AI - Azure Deployment (Using EXISTING Database)"
Write-Host "Resource Group (NEW): $($Colors.Yellow)$ResourceGroupApps$($Colors.Reset)"
Write-Host "Location: $($Colors.Yellow)$Location$($Colors.Reset)"
Write-Host "Database (EXISTING): $($Colors.Yellow)$ExistingDBHost$($Colors.Reset)"
Write-Host "Database User: $($Colors.Yellow)$ExistingDBUser$($Colors.Reset)"
Write-Host ""

# Run deployment steps
Verify-Prerequisites
Login-Azure
Create-AppServiceResourceGroup
Create-AppServicePlan
Create-BackendAppService
Create-FrontendAppService
Test-DatabaseConnection
Output-Summary

Write-Success "Azure deployment COMPLETED successfully!"
Write-Host ""
Write-Host "$($Colors.Yellow)⚠️  Remember to update GoDaddy DNS records before testing!$($Colors.Reset)"
