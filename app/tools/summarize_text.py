from openai import OpenAI
from app.prompts.templates import get_trial_summary_prompt
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = OpenAI(api_key=os.getenv("GROQ_API_KEY"))

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")  # your gsk_ key goes here
)

def summarize_trials_with_gpt(trials, model="llama3-70b-8192"):
    prompt = get_trial_summary_prompt(trials)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a biomedical research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content

    except Exception as e:
        print("❌ Groq API error:", e)
        return "Failed to generate summary."
