# DressMate – Azure AI Agent Service Prototype

A personal styling assistant powered by **Azure AI Agent Service**. The agent uses GPT-4o with Code Interpreter to help users pick outfits, analyse colour palettes, and suggest matching items.

## Project Structure

```
DressMate/
├── infra/
│   ├── main.bicep          # Azure infrastructure (AI Services + model deployment)
│   └── main.bicepparam      # Parameter values
├── src/
│   └── agent.py             # Agent prototype (interactive CLI)
├── .env.example             # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- An **Azure subscription**
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and signed in
- Python 3.10+

## 1. Deploy Infrastructure

```bash
# Create a resource group (if you don't have one)
az group create --name dressmate-rg --location eastus

# Deploy the Bicep template
az deployment group create \
  --resource-group dressmate-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam

# Note the endpoint from the outputs
az deployment group show \
  --resource-group dressmate-rg \
  --name main \
  --query properties.outputs.endpoint.value -o tsv
```

## 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set AZURE_AI_ENDPOINT to the endpoint from step 1
```

## 3. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Run the Agent

```bash
# Make sure you're logged in to Azure (for DefaultAzureCredential)
az login

python src/agent.py
```

The agent starts an interactive session. Type your styling questions and press Enter. Type `quit` to exit.

## How It Works

1. **Infrastructure** – Bicep deploys an Azure AI Services account with a GPT-4o model deployment, ready for Azure AI Agent Service.
2. **Agent creation** – The Python SDK creates a named agent with a system prompt and Code Interpreter tool.
3. **Conversation loop** – Each user message creates a thread, sends the message, runs the agent, and prints the response.
4. **Cleanup** – On exit the agent resource is deleted.

## Next Steps

- Add **File Search** tool for wardrobe catalogue lookups
- Integrate **Azure AI Search** for fashion knowledge retrieval
- Add **image analysis** using uploaded wardrobe photos
- Deploy as an API with **Azure Functions**
