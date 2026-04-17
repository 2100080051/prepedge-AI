# Azure Deployment Scripts - Using Existing Database

This directory contains automated deployment scripts for PrepEdge AI that use your **existing PostgreSQL database** in Azure without creating a new one.

## 📋 Scripts Overview

### PowerShell Script
**File:** `azure-deploy-existing-db.ps1`  
**Best for:** Windows users or Windows PowerShell 5.1+

```powershell
# Basic usage
.\azure-deploy-existing-db.ps1

# With custom location
.\azure-deploy-existing-db.ps1 -Location "eastus" -Environment "prod"
```

### Bash Script
**File:** `azure-deploy-existing-db.sh`  
**Best for:** Linux, macOS, or Windows with WSL

```bash
# Basic usage (Linux/macOS)
chmod +x azure-deploy-existing-db.sh
./azure-deploy-existing-db.sh

# With custom parameters
./azure-deploy-existing-db.sh southeastasia prod
```

## 🎯 What These Scripts Do

✅ **Creates NEW resources:**
- Resource group for App Services: `prepedge-ai-prod-services`
- App Service Plan (B2 tier - suitable for production)
- Backend FastAPI App Service: `prepedge-api-prod`
- Frontend Next.js App Service: `prepedge-web-prod`

❌ **Does NOT create:**
- PostgreSQL database (uses your **existing** database)
- Additional infrastructure (Key Vault, Storage, etc.)

✅ **Configures:**
- Database connection string pointing to: `prepedge-db-primary-sea.postgres.database.azure.com`
- Environment variables (RESEND_API_KEY, POLLINATIONS_API_KEY, etc.)
- HTTPS enforcement
- Proper runtime versions (Python 3.11, Node.js 18 LTS)

## 📋 Prerequisites

Before running these scripts, ensure you have:

1. **Azure CLI installed**
   - [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
   
2. **Azure account with subscription**
   - Active subscription with billing enabled
   - Your existing PostgreSQL database accessible

3. **Required permissions**
   - Owner or Contributor role for the subscription

4. **GoDaddy domain**
   - Domain: `prepedgeAI.in`
   - Ability to modify DNS records

## 🚀 Quick Start

### Step 1: Verify Prerequisites

```powershell
# Check Azure CLI
az version

# Login to Azure
az login
```

### Step 2: Run the Deployment Script

**Windows (PowerShell):**
```powershell
cd "c:\Users\srisa\Downloads\prepedge AI"
.\azure-deploy-existing-db.ps1
```

**Linux/macOS/WSL:**
```bash
cd ~/Downloads/prepedge\ AI
chmod +x azure-deploy-existing-db.sh
./azure-deploy-existing-db.sh
```

### Step 3: Wait for Completion

The script will:
1. ✅ Create resource group
2. ✅ Create App Service Plan
3. ✅ Create Backend App Service
4. ✅ Create Frontend App Service
5. ✅ Configure all settings
6. ✅ Display summary with endpoints

Expected runtime: **5-10 minutes**

### Step 4: Update GoDaddy DNS Records

After the script completes, you'll see output like:
```
✓ Backend API: https://prepedge-api-prod.azurewebsites.net
✓ Frontend Web: https://prepedge-web-prod.azurewebsites.net
```

Go to your GoDaddy domain management and add CNAME records:

| Type | Name | Value |
|------|------|-------|
| CNAME | api | prepedge-api-prod.azurewebsites.net |
| CNAME | www | prepedge-web-prod.azurewebsites.net |
| CNAME | @ (root) | prepedge-web-prod.azurewebsites.net |

**Wait 10-30 minutes for DNS propagation.**

### Step 5: Configure Custom Domains in Azure

Once DNS records propagate:

1. **For Backend API:**
   - Go to Azure Portal → prepedge-api-prod → Custom domains
   - Add domain: `api.prepedgeai.in`
   - Azure will auto-verify via CNAME
   - SSL certificate issued automatically

2. **For Frontend:**
   - Go to Azure Portal → prepedge-web-prod → Custom domains
   - Add domain: `prepedgeai.in`
   - Azure will auto-verify via CNAME
   - SSL certificate issued automatically

### Step 6: Deploy Application Code

Push your repository to GitHub to trigger the CI/CD pipeline:

```bash
git push origin main
```

Or use Azure deployment:
```bash
az webapp up --name prepedge-api-prod --resource-group prepedge-ai-prod-services
```

### Step 7: Verify Deployment

Test your endpoints:

```bash
# Backend health check
curl https://api.prepedgeai.in/api/v1/health

# Frontend web
curl https://prepedgeai.in
```

## 🔧 Configuration Details

### Database Configuration

The scripts automatically configure your App Services with:

```
Database Host: prepedge-db-primary-sea.postgres.database.azure.com
Database User: prepedge_admin
Database Name: postgres
Connection String: postgresql://prepedge_admin:Nani2906#@prepedge-db-primary-sea.postgres.database.azure.com:5432/postgres?sslmode=require
```

**⚠️ Important:** Ensure your database firewall allows connections from Azure App Services:
1. Go to Azure Portal
2. Navigate to your PostgreSQL server
3. Click "Networking" → "Firewall rules"
4. Enable "Allow Azure services and resources to access this server"

### Environment Variables Set by Script

**Backend App Service:**
- `ENVIRONMENT`: prod
- `DEBUG`: false
- `WEBSITES_PORT`: 8000
- `DATABASE_URL`: [Your database connection string]
- `RESEND_API_KEY`: [From .env]
- `RESEND_FROM_EMAIL`: [From .env]
- `POLLINATIONS_API_KEY`: [From .env]

**Frontend App Service:**
- `NEXT_TELEMETRY_DISABLED`: 1
- `NODE_ENV`: production
- `NEXT_PUBLIC_API_URL`: https://prepedge-api-prod.azurewebsites.net/api/v1

## 📊 Resource Costs

Based on Azure B2 App Service Plan (production-ready):

| Resource | Size | Est. Monthly Cost |
|----------|------|------------------|
| App Service Plan (B2) | Shared CPU | ~$32 |
| Backend App Service | Included | ~$0 |
| Frontend App Service | Included | ~$0 |
| **Database** | **EXISTING** | **$0** |
| Data Transfer (if <1GB) | | ~$0-5 |
| **Total** | | **~$32-37** |

*(Prices vary by region; shown for Southeast Asia)*

## 🐛 Troubleshooting

### Script Fails to Login
```powershell
# Clear Azure cache and re-login
az logout
az login
```

### Database Connection Issues
```bash
# Test connection (requires psql)
psql -h prepedge-db-primary-sea.postgres.database.azure.com \
     -U prepedge_admin \
     -d postgres \
     -c "SELECT version();"
```

### Custom Domain Not Validating
- Wait for DNS propagation: `nslookup api.prepedgeai.in`
- Verify CNAME record: `nslookup -type=CNAME api.prepedgeai.in`
- Check Azure Portal → Custom domains → Validation status

### App Service Won't Start
1. Check Application Insights logs in Azure Portal
2. SSH into App Service and check logs:
   ```bash
   az webapp ssh --resource-group prepedge-ai-prod-services --name prepedge-api-prod
   ```
3. Verify environment variables are set correctly

## 📚 Additional Resources

- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
- [Azure Custom Domains](https://learn.microsoft.com/en-us/azure/app-service/app-service-web-tutorial-custom-domain)
- [GoDaddy Domain Management](https://www.godaddy.com/help)
- [PostgreSQL Connection Strings](https://learn.microsoft.com/en-us/azure/postgresql/single-server/)

## 📝 Script Features

Both scripts include:
- ✅ Automatic prerequisite checking
- ✅ Color-coded output for easy reading
- ✅ Error handling and validation
- ✅ Summary of created resources
- ✅ Next steps guidance
- ✅ Database connection testing instructions

## ❓ Questions or Issues?

If you encounter problems:
1. Check the troubleshooting section above
2. Review Azure Portal for resource status
3. Check application logs in Application Insights
4. Verify all prerequisite are installed and configured

---

**Made for PrepEdge AI Production Deployment**  
*Using existing database - Zero downtime, zero redundancy*
