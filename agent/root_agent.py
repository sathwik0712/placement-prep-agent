import asyncio
import functools
import inspect
import os
import sys
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from memory.profile_store import load_profile
from tools.answer_evaluator import evaluate_answer
from tools.profile_updater import save_profile, update_profile
from tools.quiz_generator import generate_quiz
from tools.search_questions import search_interview_questions

# Load environment variables from .env file
load_dotenv()

# System instruction for the placement coach
COACH_SYSTEM_INSTRUCTION = """
You are a placement preparation coach for Indian engineering students. 
On the first turn (e.g. when the user starts the chat or says hello), your task is to ask the student for the following details:
(a) Target company (e.g., TCS, Infosys, Amazon, Google, etc.)
(b) Target role (e.g., Software Development Engineer, Data Analyst, Systems Engineer, etc.)
(c) Days remaining until the interview
(d) Topics they feel weak in (e.g., Data Structures, Algorithms, DBMS, OOPs, Computer Networks, etc.)

Once the student provides these details, analyze their profile and:
1. Produce a day-wise study plan tailored to the remaining days and topics they feel weak in.
2. Offer to start a quiz to test their knowledge on those topics.
Keep your responses encouraging, professional, and tailored to the typical recruitment processes of companies in India.

If this is a new student (no existing profile), you MUST call save_profile() with their
target_company, target_role, days_to_interview, and weak_topics as soon as you have collected
all four of those details - before producing the study plan. This is not optional.

TOOL USE RULES (non-negotiable):
- You MUST call search_interview_questions() before quoting any real company-specific question. Never fabricate.
- You MUST call generate_quiz() to produce quiz questions. Never write them inline.
- You MUST call evaluate_answer() after every student answer.
- You MUST call update_profile() after every evaluation.
- You MUST call save_profile() the moment you have company + role + days + weak_topics.
Violating these = failure.
"""

def _log_tool_call(name, args, kwargs, result):
    call_args = ", ".join(
        [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
    )
    preview = repr(result)
    if len(preview) > 200:
        preview = preview[:200] + "..."
    print(f"[TOOL CALLED] {name}({call_args}) -> {preview}", file=sys.stderr)


def log_tool_call(func):
    """Wraps a tool function to trace its calls/returns to stderr, without
    altering its return value or signature."""
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            _log_tool_call(func.__name__, args, kwargs, result)
            return result
        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        _log_tool_call(func.__name__, args, kwargs, result)
        return result
    return sync_wrapper


def create_agent():
    return Agent(
        name="placement_coach",
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
        instruction=COACH_SYSTEM_INSTRUCTION,
        tools=[
            log_tool_call(search_interview_questions),
            log_tool_call(generate_quiz),
            log_tool_call(evaluate_answer),
            log_tool_call(update_profile),
            log_tool_call(save_profile),
        ],
    )

def build_initial_message(profile) -> str:
    """Builds the first-turn message: returning-student context, or a fresh greeting."""
    if profile:
        return (
            "Returning student. Profile loaded: "
            f"target_company={profile.target_company}, "
            f"target_role={profile.target_role}, "
            f"days_to_interview={profile.days_to_interview}, "
            f"weak_topics={profile.weak_topics}, "
            f"topic_scores={profile.topic_scores}, "
            f"last_updated={profile.last_updated}. "
            "Greet them by acknowledging their previous progress and suggest "
            "the next step based on their weakest topic."
        )
    return "Hi Coach, I need help preparing for placements."


async def chat_loop():
    # Verify API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
        sys.exit(1)

    agent = create_agent()
    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService(),
        app_name="placement_coach_app",
        auto_create_session=True
    )

    student_id = input("Enter your student_id (or press Enter for a new session): ").strip()

    user_id = student_id or "terminal_student"
    session_id = "current_session"

    # Deterministic lookup in Python - never delegated to the LLM.
    profile = load_profile(student_id) if student_id else None

    print("\n--- Placement Prep Coach Chat Initiated ---")
    print("Type 'exit' or 'quit' to end the chat.\n")

    first_message = Content(role="user", parts=[Part.from_text(text=build_initial_message(profile))])

    try:
        print("Coach: ", end="", flush=True)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=first_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"\nError communicating with Gemini: {e}")
        return

    # Subsequent turns
    while True:
        try:
            user_input = input("Student: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye and good luck with your placements!")
            break

        user_message = Content(role="user", parts=[Part.from_text(text=user_input)])
        
        try:
            print("Coach: ", end="", flush=True)
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print("\n")
        except Exception as e:
            print(f"\nError communicating with Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(chat_loop())
