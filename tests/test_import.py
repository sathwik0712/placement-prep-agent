import asyncio
import os
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

async def main():
    print("Testing import and runner instantiation...")
    agent = Agent(
        name="placement_coach",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant."
    )
    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService(),
        app_name="placement_coach_app",
        auto_create_session=True
    )
    print("Runner initialized successfully.")
    
    # Try a simple dry run of run_async (will likely fail due to lack of API key, which is expected)
    user_msg = Content(role="user", parts=[Part.from_text(text="Hello")])
    os.environ["GEMINI_API_KEY"] = "dummy_key_for_testing"
    try:
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=user_msg
        ):
            print("Event yielded:", event)
    except Exception as e:
        print("Expected exception during run (due to dummy key):", type(e), e)

if __name__ == "__main__":
    asyncio.run(main())
