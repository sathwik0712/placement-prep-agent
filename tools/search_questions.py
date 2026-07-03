"""ADK tool for finding real interview questions via Google Search grounding."""
from google.genai import types
from pydantic import BaseModel

from tools._llm import MODEL_NAME, get_client


class _SearchedQuestion(BaseModel):
    question: str
    topic: str
    source_hint: str
    year_hint: str


async def search_interview_questions(
    company: str, topic: str, num: int = 5
) -> list[dict]:
    """Finds real, recently reported interview questions for a company and topic.

    Args:
        company: Target company, e.g. "Amazon".
        topic: Topic to search interview questions for, e.g. "DBMS".
        num: Number of questions to return.

    Returns:
        A list of dicts with keys: question, topic, source_hint, year_hint.
    """
    client = get_client()

    # Step 1: ground the search in real results via the google_search tool.
    grounded = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=(
            f"Search for {num} real interview questions that candidates have "
            f"reported being asked at {company} for the topic '{topic}'. "
            "For each question, note where it was reported (e.g. a forum, "
            "GeeksforGeeks, LeetCode discuss, Glassdoor) and the approximate year."
        ),
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    grounded_text = grounded.text or ""

    # Step 2: restructure the grounded findings into the required JSON shape.
    # response_schema can't be combined with the google_search tool in a
    # single call, so this is a separate structuring pass over step 1's output.
    structured = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=(
            "Extract the interview questions from the notes below into the "
            f"requested structure. Use '{topic}' as the topic for every item.\n\n"
            f"NOTES:\n{grounded_text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[_SearchedQuestion],
        ),
    )

    items = structured.parsed or []
    return [item.model_dump() for item in items[:num]]
