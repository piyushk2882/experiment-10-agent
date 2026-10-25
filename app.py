
import os
import time
import logging
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

# Basic logging for monitoring
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="centered",
)

st.title("🔎 AI Research Agent")
st.write(
    "Enter a topic to search the web and generate a concise "
    "research brief containing exactly three bullet points."
)

def create_llm():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured. "
            "Set it in your environment or hosting secrets."
        )

    return ChatOpenAI(
        model=os.environ.get(
            "OPENROUTER_MODEL", "openrouter/free"
        ),
        temperature=0.3,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        max_retries=2,
        timeout=60,
    )

def search_web(topic):
    search_tool = DuckDuckGoSearchRun()
    return search_tool.run(
        f"Recent developments and reliable information about {topic}"
    )

def summarize_results(topic, search_results):
    llm = create_llm()

    prompt = f"""
You are a careful research assistant.

Topic: {topic}

Search results:
{search_results}

Write exactly three bullet points summarizing the most
important findings. Be concise and factual. Do not invent
facts or imply that a search result proves something it
does not establish. Mention uncertainty when appropriate.
Return only the three bullet points, with no introduction.
"""
    response = llm.invoke(prompt)
    return response.content

def research_workflow(topic):
    start = time.perf_counter()
    logger.info("Research request received: topic=%r", topic)

    try:
        with st.status("Searching and summarizing...", expanded=True) as status:
            st.write("Stage 1/2: Searching the web...")
            results = search_web(topic)

            if not results or not results.strip():
                raise RuntimeError("The search returned no results.")

            st.write("Stage 2/2: Summarizing search results...")
            brief = summarize_results(topic, results)

            status.update(
                label="Research brief ready",
                state="complete",
                expanded=False,
            )

        elapsed = time.perf_counter() - start
        logger.info(
            "Research request completed: topic=%r duration_seconds=%.2f",
            topic,
            elapsed,
        )
        return brief, elapsed

    except Exception:
        elapsed = time.perf_counter() - start
        logger.exception(
            "Research request failed: topic=%r duration_seconds=%.2f",
            topic,
            elapsed,
        )
        raise

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g., Renewable energy in India",
    )
    submitted = st.form_submit_button(
        "Generate research brief",
        type="primary",
    )

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            brief, elapsed = research_workflow(topic.strip())
            st.subheader("Your three-point research brief")
            st.markdown(brief)
            st.caption(f"Request completed in {elapsed:.2f} seconds.")
        except Exception as exc:
            st.error(
                "The workflow failed. Check your API key, model "
                "access, network connection, and application logs."
            )
            st.caption(f"Error: {exc}")
