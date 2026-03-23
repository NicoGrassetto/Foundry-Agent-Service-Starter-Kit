# Foundry Agent Service Starter Kit

A starter template for building AI agents with **Azure AI Foundry Agent Service**. Comes pre-wired with four built-in tools (Function, Code Interpreter, File Search, Bing Grounding), Bicep infrastructure-as-code, and `azd` deployment automation.

## Project Structure

```
├── infra/
│   ├── main.bicep            # Azure infrastructure (AI Services, Storage, Bing Grounding)
│   └── main.bicepparam       # Parameter values
├── src/
│   ├── __init__.py
│   ├── config.py             # Centralised configuration from env
│   ├── setup.py              # One-time agent creation (writes AGENT_ID to .env)
│   ├── main.py               # CLI entry point (interactive conversation loop)
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py          # Agent factory, retrieval, and toolset builder
│   ├── prompts/
│   │   └── agent.prompty     # System prompt (Prompty format)
│   └── tools/
│       ├── __init__.py
│       └── sample_data.py    # Sample Function tool (in-memory data query)
├── hooks/
│   └── postprovision.sh      # Auto-writes .env after azd provision
├── azure.yaml                # azd project descriptor
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- An **Azure subscription**
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and signed in
- [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) (optional, for one-command deploy)
- Python 3.9+

## Quick Start with `azd`

```bash
azd up                  # provisions infra + writes .env via post-provision hook
python -m src.setup     # creates the agent on the service, saves AGENT_ID to .env
python -m src.main      # runs the conversation loop against the persisted agent
```

## Manual Setup

### 1. Deploy Infrastructure

```bash
az group create --name my-agent-rg --location eastus

az deployment group create \
  --resource-group my-agent-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

### 2. Configure Environment

```bash
cp .env.example .env
# Fill in AZURE_AI_ENDPOINT and BING_CONNECTION_ID from deployment outputs
```

### 3. Install & Create Agent

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

az login
python -m src.setup     # creates agent, writes AGENT_ID to .env
```

### 4. Run

```bash
python -m src.main      # reuses the persisted agent — no re-creation
```

## Built-in Tools

| Tool | Description |
|---|---|
| **Function** | Custom Python function called by the agent (sample: `query_items`) |
| **Code Interpreter** | Sandboxed Python execution for data analysis and calculations |
| **File Search** | Managed RAG over uploaded documents (vector store) |
| **Bing Grounding** | Web search for real-time information |

## Customising the Agent

1. **System prompt** — Edit [src/prompts/agent.prompty](src/prompts/agent.prompty)
2. **Function tool** — Replace `src/tools/sample_data.py` with your own domain logic
3. **Agent name** — Set `AGENT_NAME` in `.env`
4. **Model** — Set `MODEL_NAME` in `.env` (default: `gpt-4o`)

## Infrastructure

Bicep deploys:

| Resource | Purpose |
|---|---|
| Azure AI Services (S0) | AI Foundry hub + Agent Service data plane |
| Storage Account (LRS) | Thread state, files, vector stores |
| Bing Grounding (G1) | Web search for the Bing Grounding tool |
| GPT-4o deployment | Model used by the agent |

---

## Pricing

### Azure AI Agent Service

| Component | Price (East US) |
|---|---|
| **Model tokens** | $2.50 / 1M input, $10.00 / 1M output (GPT-4o) |
| **Agent orchestration** | Free (thread management, tool dispatch) |

### Built-in Tools

| Tool | Cost |
|---|---|
| **Code Interpreter** | $0.03 / session |
| **File Search** | $0.10 / GB vector store / day (first 1 GB free) |
| **Bing Grounding** | $5.00 / 1K transactions |
| **Function** | Free (runs in your process) |

### Infrastructure (idle)

| Resource | Estimated monthly cost |
|---|---|
| Azure AI Services (S0) | $0 base (pay per token) |
| Storage Account (LRS) | ~$0.02 / GB / month |
| **Total fixed cost** | **< $1 / month** |

> Prices are approximate (East US, early 2026). See [Azure pricing](https://azure.microsoft.com/pricing/) for current rates.
