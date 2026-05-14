# Azure Deployment Guide for Tictactoe

This guide walks you through deploying the Tictactoe Django application to Azure with PostgreSQL database.

## Prerequisites

1. **Azure Account**: Create one at https://azure.microsoft.com
2. **Azure CLI**: Download and install from https://aka.ms/installazurecliwindows
3. **Git**: For deploying code to Azure App Service

## Step 1: Install Azure CLI

### On Windows (PowerShell as Administrator)
```powershell
# Download and run the MSI installer
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile AzureCLI.msi
Start-Process msiexec.exe -ArgumentList '/i AzureCLI.msi /quiet' -Wait
Remove-Item AzureCLI.msi
```

Or use Chocolatey (if installed):
```powershell
choco install azure-cli
```

### Verify Installation
```powershell
az --version
```

## Step 2: Login to Azure

```powershell
az login
```

This opens a browser where you'll authenticate with your Azure account.

## Step 3: Set Your Subscription

```powershell
# List available subscriptions
az account list --output table

# Set your subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

## Step 4: Deploy Infrastructure

### Option A: Using PowerShell Script

```powershell
cd C:\Users\sayan\Desktop\New folder (3)
.\deploy-azure.ps1 -ResourceGroup "tictactoe-rg" -Location "eastus" -AppName "tictactoe"
```

### Option B: Manual Deployment

```powershell
# Create resource group
az group create --name tictactoe-rg --location eastus

# Deploy infrastructure
az deployment group create `
    --resource-group tictactoe-rg `
    --template-file ./infra/main.bicep `
    --parameters ./infra/parameters.json `
    --parameters appName=tictactoe environment=prod
```

## Step 5: Configure Environment Variables

After deployment, set the following environment variables in Azure Portal:

1. Go to Azure Portal → App Services → Your App → Configuration
2. Add the following Application Settings:

| Name | Value |
|------|-------|
| `SECRET_KEY` | Generate a random secret: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `GOOGLE_CLIENT_ID` | Your Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth Secret |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourdomain.azurewebsites.net` |

3. Click Save

## Step 6: Deploy Application Code

### Using Git Remote

```powershell
# Add Azure as a remote
az webapp deployment source config-zip `
    --resource-group tictactoe-rg `
    --name tictactoe-app-prod `
    --src <(Compress-Archive -Path . -DestinationPath .\deploy.zip -PassThru)

# Or manually zip and upload
Compress-Archive -Path . -DestinationPath deploy.zip -Force
az webapp deployment source config-zip `
    --resource-group tictactoe-rg `
    --name tictactoe-app-prod `
    --src deploy.zip
```

## Step 7: Run Migrations

### Connect via SSH

```powershell
az webapp ssh --resource-group tictactoe-rg --name tictactoe-app-prod
```

### Run Migration Commands

```bash
# Inside SSH session
cd /home/site/wwwroot

# Create migrations
python manage.py migrate --noinput

# Create superuser
python manage.py createsuperuser
```

## Step 8: Verify Deployment

Visit your app at: `https://tictactoe-app-prod.azurewebsites.net`

## Troubleshooting

### Check Application Logs

```powershell
# View live logs
az webapp log tail --resource-group tictactoe-rg --name tictactoe-app-prod

# Stream logs
az webapp log stream --resource-group tictactoe-rg --name tictactoe-app-prod
```

### Common Issues

#### Database Connection Error
- Verify `DATABASE_URL` is set correctly
- Ensure PostgreSQL firewall allows Azure App Service
- Check that SSL mode is set to `require`

#### Static Files Not Loading
```bash
# SSH into app and collect static files
python manage.py collectstatic --noinput
```

#### Google OAuth Not Working
- Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set
- Check that redirect URI in Google Console matches your Azure domain
- Add `https://yourdomain.azurewebsites.net/auth/callback/` to authorized redirects

## Scaling & Performance

### Increase App Service Plan

```powershell
az appservice plan update `
    --name tictactoe-asp-prod `
    --resource-group tictactoe-rg `
    --sku B3
```

### Enable Auto-scale

```powershell
az monitor autosetting create `
    --resource-group tictactoe-rg `
    --resource tictactoe-app-prod `
    --resource-type "Microsoft.Web/sites" `
    --enabled true
```

## Monitoring

View Application Insights metrics:
1. Azure Portal → Application Insights → Your Instance
2. Check: Performance, Failures, Custom Metrics

## Cost Management

Monitor your costs:
```powershell
az cost management query create `
    --type "Usage" `
    --timeframe "MonthToDate" `
    --dataset-aggregation "totalCost=sum:PreTaxCost"
```

## Security Best Practices

1. ✅ Always use HTTPS (enabled by default)
2. ✅ Set DEBUG=False in production
3. ✅ Use strong SECRET_KEY
4. ✅ Enable HSTS headers
5. ✅ Keep dependencies updated
6. ✅ Use Azure Key Vault for sensitive data

## Next Steps

1. Configure custom domain in Azure Portal
2. Set up SSL certificate (HTTPS)
3. Configure backup strategy
4. Set up monitoring and alerts
5. Implement CI/CD pipeline with GitHub Actions

For more info: https://docs.microsoft.com/en-us/azure/app-service/
