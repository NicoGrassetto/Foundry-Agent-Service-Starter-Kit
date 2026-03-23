# DressMate – Azure AI Agent Service Prototype

A personal styling assistant powered by **Azure AI Agent Service**. The agent uses GPT-4o with a custom wardrobe query tool and vision capabilities to help users pick outfits based on their actual clothing inventory.

## Project Structure

```
DressMate/
├── infra/
│   ├── main.bicep            # Azure infrastructure (AI Services, storage, capability host)
│   └── main.bicepparam       # Parameter values
├── src/
│   ├── __init__.py
│   ├── agent.py              # Agent CLI (interactive conversation loop)
│   └── tools/
│       ├── __init__.py
│       └── wardrobe.py       # Wardrobe query function tool
├── tests/
│   ├── __init__.py
│   ├── test_agent.py         # Integration test (hits Azure)
│   ├── test_tools.py         # Unit tests (no credentials needed)
│   └── test_vision.py        # Vision test (image analysis)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- An **Azure subscription**
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and signed in
- Python 3.9+

## 1. Deploy Infrastructure

```bash
az group create --name dressmate-rg --location eastus

az deployment group create \
  --resource-group dressmate-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.bicepparam
```

## 2. Configure Environment

```bash
cp .env.example .env
# Set AZURE_AI_ENDPOINT to: https://<ai-services-name>.services.ai.azure.com/api/projects/<project-name>
```

## 3. Install & Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

az login
python -m src.agent
```

## 4. Run Tests

```bash
python -m tests.test_tools    # Unit tests (offline, fast)
python -m tests.test_agent    # Integration test (requires Azure)
python -m tests.test_vision   # Vision test (requires Azure + image.png in project root)
```

---

## Pricing

### Azure AI Agent Service

The Agent Service itself has **two cost components**:

| Component | What you pay for | Price (East US) |
|---|---|---|
| **Model tokens** | Input + output tokens consumed by GPT-4o during agent runs | $2.50 / 1M input tokens, $10.00 / 1M output tokens |
| **Agent session storage** | Thread state, messages, and file storage managed by the service | Included with the underlying storage account (standard blob rates) |

There is **no separate per-run or per-agent fee** — you pay for the model tokens used and the storage consumed, same as calling the model directly. The Agent Service orchestration layer (thread management, tool dispatch, polling) is free.

### Built-in Tools Pricing

| Tool | Additional cost | Details |
|---|---|---|
| **Code Interpreter** | **$0.03 / session** | Charged per code execution session. A session stays alive for ~1 hour. Each session includes a sandboxed container with compute. |
| **File Search** | **$0.10 / GB of vector store / day** (first 1 GB free) | Charged based on vector store size. Includes chunking, embedding, indexing, and retrieval. No per-query cost beyond model tokens. |
| **Bing Grounding** | **$5.00 / 1K transactions** (Bing Search S1) | Requires a Bing Search resource. Each agent search query = 1 transaction. Plus model tokens to process results. |
| **Azure AI Search** | **AI Search resource pricing** (Free tier available, Basic from ~$75/mo) | You pay for the AI Search resource — the tool connection itself is free. |
| **Azure Functions** | **Azure Functions consumption pricing** | First 1M executions/month free, then $0.20/1M. Plus compute time ($0.000016/GB-s). |
| **OpenAPI** | **Free** (tool itself) | No charge for the tool — you pay only for the external API you're calling plus model tokens. |
| **Connected Agent** | **Free** (tool itself) | No charge for orchestration — you pay for the tokens consumed by the connected agent's model. |
| **Function (custom)** | **Free** | Runs in your process. No Azure charge — just model tokens for the tool call + response. |
| **Vision (image input)** | **Token-based** | Images are converted to tokens. ~765 tokens (low detail) or ~1,105 tokens (high detail 512×512 tile). Priced at the standard input token rate. |

### Example: What DressMate Costs

A typical conversation (5 turns, wardrobe tool called each turn):
- ~2,000 input tokens + ~1,500 output tokens per turn
- 5 turns = ~10,000 input + ~7,500 output tokens
- **Cost: ~$0.10 per conversation**

Add vision (1 image upload): +~1,000 input tokens = **~$0.003 extra**

### Infrastructure Costs (idle)

| Resource | SKU | Estimated monthly cost |
|---|---|---|
| Azure AI Services (S0) | Pay-per-use | $0 base (pay per token) |
| Storage Account (LRS) | Standard | ~$0.02/GB/month |
| **Total fixed cost** | | **< $1/month** (idle) |

> **Note:** Prices are approximate and based on East US region as of early 2026. Check [Azure pricing](https://azure.microsoft.com/pricing/) for current rates. GPT-4o-mini is significantly cheaper than GPT-4o if cost is a concern.

---

## How It Works

1. **Infrastructure** – Bicep deploys an Azure AI Services account with a capability host (Agent Service data plane), storage account, and GPT-4o deployment.
2. **Agent creation** – The `azure-ai-agents` SDK creates a named agent with a system prompt and the `query_wardrobe` function tool.
3. **Conversation loop** – Each user message is added to a persistent thread, a run is created, the SDK auto-handles tool calls, and the response is printed.
4. **Vision** – Images can be uploaded and sent as multimodal content — GPT-4o analyzes them natively.
5. **Cleanup** – On exit the agent resource is deleted.

## Next Steps

- Add **Bing Grounding** for weather-aware outfit suggestions
- Add **File Search** for fashion guide / lookbook RAG
- Add **Connected Agent** for a shopping assistant sub-agent
- Persist agent across sessions (avoid re-creation on each run)
- Deploy as an API with **Azure Functions**
