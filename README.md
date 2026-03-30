# Microsoft Foundry Agent Service Starter Kit

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://codespaces.new/NicoGrassetto/DressMate)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev+Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/NicoGrassetto/DressMate)

Welcome to the Microsoft Foundry Agent Service Starter Kit. It's a lightweight template for building AI agents powered by **Microsoft Foundry Agent Service**. This solution accelerator uses Azure AI Services, Azure Blob Storage, and Bing Grounding, with Bicep infrastructure-as-code and `azd` deployment automation.

Microsoft Foundry Agent Service is a powerful platform for building intelligent, tool-augmented AI agents. Designed for developers creating conversational AI workflows, it streamlines the process of orchestrating models with built-in tools — including Function calling, Code Interpreter, File Search, and Bing Grounding — into a single, cohesive interface. This eliminates the need for complex custom orchestration logic or manual tool integration, enabling scalable, low-latency agent interactions across diverse use cases. Whether you're building internal copilots, customer-facing assistants, or domain-specific reasoning agents, Microsoft Foundry Agent Service delivers production-ready results that integrate seamlessly into your business logic.

Learn more about [Microsoft Foundry Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview).

<p align="center">
  <a href="#project-structure">Project Structure</a> |
  <a href="#prerequisites">Prerequisites</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#manual-setup">Manual Setup</a> |
  <a href="#usage">Usage</a> |
  <a href="#built-in-tools">Built-in Tools</a> |
  <a href="#customization">Customization</a> |
  <a href="#new-tools">New Tools</a> |
  <a href="#new-agents">New Agents</a> |
  <a href="#infrastructure">Infrastructure</a> |
  <a href="#pricing">Pricing</a> |
  <a href="#resources">Resources</a>
</p>

<p align="center">
  <img src="assets/what-is-an-agent.png" alt="What is an Agent" width="800" />
</p>

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
│       └── math.py           # Sample Function tool (math operations)
├── hooks/
│   ├── preprovision.sh       # Auto-detects max GPT-4o quota before deploy
│   └── postprovision.sh      # Auto-writes .env and creates agent(s) after azd provision
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

## Quick Start

```bash
azd up                  # provisions infra, writes .env, and creates agent(s) via post-provision hook
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

### 5. Tear Down

To delete all provisioned Azure resources:

**With `azd`:**

```bash
azd down --purge
```

**Manual:**

```bash
az group delete --name my-agent-rg --yes --no-wait
```

## Usage

Start an interactive conversation with a registered agent:

```bash
python -m src.main [agent-key]
```

- If only one agent is registered, the key can be omitted.
- If multiple agents exist, specify which one to use (e.g. `python -m src.main default`).
- Type your message and press Enter to chat. The agent will use its configured tools automatically.
- Type `quit`, `exit`, or `q` to end the session.

**Docker:**

```bash
docker build -t foundry-agent .
docker run --env-file .env -it foundry-agent
```

To run a specific agent in Docker:

```bash
docker run --env-file .env -it foundry-agent python -m src.main default
```

## Built-in Tools

### Implemented

| Tool | Description | Pricing |
|---|---|---|
| **Function** | Custom Python function called by the agent (sample: `query_items`) | Free (runs in your process) |
| **Code Interpreter** | Sandboxed Python execution for data analysis and calculations | [Pricing](https://azure.microsoft.com/pricing/details/ai-studio/) |
| **File Search** | Managed RAG over uploaded documents (vector store) | [Pricing](https://azure.microsoft.com/pricing/details/ai-studio/) |
| **Bing Grounding** | Web search for real-time information | [Pricing](https://www.microsoft.com/en-us/bing/apis/grounding-pricing) |

### Available (not implemented)

The following tools are offered by Microsoft Foundry Agent Service but are **not yet wired up** in this starter kit:

| Tool | Description | Pricing |
|---|---|---|
| **Azure AI Search** | Enterprise RAG over Azure AI Search indexes with integrated vectorisation | [Pricing](https://azure.microsoft.com/pricing/details/search/) |
| **Azure Functions** | Call an Azure Function as a tool (serverless compute) | [Pricing](https://azure.microsoft.com/pricing/details/functions/) |
| **OpenAPI** | Call any REST API described by an OpenAPI 3.x spec | Free (calls your API) |
| **Microsoft Fabric** | Query Microsoft Fabric data through the agent | [Pricing](https://azure.microsoft.com/pricing/details/microsoft-fabric/) |
| **SharePoint** | Ground the agent on SharePoint site content | [Pricing](https://www.microsoft.com/microsoft-365/business/compare-all-plans) |
| **Azure Blob Storage** | Access files stored in Azure Blob Storage | [Pricing](https://azure.microsoft.com/pricing/details/storage/blobs/) |
| **Connected Agent** | Call another agent as a tool for multi-agent orchestration | Free (agent-to-agent) |
| **Logic Apps** | Trigger Azure Logic Apps workflows as tools | [Pricing](https://azure.microsoft.com/pricing/details/logic-apps/) |

## Customization

1. **System prompt** — Edit [src/prompts/agent.prompty](src/prompts/agent.prompty)
2. **Function tool** — Replace `src/tools/math.py` with your own domain logic
3. **Agent name** — Set `AGENT_NAME` in `.env`
4. **Model** — Set `MODEL_NAME` in `.env` (default: `gpt-4o`)

## New Tools

1. Create a new Python file under `src/tools/` (e.g. `src/tools/weather.py`) and define one or more functions. Each function **must** have a docstring with `:param` and `:return` tags — the agent uses these to understand the function signature.

   ```python
   # src/tools/weather.py
   def get_weather(city: str) -> str:
       """Return the current weather for a city.

       :param city: City name.
       :return: Weather summary.
       """
       return f"Sunny, 22 °C in {city}"
   ```

2. Re-export the function in `src/tools/__init__.py`:

   ```python
   from .weather import get_weather
   ```

3. Add the function to the `tools` set of the relevant agent in `src/agents/registry.py`:

   ```python
   from src.tools import add, get_weather

   AGENT_REGISTRY: dict = {
       "default": {
           ...
           "tools": {add, get_weather},
       },
   }
   ```

4. Run `python -m src.setup` to recreate the agent with the new tool attached.

## New Agents

1. Create a Prompty file for the agent's system prompt in `src/prompts/` (e.g. `src/prompts/travel.prompty`).

2. Add a new entry to `AGENT_REGISTRY` in `src/agents/registry.py`:

   ```python
   AGENT_REGISTRY: dict = {
       "default": { ... },
       "travel": {
           "name": "Travel Agent",
           "prompt": "travel.prompty",
           "model": None,        # None → uses MODEL_NAME from config
           "tools": set(),       # add function tools here if needed
       },
   }
   ```

3. Run `python -m src.setup` — this creates all registered agents and writes their IDs to `.env`.

4. Run the new agent:

   ```bash
   python -m src.main travel
   ```

## Infrastructure

Bicep deploys:

| Resource | Purpose |
|---|---|
| Azure AI Services (S0) | Microsoft Foundry hub + Agent Service data plane |
| Storage Account (LRS) | Thread state, files, vector stores |
| Bing Grounding (G1) | Web search for the Bing Grounding tool |
| GPT-4o deployment | Model used by the agent |

---

## Pricing

### Microsoft Foundry Agent Service

| Component | Price (East US) |
|---|---|
| **Model tokens** | $2.50 / 1M input, $10.00 / 1M output (GPT-4o) |
| **Agent orchestration** | Free (thread management, tool dispatch) |

### Infrastructure (idle)

| Resource | Description | Pricing |
|---|---|---|
| **Azure AI Services** | Pay per token | [Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/) |
| **Storage Account** | Thread state, files, vector stores | [Pricing](https://azure.microsoft.com/pricing/details/storage/blobs/) |

> Prices are approximate (East US, early 2026). See [Azure pricing](https://azure.microsoft.com/pricing/) for current rates.

> [!WARNING]
> **This repository is provided as-is as a quick-start template.**
>
> 🔒 It is the deployer's sole responsibility to review, harden, and adapt this code to meet their organisation's security, compliance, privacy, and operational requirements before using it in any production environment.
>
> 🚫 The creator(s) of this repository bear **no responsibility** for any security vulnerabilities, data breaches, compliance violations, service outages, or any other damages arising from the use or deployment of this code.
>
> 🛠️ By using this repository you acknowledge that additional changes — including but not limited to network isolation, authentication hardening, secret management, logging, monitoring, and access control — may be required to achieve a production-ready security posture.

## Resources

- 📖 [What is Microsoft Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview) — explains what the service does, how agents work, and architectural concepts
- 📖 [Quickstart: Deploy your first hosted agent](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstarts/quickstart-hosted-agent) — step-by-step guide to deploy a hosted agent using Azure Developer CLI
- 📖 [Quickstart: Create a new Microsoft Foundry Agent Service project](https://learn.microsoft.com/azure/ai-foundry/agents/quickstart?pivots=ai-foundry-portal) — classic quickstart tutorial for creating and configuring an agent project
- 📖 [Microsoft Foundry documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/) — general hub for Microsoft Foundry including models, agents, and app templates
- 🌐 [Microsoft Foundry Agent Service (product overview)](https://azure.microsoft.com/en-us/products/ai-agent-service/) — marketing + feature overview on the Azure site
