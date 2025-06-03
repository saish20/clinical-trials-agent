# Summarization prompt for clinical trials using API v2 response
def get_trial_summary_prompt(trials):
    bullet_points = ""
    for trial in trials:
        protocol = trial.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})

        title = id_module.get("briefTitle", "")
        status = status_module.get("overallStatus", "")
        phase = design_module.get("phaseList", {}).get("phases", [""])[0] if design_module.get("phaseList") else "N/A"
        sponsor = sponsor_module.get("leadSponsor", {}).get("name", "Unknown")

        bullet_points += f"- {title} (Sponsor: {sponsor}, Phase: {phase}, Status: {status})\n"

    return f"""
You are a healthcare research assistant. Below is a list of clinical trials:

{bullet_points}

Summarize:
1. What conditions are being studied?
2. What are the most common interventions?
3. Who are the main sponsors?
4. What phases are the trials in?
Provide your answer in a concise bullet point format.
"""
