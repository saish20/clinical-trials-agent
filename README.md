# 🧠 Clinical Trials Research Assistant

An AI-powered research agent that allows you to:
- 🔎 Search for clinical trials by condition and location
- 📄 Get summarized insights using LLMs
- 💡 Highlight non-invasive or imaging-based trials
- 🗨️ Interactive Q&A about trial details
- 🌐 Web interface with Streamlit

---

## ⚙️ Installation

### 1. Clone the Repo

```bash
git clone https://github.com/saish20/clinical-trials-agent.git
cd clinical-trials-agent
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv .venv
```

**On Windows:**

```bash
.venv\Scripts\activate
```

**On Mac/Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API Keys

Create a `.env` file in the root directory with your Groq API key:

```ini
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🚀 Usage

### CLI Agent (agent_runner.py)

```bash
python app/agent_runner.py
```

- Accepts a free-text research goal like “Alzheimer’s in Ireland”
- Extracts condition and location using LLM
- Retrieves trials via ClinicalTrials.gov API
- Summarizes trial data and highlights non-invasive ones
- Lets user ask follow-up questions about selected trials

### Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

- Input condition/location via sidebar
- View summaries, highlighted trials, and chat interface
- Select trial and ask questions in natural language
- Preserves multi-turn chat history per selected trial

---

---

## 📌 Notes

- This project uses Groq’s LLaMA 3 API for fast and affordable LLM calls.
- Uses the [ClinicalTrials.gov v2 API](https://clinicaltrials.gov/api/gui) to search trial metadata.
