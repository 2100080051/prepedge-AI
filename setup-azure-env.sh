#!/bin/bash

# PrepEdge AI - Azure Environment Configuration
# This script sets up environment variables for Azure deployment

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration variables
ENVIRONMENT="${1:-prod}"
LOCATION="${2:-eastus}"
RESOURCE_GROUP="prepedge-ai-${ENVIRONMENT}"

echo -e "${GREEN}PrepEdge AI - Azure Environment Setup${NC}"
echo ""

# Check if logged in to Azure
if ! az account show > /dev/null 2>&1; then
    echo -e "${YELLOW}Not logged in to Azure. Logging in...${NC}"
    az login
fi

# Get subscription details
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Tenant ID: $TENANT_ID"
echo ""

# Check if resource group exists
if ! az group exists --name "$RESOURCE_GROUP" > /dev/null; then
    echo -e "${YELLOW}Resource group $RESOURCE_GROUP does not exist yet.${NC}"
    echo "Run: az group create --name $RESOURCE_GROUP --location $LOCATION"
    exit 1
fi

echo -e "${GREEN}Resource group found: $RESOURCE_GROUP${NC}"
echo ""

# Function to export app service secrets to .env file
export_app_service_config() {
    local app_name=$1
    local output_file=$2
    
    echo -e "${YELLOW}Exporting configuration for $app_name...${NC}"
    
    # Get app settings
    APP_SETTINGS=$(az webapp config appsettings list \
        --resource-group "$RESOURCE_GROUP" \
        --name "$app_name" \
        --query "[].{name:name, value:value}" -o json)
    
    # Convert to .env format
    echo "$APP_SETTINGS" | jq -r '.[] | "\(.name)=\(.value)"' > "$output_file"
    
    echo -e "${GREEN}✓ Exported to $output_file${NC}"
}

# Setup backend environment
echo -e "${GREEN}Setting up Backend Environment${NC}"
export_app_service_config "prepedge-api" "backend/.env.production"

# Setup frontend environment
echo -e "${GREEN}Setting up Frontend Environment${NC}"
export_app_service_config "prepedge-web" "frontend/.env.production"

# Get Key Vault secrets
echo ""
echo -e "${YELLOW}Retrieving Key Vault secrets...${NC}"

VAULT_NAME="prepedge-kv-${ENVIRONMENT}"

if ! az keyvault show --name "$VAULT_NAME" > /dev/null 2>&1; then
    echo -e "${YELLOW}Key Vault $VAULT_NAME not found${NC}"
else
    echo -e "${GREEN}✓ Key Vault found: $VAULT_NAME${NC}"
    
    # Get database connection string
    DB_CONNECTION=$(az keyvault secret show \
        --vault-name "$VAULT_NAME" \
        --name "database-connection-string" \
        --query value -o tsv 2>/dev/null || echo "Not set")
    
    echo "Database Connection: ${DB_CONNECTION:0:50}..."
    
    # Get Redis URL
    REDIS_URL=$(az keyvault secret show \
        --vault-name "$VAULT_NAME" \
        --name "redis-url" \
        --query value -o tsv 2>/dev/null || echo "Not set")
    
    echo "Redis URL: ${REDIS_URL:0:50}..."
fi

echo ""
echo -e "${GREEN}✓ Environment configuration complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review and update .env.production files in backend/ and frontend/"
echo "2. Test database connection: psql <DATABASE_URL>"
echo "3. Test Redis connection: redis-cli <REDIS_URL>"
echo "4. Deploy application"
echo ""
