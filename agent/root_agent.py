import asyncio
import os
import sys
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

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
"""

def create_agent():
    return Agent(
        name="placement_coach",
        model="gemini-2.5-flash",
        instruction=COACH_SYSTEM_INSTRUCTION
    )

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

    user_id = "terminal_student"
    session_id = "current_session"

    print("\n--- Placement Prep Coach Chat Initiated ---")
    print("Type 'exit' or 'quit' to end the chat.\n")

    # Initial turn: Send a greeting to trigger the agent's first response
    first_message = Content(role="user", parts=[Part.from_text(text="Hi Coach, I need help preparing for placements.")])
    
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
