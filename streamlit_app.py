import streamlit as st
from app.tools.search_trials import search_clinical_trials_v2
from app.tools.summarize_text import summarize_trials_with_gpt
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load API key
load_dotenv()
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(page_title="Clinical Trials Agent", layout="wide")
st.title("🧠 Clinical Trials Research Assistant")

# Step 1: User enters a free-text goal
USER_GOAL = st.text_input("💬 Enter your research goal (e.g. 'Find Alzheimer trials in Ireland with non-invasive imaging')")

# Initialize chat history store
if "chat_by_trial" not in st.session_state:
    st.session_state.chat_by_trial = {}

# Step 2: Extract fields and run search
if USER_GOAL:
    with st.spinner("🧠 Extracting condition and location..."):
        extraction_prompt = f"""
        You are a data extraction assistant. Extract the disease/condition and target location from this research goal:

        "{USER_GOAL}"

        Respond only as JSON like:
        {{
          "condition": "...",
          "location": "..."
        }}
        """
        try:
            extraction_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You extract fields from a research prompt."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0
            )
            fields = json.loads(extraction_response.choices[0].message.content)
            condition = fields.get("condition", "")
            location = fields.get("location", "")
        except Exception as e:
            st.error("❌ Failed to extract fields.")
            st.exception(e)
            st.stop()

    st.success(f"🔍 Condition: `{condition}` | 🌍 Location: `{location}`")

    # Step 3: Search for trials
    with st.spinner("🔎 Searching clinical trials..."):
        trials = search_clinical_trials_v2(
            condition=condition,
            location=location,
            status="RECRUITING",
            max_results=10
        )

    if not trials:
        st.warning("⚠️ No trials found.")
        st.stop()

    st.success(f"✅ Found {len(trials)} trials.")
    for idx, trial in enumerate(trials, 1):
        title = trial["protocolSection"]["identificationModule"].get("briefTitle", "Untitled")
        print(f"{idx}. {title}")

    # Step 4: Summarize
    st.subheader("📄 Trial Summaries")
    summary = summarize_trials_with_gpt(trials)
    st.markdown(summary)

    # Step 5: Highlight non-invasive
    st.subheader("💡 Highlight: Non-Invasive Trials")
    keywords = ["non-invasive", "ultrasound", "MRI", "PET", "Exablate"]
    matches = [
        t for t in trials if any(
            kw.lower() in t["protocolSection"]["identificationModule"].get("briefTitle", "").lower()
            for kw in keywords
        )
    ]

    if matches:
        for idx, m in enumerate(matches):
            title = m["protocolSection"]["identificationModule"].get("briefTitle", "")
            st.markdown(f"**{idx+1}. {title}**")
    else:
        st.info("No explicitly non-invasive trials identified.")

    # Step 6: Question Answering
    st.divider()
    st.subheader("💬 Ask a Question About a Trial")

    trial_titles = [t["protocolSection"]["identificationModule"].get("briefTitle", "") for t in trials]
    selected_title = st.selectbox("Choose a trial to ask about", trial_titles)
    user_question = st.text_input("Ask a question about the selected trial")

    trial_obj = next(t for t in trials if t["protocolSection"]["identificationModule"].get("briefTitle", "") == selected_title)

    if user_question:
        context = json.dumps(trial_obj, indent=2)

        chat_prompt = f"""
        You are a helpful assistant. Use the following trial data to answer the user's question.

        Trial JSON:
        {context}

        Question: {user_question}

        Answer:
        """
        try:
            chat_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about a clinical trial."},
                    {"role": "user", "content": chat_prompt}
                ]
            )
            answer = chat_response.choices[0].message.content

            # Store under current trial
            if selected_title not in st.session_state.chat_by_trial:
                st.session_state.chat_by_trial[selected_title] = []

            st.session_state.chat_by_trial[selected_title].append({
                "q": user_question,
                "a": answer
            })

        except Exception as e:
            st.error("❌ Failed to generate answer.")
            st.exception(e)

    # Display Q&A history for selected trial
    if selected_title in st.session_state.chat_by_trial:
        st.markdown("### 💬 Conversation History")
        for trial_title, qa_list in st.session_state.chat_by_trial.items():
            with st.expander(f"📌 Trial: {trial_title}", expanded=(trial_title == selected_title)):
                for idx, entry in enumerate(qa_list):
                    st.markdown(f"**Q{idx+1}:** {entry['q']}")
                    st.markdown(f"**A{idx+1}:** {entry['a']}")
                    st.markdown("---")
