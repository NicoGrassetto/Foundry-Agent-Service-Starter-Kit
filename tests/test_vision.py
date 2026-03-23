"""Test vision: upload an image and ask the agent to describe clothing items."""
import os

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    AgentThreadCreationOptions,
    FunctionTool,
    MessageImageFileParam,
    MessageInputImageFileBlock,
    MessageInputTextBlock,
    MessageRole,
    ThreadMessageOptions,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from src.agent import SYSTEM_INSTRUCTIONS
from src.tools import query_wardrobe

load_dotenv()

credential = DefaultAzureCredential()
client = AgentsClient(
    endpoint=os.environ["AZURE_AI_ENDPOINT"],
    credential=credential,
)

# Upload the image
image_path = os.path.join(os.path.dirname(__file__), "..", "image.png")
uploaded = client.files.upload(file_path=image_path, purpose="assistants")
print(f"Uploaded image: {uploaded.id}")

# Set up tools
functions = FunctionTool(functions={query_wardrobe})
client.enable_auto_function_calls(functions)

agent = client.create_agent(
    model="gpt-4o",
    name="DressMate-Vision-Test",
    instructions=SYSTEM_INSTRUCTIONS,
    toolset=functions,
)
print(f"Agent created: {agent.id}")

# Send the image with a prompt
run = client.create_thread_and_process_run(
    agent_id=agent.id,
    thread=AgentThreadCreationOptions(
        messages=[
            ThreadMessageOptions(
                role=MessageRole.USER,
                content=[
                    MessageInputTextBlock(
                        text=(
                            "Look at this image. List every clothing item and accessory you can see. "
                            "For each item give: type, color, style (casual/formal), material if you can tell, "
                            "and a short description. Format as a numbered list."
                        )
                    ),
                    MessageInputImageFileBlock(
                        image_file=MessageImageFileParam(file_id=uploaded.id)
                    ),
                ],
            )
        ]
    ),
    toolset=functions,
)
print(f"Run status: {run.status}")

last = client.messages.get_last_message_text_by_role(
    thread_id=run.thread_id,
    role=MessageRole.AGENT,
)
print(f"\nDressMate:\n{last.text.value if last else '(no response)'}")

# Cleanup
client.delete_agent(agent.id)
client.files.delete(uploaded.id)
print("\nCleaned up. Vision test passed!")
