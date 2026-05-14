# Azure Deployment Script for Tictactoe Django App (PowerShell)
# Prerequisites: Azure CLI installed and logged in

param(
    [string]$ResourceGroup = "tictactoe-rg",
    [string]$Location = "eastus",
    [string]$AppName = "tictactoe",
    [string]$Environment = "prod"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Azure Deployment for Tictactoe..." -ForegroundColor Yellow

# Check if logged in to Azure
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "Already logged in to Azure" -ForegroundColor Green
} catch {
    Write-Host "Logging into Azure..." -ForegroundColor Yellow
    az login
}

# Get current subscription
$subscriptionId = az account show --query id -o tsv
Write-Host "Using subscription: $subscriptionId" -ForegroundColor Green

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location | Out-Null

# Deploy Bicep template
Write-Host "Deploying infrastructure..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroup `
    --template-file ./infra/main.bicep `
    --parameters ./infra/parameters.json `
    --parameters appName=$AppName environment=$Environment | Out-Null

# Get deployment outputs
Write-Host "Retrieving deployment outputs..." -ForegroundColor Yellow
$deployment = az deployment group show `
    --name main `
    --resource-group $ResourceGroup `
    --query "properties.outputs" | ConvertFrom-Json

$appServiceName = "$AppName-app-$Environment"
$appServiceUrl = $deployment.appServiceUrl.value
$postgresServer = $deployment.postgresqlServerFqdn.value

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "App Service URL: $appServiceUrl" -ForegroundColor Green
Write-Host "PostgreSQL Server: $postgresServer" -ForegroundColor Green

# Configure App Service for Python
Write-Host "Configuring App Service for Python deployment..." -ForegroundColor Yellow

$startupCmd = "gunicorn tictactoe.wsgi:application --worker-class=gthread --workers=2 --bind=0.0.0.0:`$PORT"
az webapp config set `
    --resource-group $ResourceGroup `
    --name $appServiceName `
    --startup-file $startupCmd | Out-Null

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Set environment variables in Azure Portal:"
Write-Host "   - SECRET_KEY: Generate a random secret key"
Write-Host "   - GOOGLE_CLIENT_ID: Your Google OAuth client ID"
Write-Host "   - GOOGLE_CLIENT_SECRET: Your Google OAuth secret"
Write-Host "   - DEBUG: False"
Write-Host ""
Write-Host "2. Deploy code using: git push azure main"
Write-Host ""
Write-Host "3. Run migrations from SSH:"
Write-Host "   az webapp ssh --resource-group $ResourceGroup --name $appServiceName"
Write-Host "   python manage.py migrate --noinput"
Write-Host ""
Write-Host "4. Create superuser:"
Write-Host "   python manage.py createsuperuser"
