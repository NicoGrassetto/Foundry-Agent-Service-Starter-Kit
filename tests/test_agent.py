"""Quick integration test for DressMate Agent Service."""
import os

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    FunctionTool,
    MessageRole,
    ThreadMessageOptions,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from src.agent import SYSTEM_INSTRUCTIONS
from src.tools import query_wardrobe

load_dotenv()

endpoint = os.environ["AZURE_AI_ENDPOINT"]
print(f"Endpoint: {endpoint}")

credential = DefaultAzureCredential()
client = AgentsClient(endpoint=endpoint, credential=credential)

functions = FunctionTool(functions={query_wardrobe})
client.enable_auto_function_calls(functions)

agent = client.create_agent(
    model="gpt-4o",
    name="DressMate-Test",
    instructions=SYSTEM_INSTRUCTIONS,
    toolset=functions,
)
print(f"Agent created: {agent.id}")

# Run a single turn test
run = client.create_thread_and_process_run(
    agent_id=agent.id,
    thread=AgentThreadCreationOptions(
        messages=[
            ThreadMessageOptions(role=MessageRole.USER, content="What casual outfits can I wear today?")
        ]
    ),
    toolset=functions,
)
print(f"Run status: {run.status}")
print(f"Thread: {run.thread_id}")

# Get the response
last = client.messages.get_last_message_text_by_role(
    thread_id=run.thread_id,
    role=MessageRole.AGENT,
)
print(f"\nDressMate: {last.text.value if last else '(no response)'}")

# Cleanup
client.delete_agent(agent.id)
print("\nAgent cleaned up. Test passed!")
