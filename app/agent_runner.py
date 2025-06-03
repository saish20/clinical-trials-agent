# 📄 agent_runner.py – Agentic Clinical Trials Researcher

from app.tools.search_trials import search_clinical_trials_v2
from app.tools.summarize_text import summarize_trials_with_gpt
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load API keys from .env
load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Step 1: Accept high-level goal from user input
USER_GOAL = input("💬 Enter your research goal: ")

# Step 2: Extract condition and location from goal
extraction_prompt = f"""
You are a data extraction assistant. Extract the disease/condition and target location from this research goal:

"{USER_GOAL}"

Respond only as JSON like:
{{
  "condition": "...",
  "location": "..."
}}
"""

extraction_response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {"role": "system", "content": "You extract fields from a research prompt."},
        {"role": "user", "content": extraction_prompt}
    ],
    temperature=0
)

fields = json.loads(extraction_response.choices[0].message.content)
CONDITION = fields.get("condition", "")
LOCATION = fields.get("location", "")

print(f"🔍 Condition: {CONDITION}")
print(f"🌍 Location: {LOCATION}")

# Step 3: Search for trials
trials = search_clinical_trials_v2(
    condition=CONDITION,
    location=LOCATION,
    status="RECRUITING",
    max_results=10
)
if not trials:
    print("⚠️ No trials found.")
    exit()

print("\n📋 Trials Found:")
for idx, trial in enumerate(trials, 1):
    title = trial["protocolSection"]["identificationModule"].get("briefTitle", "Untitled")
    print(f"{idx}. {title}")

# Step 4: Summarize trials
summary = summarize_trials_with_gpt(trials)
print("\n🔍 Summary:\n")
print(summary)

# Step 5: Highlight trials with non-invasive features
keywords = ["non-invasive", "ultrasound", "MRI", "PET", "Exablate"]
matches = [
    t for t in trials
    if any(
        kw.lower() in t["protocolSection"]["identificationModule"].get("briefTitle", "").lower()
        for kw in keywords
    )
]

if matches:
    print("\n💡 Highlighted Trials (non-invasive/intervention-related):")
    for m in matches:
        title = m["protocolSection"]["identificationModule"].get("briefTitle", "")
        print(f"- {title}")
else:
    print("\n🚫 No explicitly non-invasive trials identified in this batch.")

# Step 6: Let user choose a trial to ask questions
print("\n📥 Select a trial to explore in detail")
choice = int(input("Enter trial number: "))
selected_trial = trials[choice - 1]

# Step 7: Conversation loop
while True:
    question = input("\n❓ Ask a question about the selected trial (or type 'exit'): ")
    if question.lower() == "exit":
        break

    trial_json = json.dumps(selected_trial)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You're a helpful assistant answering questions about clinical trials. The user is asking about the following trial:"},
            {"role": "user", "content": f"Trial data:\n{trial_json}"},
            {"role": "user", "content": question}
        ]
    )
    print("\n💬 Answer:\n", response.choices[0].message.content)

print("\n✅ Agent workflow complete.")
