import os
import time
import json

from system_monitor import get_system_snapshot, compare_snapshots
from ai_explainer import explain_system

# 🔍 TEMPORARY CHECK: Verify API key is loaded
print("API KEY FOUND:", bool(os.getenv("GEMINI_API_KEY")))

print("\n📸 Taking initial system snapshot...")
snapshot_before = get_system_snapshot()

print("⏳ Waiting for 10 seconds...")
time.sleep(10)

print("📸 Taking new system snapshot...")
snapshot_now = get_system_snapshot()

changes = compare_snapshots(snapshot_before, snapshot_now)

print("\n🧠 SYSTEM CHANGE SUMMARY:\n")
print(json.dumps(changes, indent=4))

print("\n🤖 AI EXPLANATION:\n")
ai_output = explain_system(changes)
print(ai_output)
