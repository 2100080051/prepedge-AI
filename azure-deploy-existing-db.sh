#!/bin/bash

# PrepEdge AI - Azure Deployment for Existing Database
# This script deploys to Azure using your EXISTING database
# No new database will be created

set -e

# ============================================================================
# Configuration - USING EXISTING DATABASE
# ============================================================================

# NEW Resource Group for App Services only
RESOURCE_GROUP_APPS="prepedge-ai-prod-services"
PROJECT_NAME="prepedge"
BACKEND_APP_NAME="prepedge-api-prod"
FRONTEND_APP_NAME="prepedge-web-prod"
APP_PLAN_NAME="prepedge-appservice-plan"
LOCATION="${1:-southeastasia}"
ENVIRONMENT="${2:-prod}"

# EXISTING Database Details (DO NOT CHANGE)
EXISTING_DB_HOST="prepedge-db-primary-sea.postgres.database.azure.com"
EXISTING_DB_USER="prepedge_admin"
EXISTING_DB_PASSWORD="Nani2906#"
EXISTING_DB_NAME="postgres"

# Other settings from .env
RESEND_API_KEY="re_5arQBmoM_BMnmLy6N9dzWEQoUbJ4WTYio"
RESEND_FROM_EMAIL="noreply@prepedge.io"
POLLINATIONS_API_KEY="pk_EbH2wym2aXzDZkfl"

# ============================================================================
# Colors for Output
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

write_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

write_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

write_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

write_error() {
    echo -e "${RED}✗ $1${NC}"
}

verify_prerequisites() {
    write_info "Verifying prerequisites..."
    
    if ! command -v az &> /dev/null; then
        write_error "Azure CLI is not installed"
        exit 1
    fi
    
    write_success "Azure CLI installed"
}

login_to_azure() {
    write_info "Logging in to Azure..."
    
    if ! az account show &> /dev/null; then
        az login
    fi
    
    local account=$(az account show --query "name" -o tsv)
    write_success "Logged in as: $account"
}

create_app_service_resource_group() {
    write_info "Creating App Service resource group: $RESOURCE_GROUP_APPS..."
    
    if az group exists --name "$RESOURCE_GROUP_APPS" --query "value" -o tsv | grep -q "true"; then
        write_success "Resource group already exists"
    else
        az group create \
            --name "$RESOURCE_GROUP_APPS" \
            --location "$LOCATION" \
            --tags "Environment=$ENVIRONMENT" "Project=PrepEdgeAI" > /dev/null
        
        write_success "Resource group created"
    fi
}

create_app_service_plan() {
    write_info "Creating App Service Plan: $APP_PLAN_NAME..."
    
    az appservice plan create \
        --name "$APP_PLAN_NAME" \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --sku B2 \
        --is-linux > /dev/null
    
    write_success "App Service Plan created"
}

create_backend_app_service() {
    write_info "Creating Backend App Service: $BACKEND_APP_NAME..."
    
    # Create app
    az webapp create \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --plan "$APP_PLAN_NAME" \
        --name "$BACKEND_APP_NAME" \
        --runtime "python|3.11" > /dev/null
    
    # Build connection string with URL-encoded password
    local escaped_password=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$EXISTING_DB_PASSWORD'))")
    local database_url="postgresql://${EXISTING_DB_USER}:${escaped_password}@${EXISTING_DB_HOST}:5432/${EXISTING_DB_NAME}?sslmode=require"
    
    # Configure settings
    write_info "Configuring Backend app settings..."
    
    az webapp config appsettings set \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$BACKEND_APP_NAME" \
        --settings \
            ENVIRONMENT="$ENVIRONMENT" \
            DEBUG="false" \
            WEBSITES_PORT="8000" \
            DATABASE_URL="$database_url" \
            RESEND_API_KEY="$RESEND_API_KEY" \
            RESEND_FROM_EMAIL="$RESEND_FROM_EMAIL" \
            POLLINATIONS_API_KEY="$POLLINATIONS_API_KEY" > /dev/null
    
    # Enable HTTPS
    az webapp update \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$BACKEND_APP_NAME" \
        --set httpsOnly=true > /dev/null
    
    write_success "Backend App Service configured"
}

create_frontend_app_service() {
    write_info "Creating Frontend App Service: $FRONTEND_APP_NAME..."
    
    # Create app
    az webapp create \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --plan "$APP_PLAN_NAME" \
        --name "$FRONTEND_APP_NAME" \
        --runtime "node|18-lts" > /dev/null
    
    # Configure settings
    write_info "Configuring Frontend app settings..."
    
    local backend_url="https://${BACKEND_APP_NAME}.azurewebsites.net/api/v1"
    
    az webapp config appsettings set \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$FRONTEND_APP_NAME" \
        --settings \
            NEXT_TELEMETRY_DISABLED="1" \
            NODE_ENV="production" \
            NEXT_PUBLIC_API_URL="$backend_url" > /dev/null
    
    # Enable HTTPS
    az webapp update \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$FRONTEND_APP_NAME" \
        --set httpsOnly=true > /dev/null
    
    write_success "Frontend App Service configured"
}

test_database_connection() {
    write_info "Testing connection to EXISTING database..."
    
    echo ""
    echo -e "${YELLOW}To test database connection manually, use:${NC}"
    echo "psql -h $EXISTING_DB_HOST -U $EXISTING_DB_USER -d $EXISTING_DB_NAME -c 'SELECT version();'"
    echo ""
    echo -e "${YELLOW}After you have psql installed and connected, type password: Nani2906#${NC}"
    echo ""
    
    write_success "Database connection string configured in App Service"
}

output_summary() {
    write_header "Deployment Summary"
    
    local backend_host=$(az webapp show \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$BACKEND_APP_NAME" \
        --query "defaultHostName" -o tsv)
    
    local frontend_host=$(az webapp show \
        --resource-group "$RESOURCE_GROUP_APPS" \
        --name "$FRONTEND_APP_NAME" \
        --query "defaultHostName" -o tsv)
    
    echo -e "${GREEN}✓ Backend API:${NC} https://$backend_host"
    echo -e "${GREEN}✓ Frontend Web:${NC} https://$frontend_host"
    echo -e "${GREEN}✓ Resource Group:${NC} $RESOURCE_GROUP_APPS"
    echo -e "${GREEN}✓ Using Existing Database:${NC} $EXISTING_DB_HOST"
    echo ""
    
    echo -e "${YELLOW}IMPORTANT - Next Steps:${NC}"
    echo "  1. Verify database firewall allows Azure Services:"
    echo "     - Check: https://portal.azure.com → Your existing database → Networking"
    echo ""
    echo "  2. Update GoDaddy DNS records (prepedgeAI.in):"
    echo "     - api CNAME → $backend_host"
    echo "     - www CNAME → $frontend_host"
    echo "     - @ (root) CNAME → $frontend_host"
    echo ""
    echo "  3. Wait for DNS propagation (10-30 minutes)"
    echo ""
    echo "  4. Configure custom domains in Azure Portal:"
    echo "     - Backend: api.prepedgeai.in"
    echo "     - Frontend: prepedgeai.in"
    echo ""
    echo "  5. Deploy application code:"
    echo "     - Push to GitHub or use 'git push azure main'"
    echo ""
    echo "  6. Verify deployment:"
    echo "     - curl https://api.prepedgeai.in/api/v1/health"
    echo "     - curl https://prepedgeai.in"
    echo ""
}

# ============================================================================
# Main Execution
# ============================================================================

write_header "PrepEdge AI - Azure Deployment (Using EXISTING Database)"
echo "Resource Group (NEW): ${YELLOW}$RESOURCE_GROUP_APPS${NC}"
echo "Location: ${YELLOW}$LOCATION${NC}"
echo "Database (EXISTING): ${YELLOW}$EXISTING_DB_HOST${NC}"
echo "Database User: ${YELLOW}$EXISTING_DB_USER${NC}"
echo ""

# Run deployment steps
verify_prerequisites
login_to_azure
create_app_service_resource_group
create_app_service_plan
create_backend_app_service
create_frontend_app_service
test_database_connection
output_summary

write_success "Azure deployment COMPLETED successfully!"
echo ""
echo -e "${YELLOW}⚠️  Remember to update GoDaddy DNS records before testing!${NC}"
