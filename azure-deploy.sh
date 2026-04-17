#!/bin/bash

# PrepEdge AI - Azure Deployment Script
# This script automates the deployment of PrepEdge AI to Azure
# Usage: ./azure-deploy.sh [environment] [location]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-prod}"
LOCATION="${2:-eastus}"
RESOURCE_GROUP="prepedge-ai-${ENVIRONMENT}"
PROJECT_NAME="prepedge"

# Derived names
BACKEND_APP_NAME="${PROJECT_NAME}-api"
FRONTEND_APP_NAME="${PROJECT_NAME}-web"
APP_PLAN="${PROJECT_NAME}-plan-${ENVIRONMENT}"
DB_NAME="${PROJECT_NAME}-db-${ENVIRONMENT}"
REDIS_NAME="${PROJECT_NAME}-cache-${ENVIRONMENT}"
VAULT_NAME="${PROJECT_NAME}-kv-${ENVIRONMENT}"
INSIGHTS_NAME="${PROJECT_NAME}-insights-${ENVIRONMENT}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PrepEdge AI - Azure Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Location: ${YELLOW}${LOCATION}${NC}"
echo -e "Resource Group: ${YELLOW}${RESOURCE_GROUP}${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed"
        echo "Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    
    print_status "All prerequisites met"
}

# Login to Azure
login_to_azure() {
    print_info "Logging in to Azure..."
    az login --use-device-code
    print_status "Logged in to Azure"
}

# Create resource group
create_resource_group() {
    print_info "Creating resource group: ${RESOURCE_GROUP}..."
    
    az group create \
        --name "${RESOURCE_GROUP}" \
        --location "${LOCATION}" \
        --tags Environment="${ENVIRONMENT}" Project="PrepEdgeAI"
    
    print_status "Resource group created"
}

# Deploy ARM template
deploy_infrastructure() {
    print_info "Deploying infrastructure via ARM template..."
    
    az deployment group create \
        --resource-group "${RESOURCE_GROUP}" \
        --template-file "azure-infrastructure.json" \
        --parameters \
            environment="${ENVIRONMENT}" \
            location="${LOCATION}" \
            appServicePlanSku="B2" \
            databaseSku="Standard_B2s" \
            redisSku="Basic"
    
    print_status "Infrastructure deployed"
}

# Setup Key Vault secrets
setup_key_vault() {
    print_info "Setting up Key Vault secrets..."
    
    # Generate secrets if not provided
    SECRET_KEY=$(openssl rand -base64 32)
    
    # Get database connection string
    DB_SERVER=$(az postgres server show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${DB_NAME}" \
        --query "fullyQualifiedDomainName" -o tsv)
    
    DB_CONNECTION="postgresql://adminuser:${DB_PASSWORD}@${DB_SERVER}:5432/prepedge"
    
    # Store secrets in Key Vault
    print_info "Storing secrets in Key Vault..."
    
    az keyvault secret set \
        --vault-name "${VAULT_NAME}" \
        --name "database-connection-string" \
        --value "${DB_CONNECTION}"
    
    az keyvault secret set \
        --vault-name "${VAULT_NAME}" \
        --name "secret-key" \
        --value "${SECRET_KEY}"
    
    az keyvault secret set \
        --vault-name "${VAULT_NAME}" \
        --name "redis-url" \
        --value "redis://${REDIS_NAME}.redis.cache.windows.net:6380?ssl=True"
    
    # Note: User should add these manually or via environment
    echo ""
    echo -e "${YELLOW}Please add the following secrets to Key Vault:${NC}"
    echo "  - openai-api-key: [Your NVIDIA NIM API Key]"
    echo "  - sendgrid-api-key: [Your SendGrid API Key]"
    echo "  - razorpay-key-id: [Your Razorpay Key ID]"
    echo "  - razorpay-key-secret: [Your Razorpay Key Secret]"
    echo ""
    
    print_status "Key Vault secrets configured"
}

# Grant Key Vault access to App Services
grant_key_vault_access() {
    print_info "Granting Key Vault access to App Services..."
    
    # Backend App Service
    BACKEND_PRINCIPAL=$(az webapp identity show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${BACKEND_APP_NAME}" \
        --query "principalId" -o tsv)
    
    az keyvault set-policy \
        --vault-name "${VAULT_NAME}" \
        --object-id "${BACKEND_PRINCIPAL}" \
        --secret-permissions get list
    
    # Frontend App Service
    FRONTEND_PRINCIPAL=$(az webapp identity show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${FRONTEND_APP_NAME}" \
        --query "principalId" -o tsv)
    
    az keyvault set-policy \
        --vault-name "${VAULT_NAME}" \
        --object-id "${FRONTEND_PRINCIPAL}" \
        --secret-permissions get list
    
    print_status "Key Vault access granted"
}

# Configure App Service settings
configure_app_services() {
    print_info "Configuring App Service settings..."
    
    # Backend configuration
    az webapp config appsettings set \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${BACKEND_APP_NAME}" \
        --settings \
            ENVIRONMENT="${ENVIRONMENT}" \
            DEBUG="false" \
            WEBSITES_PORT="8000" \
            SCM_DO_BUILD_DURING_DEPLOYMENT="true"
    
    # Frontend configuration
    az webapp config appsettings set \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${FRONTEND_APP_NAME}" \
        --settings \
            NEXT_TELEMETRY_DISABLED="1" \
            NODE_ENV="production" \
            NEXT_PUBLIC_API_URL="https://${BACKEND_APP_NAME}.azurewebsites.net/api/v1"
    
    print_status "App Services configured"
}

# Output deployment information
output_deployment_info() {
    print_info "Deployment Summary"
    
    BACKEND_URL=$(az webapp show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${BACKEND_APP_NAME}" \
        --query "defaultHostName" -o tsv)
    
    FRONTEND_URL=$(az webapp show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${FRONTEND_APP_NAME}" \
        --query "defaultHostName" -o tsv)
    
    DB_SERVER=$(az postgres server show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${DB_NAME}" \
        --query "fullyQualifiedDomainName" -o tsv)
    
    REDIS_HOST=$(az redis show \
        --resource-group "${RESOURCE_GROUP}" \
        --name "${REDIS_NAME}" \
        --query "hostName" -o tsv)
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Deployment Information${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Backend API:${NC} https://${BACKEND_URL}"
    echo -e "${GREEN}Frontend Web:${NC} https://${FRONTEND_URL}"
    echo -e "${GREEN}Database:${NC} ${DB_SERVER}"
    echo -e "${GREEN}Redis Cache:${NC} ${REDIS_HOST}"
    echo -e "${GREEN}Resource Group:${NC} ${RESOURCE_GROUP}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update GoDaddy DNS records"
    echo "2. Configure custom domains in Azure Portal"
    echo "3. Add missing secrets to Key Vault"
    echo "4. Deploy backend code"
    echo "5. Deploy frontend code"
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    login_to_azure
    create_resource_group
    deploy_infrastructure
    grant_key_vault_access
    configure_app_services
    output_deployment_info
    
    print_status "Azure deployment completed successfully!"
}

# Run main function
main
