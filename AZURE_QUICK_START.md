# Azure Deployment Quick Start - PrepEdge AI

## 🚀 Quick Setup (5 Steps)

### Step 1: Prepare Azure Environment

```powershell
# Install Azure CLI if not already installed
# https://docs.microsoft.com/cli/azure/install-azure-cli-windows

# Login to Azure
az login

# Verify subscription
az account show
```

### Step 2: Deploy Infrastructure

```powershell
# Navigate to project root
cd "c:\Users\srisa\Downloads\prepedge AI"

# Run deployment script (Linux/Mac with WSL)
bash azure-deploy.sh prod eastus

# OR manually deploy ARM template (Windows PowerShell)
$rg = "prepedge-ai-prod"
$location = "eastus"

az group create --name $rg --location $location

az deployment group create `
  --resource-group $rg `
  --template-file azure-infrastructure.json `
  --parameters `
    environment="prod" `
    location=$location `
    appServicePlanSku="B2"
```

### Step 3: Configure GitHub Secrets

```powershell
# Get Azure credentials for GitHub Actions
$subscription = az account show --query id -o tsv
$tenant = az account show --query tenantId -o tsv

# Create service principal
$sp = az ad sp create-for-rbac `
  --name "github-prepedge-deploy" `
  --role "Contributor" `
  --scopes "/subscriptions/$subscription"

# Get values from output:
# - CREATE_AZURE_CLIENT_ID: appId
# - CREATE_AZURE_TENANT_ID: tenant
# - CREATE_AZURE_SUBSCRIPTION_ID: subscription
# - CREATE_AZURE_CLIENT_SECRET: password
```

Add these to GitHub repository secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_CLIENT_SECRET`

### Step 4: Configure Domain (GoDaddy → Azure)

Go to **Azure Portal** → your App Service → **Custom domains**

#### For Backend (api.prepedgeai.in):
1. Click "Add custom domain"
2. Enter: `api.prepedgeai.in`
3. Choose "CNAME record validation"
4. Copy the CNAME target from Azure

In **GoDaddy DNS** (DNS Management):
```
Name: api
Type: CNAME
Value: prepedge-api.azurewebsites.net
TTL: 3600
```

5. Click **Validate** in Azure Portal
6. Enable SSL/TLS (Azure-managed certificate)
7. Force HTTPS

#### For Frontend (prepedgeai.in):
1. Click "Add custom domain"
2. Enter: `prepedgeai.in`
3. Choose "CNAME record validation"
4. Copy the CNAME target

In **GoDaddy DNS**:
```
Name: @
Type: CNAME
Value: prepedge-web.azurewebsites.net
TTL: 3600
```

Also add for www:
```
Name: www
Type: CNAME
Value: prepedge-web.azurewebsites.net
TTL: 3600
```

### Step 5: Deploy Application

The GitHub Actions pipeline will automatically:
1. Test backend & frontend
2. Build Docker images
3. Deploy to Azure App Services
4. Run database migrations
5. Verify deployment

Just push to main:
```powershell
git push origin main
```

## 📊 Verification Checklist

- [ ] Resource group created in Azure
- [ ] PostgreSQL database running
- [ ] Redis cache operational  
- [ ] App Services created and running
- [ ] DNS records configured in GoDaddy
- [ ] Custom domains validated in Azure
- [ ] SSL certificates issued
- [ ] GitHub Actions secrets configured
- [ ] Application deployed successfully

## 🔗 Important Links

**Azure Resources:**
- Backend API: https://prepedge-api.azurewebsites.net
- Frontend Web: https://prepedge-web.azurewebsites.net
- Resource Group: https://portal.azure.com/#blade/HubsExtension/BrowseResourceGroups

**Monitoring:**
- Application Insights: Azure Portal → prepedge-insights
- Logs: Azure Portal → Monitoring → Logs
- Metrics: Azure Portal → Monitoring → Metrics

**Domain:**
- GoDaddy Dashboard: https://godaddy.com/domains
- DNS Manager: https://dcc.godaddy.com/manage/prepedgeai.in/dns

## 💰 Estimated Monthly Costs

| Service | Tier | Cost |
|---------|------|------|
| App Service Plan | B2 | $50 |
| PostgreSQL | Standard_B2s | $100 |
| Redis Cache | Basic | $30 |
| Application Insights | Pay-as-you-go | $10 |
| Storage | Hot | $5 |
| **Total** | | **~$195/month** |

## 🔐 Security Configuration

1. **PostgreSQL Firewall:**
   - Only allow Azure Services
   - Restrict to App Services only

2. **Redis Cache:**
   - Require SSL/TLS
   - Set minimum TLS version to 1.2
   - Use strong password

3. **App Services:**
   - Enable HTTPS only
   - Set security headers
   - Enable authentication

4. **Key Vault:**
   - Store all secrets
   - Enable soft delete
   - Enable purge protection

## 🚨 Troubleshooting

### Domain Not Resolving
```powershell
# Check DNS propagation
nslookup api.prepedgeai.in
nslookup prepedgeai.in

# Check CNAME records
dig api.prepedgeai.in CNAME
```

### App Service Not Starting
```powershell
# Check logs
az webapp log tail --resource-group prepedge-ai-prod --name prepedge-api

# Restart app service
az webapp restart --resource-group prepedge-ai-prod --name prepedge-api
```

### Database Connection Error
```powershell
# Check firewall rules
az postgres server firewall-rule list --resource-group prepedge-ai-prod --server prepedge-db-prod

# Test connection
psql -h prepedge-db-prod.postgres.database.azure.com -U adminuser -d prepedge
```

### Redis Connection Issues
```powershell
# Get connection string
az redis list-keys --resource-group prepedge-ai-prod --name prepedge-cache-prod

# Test connection
redis-cli -h prepedge-cache-prod.redis.cache.windows.net -p 6380 -a <key> --tls ping
```

## 📚 Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/azure/postgresql)
- [Azure Cache for Redis](https://docs.microsoft.com/azure/azure-cache-for-redis)
- [Custom Domains in App Service](https://docs.microsoft.com/azure/app-service/app-service-web-tutorial-custom-domain)
- [GoDaddy DNS Management](https://godaddy.com/help)

## 🎯 Next Steps After Deployment

1. **Setup Monitoring**
   - Configure Application Insights alerts
   - Create custom dashboards
   - Setup log aggregation

2. **Performance Optimization**
   - Enable CDN for static assets
   - Optimize database queries
   - Configure caching headers

3. **Backup & Disaster Recovery**
   - Enable automated backups
   - Test restore procedures
   - Document recovery procedures

4. **CI/CD Enhancement**
   - Setup staging environment
   - Configure blue-green deployment
   - Add approval workflow

5. **Security Hardening**
   - Enable Azure Sentinel
   - Configure Azure Firewall
   - Regular security assessments

---

**Need Help?**
- Azure Support: https://docs.microsoft.com/azure/support-plans
- GitHub Issues: https://github.com/2100080051/prepedge-AI/issues
- Documentation: See `AZURE_DEPLOYMENT_GUIDE.md`
