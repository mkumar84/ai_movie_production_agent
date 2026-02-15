import streamlit as st
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.team import Team
from agno.tools.serpapi import SerpApiTools
from textwrap import dedent
from typing import Optional

st.set_page_config(page_title="AI Movie Production Agent 🎬", layout="wide")

# --- Helper utilities -----------------------------------------------------
EXAMPLES = {
    "Time-travel heist": "A small crew attempts a high-stakes heist by jumping through time to steal a future technology.",
    "Romantic AI drama": "An AI assistant develops emotions and complicates the life of its human creator.",
    "Noir detective sci-fi": "A private detective in a neon city uncovers a conspiracy involving memory-forging.",
}


def generate_demo_output(idea: str, genre: str, audience: str, runtime: int) -> str:
    """Return a canned demo output (used when API keys are not provided)."""
    return dedent(
        f"""\
        **Demo — Script outline**

        Title: {idea[:60]} — {genre}

        Summary:
        A {genre.lower()} film for {audience.lower()} audiences. Estimated runtime: {runtime} minutes.

        Characters:
        - Protagonist: Alex — driven, clever, morally grey.
        - Sidekick: Jordan — loyal, funny relief.
        - Antagonist: Dr. Voss — charismatic, dangerous.

        Three-act structure:
        1) Setup — Introduce world and stakes.
        2) Confrontation — Heist / conflict escalates; twist revealed.
        3) Resolution — Big payoff and emotional arc.

        Suggested casting:
        - Alex: Actor A or Actor B — dramatic range needed.
        - Jordan: Actor C — strong comedic timing.
        - Dr. Voss: Actor D — intense presence.

        Notes: This is a demo response — provide API keys to generate AI-produced content.
        """
    )


def build_movie_producer(google_api_key: str, serp_api_key: Optional[str]) -> Team:
    """Constructs the Team (ScriptWriter + CastingDirector) when keys are provided.

    Gemini is imported lazily so the app can run in demo mode without `google-genai`.
    If the package is missing, raise a clear ImportError explaining how to install it.
    """
    try:
        from agno.models.google import Gemini
    except Exception as exc:
        raise ImportError(
            "`google-genai` is required to use the Gemini model. Install with `pip install google-genai`"
        ) from exc

    script_writer = Agent(
        name="ScriptWriter",
        model=Gemini(id="gemini-2.5-flash", api_key=google_api_key),
        description=dedent(
            """You are an expert screenplay writer. Given a movie idea and genre, develop a compelling script
            outline with character descriptions and key plot points."""
        ),
        instructions=[
            "Write a script outline with 3-5 main characters and key plot points.",
            "Outline the three-act structure and suggest 2-3 twists.",
            "Ensure the script aligns with the specified genre and target audience.",
        ],
    )

    tools = [SerpApiTools(api_key=serp_api_key)] if serp_api_key else []

    casting_director = Agent(
        name="CastingDirector",
        model=Gemini(id="gemini-2.5-flash", api_key=google_api_key),
        description=dedent(
            """You are a talented casting director. Given a script outline and character descriptions,
            suggest suitable actors for the main roles, considering their past performances and current availability."""
        ),
        instructions=[
            "Suggest 2-3 actors for each main role.",
            "Check actors' current status using `search_google` when available.",
            "Provide a brief explanation for each casting suggestion.",
            "Consider diversity and representation in your casting choices.",
        ],
        tools=tools,
    )

    movie_producer = Team(
        name="MovieProducer",
        model=Gemini(id="gemini-2.5-flash", api_key=google_api_key),
        members=[script_writer, casting_director],
        description="Experienced movie producer overseeing script and casting.",
        instructions=[
            "Ask ScriptWriter for a script outline based on the movie idea.",
            "Pass the outline to CastingDirector for casting suggestions.",
            "Summarize the script outline and casting suggestions.",
            "Provide a concise movie concept overview.",
        ],
        markdown=True,
    )

    return movie_producer


# --- UI (sidebar + main) -------------------------------------------------
with st.sidebar.expander("🔑 API keys & settings", expanded=True):
    google_api_key = st.text_input("Google API key (Gemini)", type="password")
    serp_api_key = st.text_input("SerpAPI key (optional, used for casting research)", type="password")
    demo_mode = st.checkbox("Run in demo mode (no API keys required)", value=False)
    st.write("Example prompts:")
    example = st.selectbox("Load example idea", ["", *EXAMPLES.keys()])
    if example:
        st.write(EXAMPLES[example])

st.title("AI Movie Production Agent 🎬")
st.caption("Generate script outlines and casting suggestions — enter keys to use AI, or run demo mode.")

# persistent state for results
if "result" not in st.session_state:
    st.session_state.result = ""

col_left, col_right = st.columns([1, 2])

with col_left:
    movie_idea = st.text_area("Describe your movie idea (required)", value=(EXAMPLES[example] if example else ""), height=150)
    genre = st.selectbox("Genre", ["Action", "Comedy", "Drama", "Sci-Fi", "Horror", "Romance", "Thriller"])
    target_audience = st.selectbox("Target audience", ["General", "Children", "Teenagers", "Adults", "Mature"])
    estimated_runtime = st.slider("Estimated runtime (minutes)", 60, 180, 120)

    st.markdown("---")
    run_col, clear_col, demo_col = st.columns([1, 1, 1])
    run_clicked = run_col.button("Develop Movie Concept")
    clear_clicked = clear_col.button("Clear Output")
    if demo_col.button("Copy example to input") and example:
        st.experimental_set_query_params()  # quick no-op to keep UI responsive

with col_right:
    st.subheader("Output")
    if st.session_state.result:
        st.markdown(st.session_state.result)
        st.download_button("Download result", st.session_state.result, file_name="movie_concept.md", mime="text/markdown")
    else:
        st.info("No output yet — enter an idea and click 'Develop Movie Concept' (or enable demo mode).")

# Clear output
if clear_clicked:
    st.session_state.result = ""

# Input validation
if run_clicked:
    if not movie_idea.strip():
        st.error("Please provide a short movie idea before generating.")
    elif demo_mode or (google_api_key and demo_mode):
        st.success("Running in demo mode — no external API calls will be made.")
        st.session_state.result = generate_demo_output(movie_idea, genre, target_audience, estimated_runtime)
    else:
        if not google_api_key:
            st.error("Google API key is required to run the AI agents. Enable demo mode to run without keys.")
        else:
            try:
                movie_producer = build_movie_producer(google_api_key, serp_api_key)
                with st.spinner("Generating with AI (this may take a few seconds)..."):
                    input_text = (
                        f"Movie idea: {movie_idea}, Genre: {genre}, "
                        f"Target audience: {target_audience}, Estimated runtime: {estimated_runtime} minutes"
                    )
                    response: RunOutput = movie_producer.run(input_text, stream=False)
                    st.session_state.result = response.content
                    st.success("Generation complete")
            except Exception as exc:
                st.session_state.result = ""
                st.error(f"Generation failed: {exc}")

# Footer / tips
with st.expander("ℹ️ Tips & next steps", expanded=False):
    st.write("- Use demo mode to try the app without API keys.")
    st.write("- Provide a focused movie idea (1–2 sentences) for best results.")
    st.write("- To enable richer casting suggestions, supply a SerpAPI key in the sidebar.")
