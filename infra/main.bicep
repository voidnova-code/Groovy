@minLength(3)
@maxLength(24)
param appName string = 'tictactoe'

param location string = resourceGroup().location

param environment string = 'prod'

// App Service Plan
param appServiceSkuName string = 'B2'
param appServiceSkuTier string = 'Basic'

// PostgreSQL Database
param postgresqlSkuName string = 'Standard_B1ms'
param postgresqlVersion string = '14'

// Resource naming
var appServicePlanName = '${appName}-asp-${environment}'
var appServiceName = '${appName}-app-${environment}'
var postgreSqlServerName = '${appName}-postgres-${environment}-${uniqueString(resourceGroup().id)}'
var keyVaultName = '${appName}-kv-${environment}-${uniqueString(resourceGroup().id)}'
var managedIdentityName = '${appName}-identity-${environment}'
var logAnalyticsName = '${appName}-logs-${environment}'
var appInsightsName = '${appName}-insights-${environment}'

// User-Assigned Managed Identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: managedIdentity.properties.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
}

// PostgreSQL Server
resource postgresqlServer 'Microsoft.DBforPostgreSQL/servers@2017-12-01' = {
  name: postgreSqlServerName
  location: location
  sku: {
    name: postgresqlSkuName
    tier: 'Basic'
    capacity: 1
  }
  properties: {
    createMode: 'Default'
    version: postgresqlVersion
    administratorLogin: 'pgadmin'
    administratorLoginPassword: 'P@ssw0rd${uniqueString(resourceGroup().id)}'
    sslEnforcement: 'ENABLED'
    storageProfile: {
      storageMB: 51200
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource postgresqlDatabase 'Microsoft.DBforPostgreSQL/servers/databases@2017-12-01' = {
  parent: postgresqlServer
  name: 'tictactoe'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Allow all Azure services to PostgreSQL
resource postgresqlFirewallAllowAzure 'Microsoft.DBforPostgreSQL/servers/firewallRules@2017-12-01' = {
  parent: postgresqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: appServiceSkuName
    tier: appServiceSkuTier
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// App Service
resource appService 'Microsoft.Web/sites@2022-03-01' = {
  name: appServiceName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
  }
}

// App Service Configuration
resource appServiceConfig 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appService
  name: 'web'
  properties: {
    numberOfWorkers: 1
    defaultDocuments: []
    netFrameworkVersion: 'v4.0'
    pythonVersion: '3.11'
    requestTracingEnabled: false
    remoteDebuggingEnabled: false
    httpLoggingEnabled: true
    detailedErrorLoggingEnabled: true
    alwaysOn: true
    webSocketsEnabled: false
    managedPipelineMode: 'Integrated'
  }
}

// App Service Diagnostic Settings
resource appServiceDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  scope: appService
  name: 'appServiceDiags'
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// App Settings
resource appServiceAppSettings 'Microsoft.Web/sites/config@2022-03-01' = {
  parent: appService
  name: 'appsettings'
  properties: {
    WEBSITES_PORT: '8000'
    PYTHONPATH: '/home/site/wwwroot'
    DATABASE_URL: 'postgresql://pgadmin:${postgresqlServer.properties.administratorLoginPassword}@${postgresqlServer.properties.fullyQualifiedDomainName}:5432/tictactoe?sslmode=require'
    DJANGO_SETTINGS_MODULE: 'tictactoe.settings'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    ENABLE_ORYX_BUILD: 'true'
  }
}

// Outputs
@export()
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
@export()
output postgresqlServerName string = postgresqlServer.name
@export()
output postgresqlServerFqdn string = postgresqlServer.properties.fullyQualifiedDomainName
@export()
output keyVaultUrl string = keyVault.properties.vaultUri
@export()
output managedIdentityId string = managedIdentity.id
@export()
output applicationInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
