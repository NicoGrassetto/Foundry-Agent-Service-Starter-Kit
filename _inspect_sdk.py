"""Temporary script to inspect azure-ai-agents SDK."""
from azure.ai.agents.operations import MessagesOperations, ThreadsOperations, RunsOperations
import inspect

print("=== MessagesOperations ===")
for m in sorted(dir(MessagesOperations)):
    if not m.startswith("_"):
        try:
            sig = inspect.signature(getattr(MessagesOperations, m))
            print(f"  {m}{sig}")
        except Exception:
            print(f"  {m}")

print("\n=== ThreadsOperations ===")
for m in sorted(dir(ThreadsOperations)):
    if not m.startswith("_"):
        try:
            sig = inspect.signature(getattr(ThreadsOperations, m))
            print(f"  {m}{sig}")
        except Exception:
            print(f"  {m}")

print("\n=== RunsOperations ===")
for m in sorted(dir(RunsOperations)):
    if not m.startswith("_") and callable(getattr(RunsOperations, m, None)):
        try:
            sig = inspect.signature(getattr(RunsOperations, m))
            print(f"  {m}{sig}")
        except Exception:
            print(f"  {m}")
