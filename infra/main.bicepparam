using './main.bicep'

param location = 'eastus'
param modelName = 'gpt-4o'
param modelVersion = '2024-11-20'
param deploymentCapacity = int(readEnvironmentVariable('DEPLOYMENT_CAPACITY', '30'))
