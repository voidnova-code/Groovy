#!/bin/bash

# Azure Deployment Script for Tictactoe Django App
# Prerequisites: Azure CLI installed and logged in

set -e

# Configuration
RESOURCE_GROUP="tictactoe-rg"
LOCATION="eastus"
APP_NAME="tictactoe"
ENVIRONMENT="prod"
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Azure Deployment for Tictactoe...${NC}"

# Check if logged in to Azure
if ! az account show > /dev/null 2>&1; then
    echo -e "${YELLOW}Logging into Azure...${NC}"
    az login
fi

# Set subscription if provided
if [ -n "$SUBSCRIPTION_ID" ]; then
    az account set --subscription "$SUBSCRIPTION_ID"
fi

# Get current subscription
CURRENT_SUB=$(az account show --query id -o tsv)
echo -e "${GREEN}Using subscription: $CURRENT_SUB${NC}"

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

# Deploy Bicep template
echo -e "${YELLOW}Deploying infrastructure...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file ./infra/main.bicep \
    --parameters ./infra/parameters.json \
    --parameters appName="$APP_NAME" environment="$ENVIRONMENT"

# Get deployment outputs
echo -e "${YELLOW}Retrieving deployment outputs...${NC}"
DEPLOYMENT_OUTPUT=$(az deployment group show \
    --name main \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.outputs" \
    -o json)

APP_SERVICE_NAME="${APP_NAME}-app-${ENVIRONMENT}"
APP_SERVICE_URL=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.appServiceUrl.value')
POSTGRES_SERVER=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.postgresqlServerFqdn.value')

echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${GREEN}App Service URL: $APP_SERVICE_URL${NC}"
echo -e "${GREEN}PostgreSQL Server: $POSTGRES_SERVER${NC}"

# Get PostgreSQL password from bicep
POSTGRES_ADMIN="pgadmin"
echo -e "${YELLOW}PostgreSQL Admin: $POSTGRES_ADMIN${NC}"

# Configure App Service for Python
echo -e "${YELLOW}Configuring App Service for Python deployment...${NC}"

# Set startup command
az webapp config set \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --startup-file "gunicorn tictactoe.wsgi:application --worker-class=gthread --workers=2 --bind=0.0.0.0:\$PORT"

# Deploy application code
echo -e "${YELLOW}Deploying application code...${NC}"
az webapp deployment source config-zip \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_SERVICE_NAME" \
    --src <(cd . && zip -r - . -x ".git/*" ".gitignore" "infra/*" "*.env" 2>/dev/null)

echo -e "${GREEN}Deployment successful!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Set environment variables in Azure Portal:"
echo "   - SECRET_KEY"
echo "   - GOOGLE_CLIENT_ID"
echo "   - GOOGLE_CLIENT_SECRET"
echo "   - DEBUG=False"
echo ""
echo "2. Run migrations:"
echo "   az webapp ssh --resource-group $RESOURCE_GROUP --name $APP_SERVICE_NAME"
echo "   python manage.py migrate"
echo ""
echo "3. Create superuser:"
echo "   python manage.py createsuperuser"
