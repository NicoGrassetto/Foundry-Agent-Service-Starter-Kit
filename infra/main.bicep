targetScope = 'resourceGroup'

@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name of the AI Services account (AI Foundry hub)')
param aiServicesName string = 'dressmate-ai-${uniqueSuffix}'

@description('Name of the AI Foundry project')
param projectName string = 'dressmate-project'

@description('Name of the storage account for agent state')
param storageAccountName string = 'dmstr${uniqueSuffix}'

@description('Model to deploy for the agent')
param modelName string = 'gpt-4o'

@description('Model version')
param modelVersion string = '2024-08-06'

@description('Deployment capacity (thousands of tokens per minute)')
param deploymentCapacity int = 30

@description('Name of the Bing Grounding resource')
param bingGroundingName string = 'dressmate-bing-${uniqueSuffix}'

// Storage account for Agent Service state (threads, files, code interpreter)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

// Blob service on the storage account
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

// Container for agent state
resource agentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'agents'
}

// Azure AI Services account (serves as AI Foundry hub)
resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiServicesName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: aiServicesName
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
    allowProjectManagement: true
  }
}

// Grant AI Services managed identity "Storage Blob Data Contributor" on the storage account
resource storageBlobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, aiServices.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: storageAccount
  properties: {
    principalId: aiServices.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}

// Connection from AI Services to the storage account (for Agent Service)
resource storageConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  parent: aiServices
  name: 'dressmate-storage'
  properties: {
    category: 'AzureBlob'
    authType: 'AAD'
    target: storageAccount.properties.primaryEndpoints.blob
    isSharedToAll: true
    metadata: {
      ResourceId: storageAccount.id
      AccountName: storageAccount.name
      ContainerName: 'agents'
    }
  }
}

// Capability host for Agent Service (enables the agents data plane)
resource capabilityHost 'Microsoft.CognitiveServices/accounts/capabilityHosts@2025-04-01-preview' = {
  parent: aiServices
  name: 'dressmate-agent-host'
  properties: {
    capabilityHostKind: 'Agents'
    storageConnections: [
      storageConnection.id
    ]
    threadStorageConnections: [
      storageConnection.id
    ]
    vectorStoreConnections: [
      storageConnection.id
    ]
  }
  dependsOn: [
    storageBlobRoleAssignment
  ]
}

// AI Foundry project under the hub
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: aiServices
  name: projectName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
  dependsOn: [
    capabilityHost
  ]
}

// Bing Grounding resource for web search tool
resource bingGrounding 'Microsoft.Bing/accounts@2020-06-10' = {
  name: bingGroundingName
  location: 'global'
  kind: 'Bing.Grounding'
  sku: {
    name: 'G1'
  }
}

// Connection from AI Services to Bing Search (for Bing Grounding tool)
resource bingConnection 'Microsoft.CognitiveServices/accounts/connections@2025-04-01-preview' = {
  parent: aiServices
  name: 'dressmate-bing'
  properties: {
    category: 'ApiKey'
    authType: 'ApiKey'
    target: 'https://api.bing.microsoft.com/'
    isSharedToAll: true
    credentials: {
      key: bingGrounding.listKeys().key1
    }
    metadata: {
      type: 'bing_grounding'
    }
  }
}

// GPT-4o model deployment for the agent
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiServices
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: deploymentCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

@description('AI Foundry project endpoint for the Agent SDK')
output endpoint string = 'https://${aiServices.properties.customSubDomainName}.services.ai.azure.com/api/projects/${projectName}'

@description('AI Services account name')
output aiServicesAccountName string = aiServices.name

@description('Project name')
output projectNameOutput string = project.name

@description('Model deployment name')
output deploymentName string = modelDeployment.name

@description('Storage account name')
output storageAccountNameOutput string = storageAccount.name

@description('Bing connection name for Bing Grounding tool')
output bingConnectionName string = bingConnection.name

@description('Bing connection ID for the agent SDK (project-scoped)')
output bingConnectionId string = '${project.id}/connections/${bingConnection.name}'
