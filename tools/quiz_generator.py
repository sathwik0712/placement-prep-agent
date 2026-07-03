"""ADK tool for generating quiz questions with Gemini structured output."""
from google.genai import types

from agent.schemas import QuizQuestion
from tools._llm import MODEL_NAME, get_client


async def generate_quiz(
    topic: str, difficulty: str, num_questions: int = 5
) -> list[dict]:
    """Generates a mixed MCQ / short-answer quiz for a topic.

    Args:
        topic: Subject to quiz on, e.g. "Operating Systems".
        difficulty: One of "easy", "medium", "hard".
        num_questions: How many questions to generate.

    Returns:
        A list of QuizQuestion dicts, mixing MCQ and short-answer questions.
    """
    client = get_client()
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=(
            f"Generate {num_questions} {difficulty}-difficulty interview quiz "
            f"questions on '{topic}' for an Indian engineering student "
            "preparing for placements. Mix multiple-choice questions (with 4 "
            "options) and short-answer questions (leave options empty for "
            "those). Give each question a unique id, the correct answer, and "
            "a short explanation."
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[QuizQuestion],
        ),
    )
    questions = response.parsed or []
    return [q.model_dump() for q in questions]
