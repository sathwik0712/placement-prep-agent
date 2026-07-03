"""Streamlit demo UI for the placement prep coach agent."""
import os
import sys
from pathlib import Path
from uuid import uuid4

# `streamlit run` does not put the project root on sys.path (only the
# directory containing the streamlit executable and this script's own
# directory), so agent/memory/tools would otherwise fail to import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from agent.root_agent import build_initial_message, create_agent
from memory.profile_store import load_profile

load_dotenv()

APP_NAME = "placement_coach_app"

st.set_page_config(page_title="Placement Prep Coach", page_icon="🎯")

if not os.environ.get("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
    st.stop()


@st.cache_resource
def get_runner() -> Runner:
    return Runner(
        agent=create_agent(),
        session_service=InMemorySessionService(),
        app_name=APP_NAME,
        auto_create_session=True,
    )


async def _stream_reply(runner, user_id, session_id, message_text):
    """Yields text chunks as the model generates them (ADK SSE streaming mode)."""
    content = Content(role="user", parts=[Part.from_text(text=message_text)])
    run_config = RunConfig(streaming_mode=StreamingMode.SSE)
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
        run_config=run_config,
    ):
        if event.partial and event.content and event.content.parts:
            has_text = any(part.text for part in event.content.parts)
            has_function_call = any(part.function_call for part in event.content.parts)
            if has_text and not has_function_call:
                text = "".join(part.text or "" for part in event.content.parts)
                if text:
                    yield text


def _send_and_render(runner, user_id, session_id, message_text) -> str:
    with st.chat_message("assistant"):
        try:
            return st.write_stream(_stream_reply(runner, user_id, session_id, message_text))
        except Exception as e:
            error_text = f"Error communicating with Gemini: {e}"
            st.error(error_text)
            return error_text


def _reset_session(student_id: str) -> None:
    """(Re)starts the conversation for a student, loading their profile deterministically."""
    st.session_state.student_id = student_id
    st.session_state.session_id = str(uuid4())
    st.session_state.profile = load_profile(student_id) if student_id else None
    st.session_state.messages = []
    st.session_state.pending_first_turn = True


with st.sidebar:
    st.header("Student")
    default_id = st.session_state.get("student_id", "demo_student")
    student_id_input = st.text_input("student_id", value=default_id, key="student_id_widget")
    new_session_clicked = st.button("New session")

    if "student_id" not in st.session_state:
        _reset_session(student_id_input or "demo_student")
    elif new_session_clicked or student_id_input != st.session_state.student_id:
        _reset_session(student_id_input or "demo_student")

    st.divider()
    st.subheader("Profile")
    profile = st.session_state.get("profile")
    if profile:
        st.metric("Target company", profile.target_company)
        st.metric("Days left", profile.days_to_interview)
        if profile.topic_scores:
            st.bar_chart(pd.Series(profile.topic_scores, name="score"))
        else:
            st.caption("No quiz scores recorded yet.")
    else:
        st.caption("No saved profile yet - it will be created after your first chat.")

st.title("🎯 Placement Prep Coach")

for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

runner = get_runner()
user_id = st.session_state.student_id or "terminal_student"

if st.session_state.get("pending_first_turn"):
    st.session_state.pending_first_turn = False
    first_message_text = build_initial_message(st.session_state.profile)
    reply = _send_and_render(runner, user_id, st.session_state.session_id, first_message_text)
    st.session_state.messages.append({"role": "assistant", "content": reply})

if prompt := st.chat_input("Message your coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    reply = _send_and_render(runner, user_id, st.session_state.session_id, prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
