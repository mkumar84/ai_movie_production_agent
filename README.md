# ai_movie_production_agent

AI Movie Production Agent — a small Streamlit app that generates script outlines and casting suggestions using AI.

## Features ✅
- Generate a script outline (three-act structure, characters, twists)
- Suggest casting choices for main roles (optionally uses SerpAPI)
- Demo mode available so you can run the app without API keys
- Download generated concept as Markdown

## Requirements
- Python 3.8+
- See `requirements.txt` for exact dependencies (includes `streamlit` and `agno`).

## Quick start (local)
1. Create & activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run movie_prod.py
   ```
4. Open http://localhost:8501 in your browser. Use "Demo mode" in the sidebar to run without API keys, or paste your Google API key and SerpAPI key for live generation.

## Demo mode
If you don't have API keys, enable "Run in demo mode" in the sidebar — the app will return canned example output so you can test the UI and workflow.

## Deployment

### Streamlit Community Cloud (recommended)
- Connect this repository in Streamlit Cloud and set the following **Repository secrets**:
  - `GOOGLE_API_KEY` — your Google GenAI (Gemini) API key
  - `SERPAPI_KEY` — optional (used for casting research)
- Select the `main` branch and set the start file to `movie_prod.py`.

### GitHub Actions (CI)
- A basic CI workflow is included at `.github/workflows/ci.yml` that installs dependencies and performs a smoke import of the app on push/pull-request.

### Docker
- You can containerize the app with a simple Python + Streamlit Dockerfile if you prefer self-hosting.

> Note: `google-genai` was added to `requirements.txt` so Gemini works out-of-the-box. If you want me to pin a specific version, tell me which version to use.

## Usage tips
- Keep the movie idea short and focused (1–2 sentences).
- Provide SerpAPI key for live casting research and improved recommendations.

## License
MIT
