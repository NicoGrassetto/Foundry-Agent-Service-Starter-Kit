targetScope = 'resourceGroup'

@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name of the AI Services account (AI Foundry hub)')
param aiServicesName string = 'dressmate-ai-${uniqueSuffix}'

@description('Name of the AI Foundry project')
param projectName string = 'dressmate-project'

@description('Model to deploy for the agent')
param modelName string = 'gpt-4o'

@description('Model version')
param modelVersion string = '2024-08-06'

@description('Deployment capacity (thousands of tokens per minute)')
param deploymentCapacity int = 30

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

@description('AI Services endpoint for the SDK')
output endpoint string = 'https://${aiServices.properties.customSubDomainName}.services.ai.azure.com/'

@description('AI Services account name')
output aiServicesAccountName string = aiServices.name

@description('Project name')
output projectNameOutput string = project.name

@description('Model deployment name')
output deploymentName string = modelDeployment.name
