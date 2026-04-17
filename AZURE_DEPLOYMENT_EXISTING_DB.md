# PrepEdge AI - Azure Deployment Guide (Using Existing Database)

## 📋 Overview

This guide deploys PrepEdge AI to Azure using your **existing PostgreSQL database**:
- **Server:** prepedge-db-primary-sea.postgres.database.azure.com
- **Database:** postgres (or your existing database name)
- **User:** prepedge_admin

We will NOT create a new database - we'll use what you already have.

## 🎯 Architecture

```
Your Existing Database (prepedge-db-primary-sea)
              ↓
        Azure App Services
        ↙                ↘
    Backend API      Frontend Web
    (FastAPI)        (Next.js)
         ↓                ↓
    api.prepedgeai.in  prepedgeai.in
         ↓                ↓
    GoDaddy Domain Management
```

---

## 🔧 Part 1: Setup Existing Database Connection

### 1.1 Database Details You Already Have

```
Server: prepedge-db-primary-sea.postgres.database.azure.com
User: prepedge_admin
Password: Nani2906#
Port: 5432
Database Name: postgres (or your existing db)
SSL Mode: require
```

### 1.2 Verify Database Connection

From your local machine:

```powershell
# Install PostgreSQL client (if not already installed)
# Download from: https://www.postgresql.org/download/

# Test connection
$env:PASSWORD = "Nani2906#"
psql -h prepedge-db-primary-sea.postgres.database.azure.com `
     -U prepedge_admin `
     -d postgres `
     -c "SELECT version();"

# You should see PostgreSQL version info
```

### 1.3 Configure Firewall Rules (If Needed)

Your database might already have these, but verify:

```powershell
# Allow Azure Services
$resourceGroup = "your-existing-rg"  # Where your database lives
$serverName = "prepedge-db-primary-sea"

az postgres server firewall-rule create `
  --resource-group $resourceGroup `
  --server $serverName `
  --name "AllowAzureServices" `
  --start-ip-address "0.0.0.0" `
  --end-ip-address "0.0.0.0"
```

---

## 📱 Part 2: Create App Services (New Infrastructure Only)

### 2.1 Create Resource Group for New Services

```powershell
# Variables
$newResourceGroup = "prepedge-ai-prod-services"
$location = "southeastasia"  # Same as existing database
$environment = "prod"

# Create new resource group (only for App Services)
az group create `
  --name $newResourceGroup `
  --location $location `
  --tags Environment=$environment Project=PrepEdgeAI
```

### 2.2 Create App Service Plan

```powershell
$appPlanName = "prepedge-appservice-plan"

az appservice plan create `
  --name $appPlanName `
  --resource-group $newResourceGroup `
  --sku B2 `
  --is-linux
```

### 2.3 Create Backend App Service

```powershell
$backendAppName = "prepedge-api-prod"

az webapp create `
  --resource-group $newResourceGroup `
  --plan $appPlanName `
  --name $backendAppName `
  --runtime "python|3.11"

# Configure settings
az webapp config appsettings set `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --settings `
    ENVIRONMENT="production" `
    DEBUG="false" `
    WEBSITES_PORT="8000" `
    DATABASE_URL="postgresql://prepedge_admin:Nani2906%23@prepedge-db-primary-sea.postgres.database.azure.com:5432/postgres?sslmode=require" `
    REDIS_URL="redis://your-redis-connection:6379/0" `
    SECRET_KEY="your-super-secret-key-min-32-chars" `
    RESEND_API_KEY="your-resend-key"

# Enable HTTPS only
az webapp update `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --set httpsOnly=true
```

### 2.4 Create Frontend App Service

```powershell
$frontendAppName = "prepedge-web-prod"

az webapp create `
  --resource-group $newResourceGroup `
  --plan $appPlanName `
  --name $frontendAppName `
  --runtime "node|18-lts"

# Configure settings
az webapp config appsettings set `
  --resource-group $newResourceGroup `
  --name $frontendAppName `
  --settings `
    NEXT_TELEMETRY_DISABLED="1" `
    NODE_ENV="production" `
    NEXT_PUBLIC_API_URL="https://$backendAppName.azurewebsites.net/api/v1"

# Enable HTTPS only
az webapp update `
  --resource-group $newResourceGroup `
  --name $frontendAppName `
  --set httpsOnly=true
```

---

## 🌐 Part 3: Configure GoDaddy Domain

### 3.1 Get Azure App Hostnames

```powershell
# Get backend hostname
$backendHost = az webapp show `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --query "defaultHostName" -o tsv

# Get frontend hostname  
$frontendHost = az webapp show `
  --resource-group $newResourceGroup `
  --name $frontendAppName `
  --query "defaultHostName" -o tsv

Write-Host "Backend: $backendHost"
Write-Host "Frontend: $frontendHost"
```

### 3.2 Update GoDaddy DNS Records

Log in to **GoDaddy** → **Domains** → **prepedgeAI.in** → **DNS Management**

Add these CNAME records:

| Name | Type | Value | TTL |
|------|------|-------|-----|
| `api` | CNAME | `prepedge-api-prod.azurewebsites.net` | 3600 |
| `www` | CNAME | `prepedge-web-prod.azurewebsites.net` | 3600 |
| `@` (root) | CNAME | `prepedge-web-prod.azurewebsites.net` | 3600 |

### 3.3 Wait for DNS Propagation

```powershell
# Check DNS propagation (wait 10-30 minutes)
nslookup api.prepedgeai.in
nslookup prepedgeai.in
```

---

## 🔗 Part 4: Configure Custom Domains in Azure

### 4.1 Add Custom Domain to Backend

1. **Azure Portal** → **App Service** → `prepedge-api-prod`
2. Navigate to **Settings** → **Custom domains**
3. Click **Add custom domain**
4. Enter: `api.prepedgeai.in`
5. Validation method: **CNAME record validation**
6. Click **Add custom domain**
7. Wait for validation
8. SSL binding automatically created (Azure-managed certificate)

### 4.2 Add Custom Domain to Frontend

1. **Azure Portal** → **App Service** → `prepedge-web-prod`
2. Navigate to **Settings** → **Custom domains**
3. Click **Add custom domain**
4. Enter: `prepedgeai.in`
5. Validation method: **CNAME record validation**
6. Click **Add custom domain**
7. Wait for validation
8. SSL binding automatically created

Also add `www.prepedgeai.in` and redirect to main domain.

---

## 📦 Part 5: Deploy Application Code

### 5.1 Deploy Backend

```powershell
# Navigate to backend
cd backend

# Create deployment package
Compress-Archive -Path . -DestinationPath "..\backend.zip" -Force

# Deploy to Azure
az webapp deployment source config-zip `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --src "..\backend.zip"

# Or use Git deployment
git push azure main
```

### 5.2 Deploy Frontend

```powershell
# Navigate to frontend
cd ../frontend

# Install and build
npm ci
npm run build

# Create deployment package
Compress-Archive -Path .next, public, node_modules, package.json `
  -DestinationPath "..\frontend.zip" -Force

# Deploy to Azure
az webapp deployment source config-zip `
  --resource-group $newResourceGroup `
  --name $frontendAppName `
  --src "..\frontend.zip"
```

### 5.3 Run Database Migrations (If Needed)

```powershell
# SSH into backend app service
az webapp ssh `
  --resource-group $newResourceGroup `
  --name $backendAppName

# Run migrations (if you have migration scripts)
alembic upgrade head

# Exit SSH
exit
```

---

## ✅ Part 6: Verification

### 6.1 Test API Health

```powershell
# Test health endpoint
curl https://api.prepedgeai.in/api/v1/health

# Expected response:
# {"status":"ok","timestamp":"2026-04-18T...","environment":"production"}
```

### 6.2 Test Frontend

```powershell
# Test web app
curl https://prepedgeai.in

# Should return HTML content
```

### 6.3 Check Database Connection

From your app service, verify the database connection is working:

```powershell
# SSH into backend
az webapp ssh `
  --resource-group $newResourceGroup `
  --name $backendAppName

# Test database connection
python3 << 'EOF'
import os
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("✓ Database connection successful!")
EOF

exit
```

### 6.4 Monitor in Azure Portal

1. **App Service** → **Monitoring** → **Metrics**
2. View CPU, Memory, HTTP Request metrics
3. Check **Logs** for any errors

---

## 🔐 Security Configuration (Existing Database)

### 6.1 Verify Firewall Rules

Your existing database should have these rules:

```powershell
# Check existing firewall rules
az postgres server firewall-rule list `
  --resource-group "your-existing-rg" `
  --server "prepedge-db-primary-sea"

# Ensure this rule exists:
# AllowAzureServices: 0.0.0.0 - 0.0.0.0
```

### 6.2 Verify SSL Requirement

```powershell
# Check SSL enforcement (should already be ON)
az postgres server show `
  --resource-group "your-existing-rg" `
  --name "prepedge-db-primary-sea" `
  --query "sslEnforcement"

# Output should be: ENABLED
```

### 6.3 App Service Security

Already configured:
- ✅ HTTPS only enabled
- ✅ TLS 1.2 minimum
- ✅ Custom domain with SSL certificate

### 6.4 Connection String Safety

**IMPORTANT:** The DATABASE_URL is stored in App Service Configuration. To be extra secure:

1. Move DATABASE_URL to Azure Key Vault
2. Reference it as a Key Vault secret in App Service settings
3. This prevents accidental exposure in logs

```powershell
# Create Key Vault (if not existing)
$vaultName = "prepedge-kv-prod"

az keyvault create `
  --name $vaultName `
  --resource-group $newResourceGroup `
  --location $location

# Store database connection string
az keyvault secret set `
  --vault-name $vaultName `
  --name "database-url" `
  --value "postgresql://prepedge_admin:Nani2906%23@prepedge-db-primary-sea.postgres.database.azure.com:5432/postgres?sslmode=require"

# Grant app access to Key Vault
$appId = az webapp identity show `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --query "principalId" -o tsv

az keyvault set-policy `
  --vault-name $vaultName `
  --object-id $appId `
  --secret-permissions get list

# Update app setting to reference Key Vault
az webapp config appsettings set `
  --resource-group $newResourceGroup `
  --name $backendAppName `
  --settings `
    DATABASE_URL="@Microsoft.KeyVault(VaultName=$vaultName;SecretName=database-url)"
```

---

## 📊 Cost Analysis

### Current Usage (Your Existing Database)

| Service | Details | Cost |
|---------|---------|------|
| PostgreSQL | prepedge-db-primary-sea (existing) | Already being paid |
| Redis | (if using) | Already existing |

### New Services Being Added

| Service | SKU | Estimated Cost |
|---------|-----|-----------------|
| App Service Plan | B2 | $50/month |
| Application Insights | Pay-as-you-go | $10-20/month |
| Storage (static files) | Hot tier | $5/month |
| **New Monthly Total** | | **~$65-75/month** |

### No Additional Database Costs
✅ Using existing database - no new charges for PostgreSQL

---

## 🔄 Maintenance & Monitoring

### Weekly Tasks

1. **Check Application Health**
   ```powershell
   curl https://api.prepedgeai.in/api/v1/health
   ```

2. **Review Logs**
   ```powershell
   az webapp log tail `
     --resource-group $newResourceGroup `
     --name $backendAppName
   ```

3. **Monitor Your Existing Database**
   - CPU usage
   - Storage usage
   - Connection count

### Monthly Tasks

1. Backup your database (if not auto-enabled)
2. Review Azure cost
3. Update dependencies
4. Security audit

---

## 🚀 Summary of Changes Needed

✅ **No Database Changes Required** - Using existing database
✅ Create new Azure App Service Plan
✅ Create Backend App Service
✅ Create Frontend App Service
✅ Update GoDaddy DNS records
✅ Configure custom domains in Azure
✅ Deploy application code
✅ Verify everything works

---

## ⚡ Quick Checklist

- [ ] Database connection verified
- [ ] Azure App Services created
- [ ] GoDaddy DNS records updated
- [ ] Custom domains configured in Azure
- [ ] DNS propagated (10-30 minutes)
- [ ] Backend deployed and running
- [ ] Frontend deployed and running
- [ ] HTTPS certificates activated
- [ ] Health check endpoints responding
- [ ] Database connection confirmed from app

---

## 📞 Troubleshooting

### Database Connection Failed
```powershell
# Verify connection string
echo "DATABASE_URL=postgresql://prepedge_admin:Nani2906%23@prepedge-db-primary-sea.postgres.database.azure.com:5432/postgres?sslmode=require"

# Test from local machine
psql -h prepedge-db-primary-sea.postgres.database.azure.com `
     -U prepedge_admin `
     -d postgres `
     -c "SELECT 1"
```

### App Service Not Starting
```powershell
# Check logs
az webapp log tail `
  --resource-group $newResourceGroup `
  --name $backendAppName

# Restart app
az webapp restart `
  --resource-group $newResourceGroup `
  --name $backendAppName
```

### DNS Not Resolving
```powershell
# Wait for propagation
nslookup api.prepedgeai.in

# Check with Google DNS
nslookup api.prepedgeai.in 8.8.8.8
```

---

**Your PrepEdge AI is now deployed with your existing database!** 🎉
