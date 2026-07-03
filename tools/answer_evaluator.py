"""ADK tool for grading a student's answer with Gemini."""
from google.genai import types

from agent.schemas import EvaluationResult
from tools._llm import MODEL_NAME, get_client


async def evaluate_answer(
    question: str, student_answer: str, correct_answer: str, topic: str
) -> dict:
    """Grades a student's answer to an interview question.

    Args:
        question: The interview question that was asked.
        student_answer: The answer the student gave.
        correct_answer: The reference correct answer.
        topic: The topic the question belongs to.

    Returns:
        An EvaluationResult dict: is_correct, score, feedback, and
        suggested_next_topic.
    """
    client = get_client()
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=(
            "You are a strict but encouraging placement interview grader.\n"
            f"Topic: {topic}\n"
            f"Question: {question}\n"
            f"Reference correct answer: {correct_answer}\n"
            f"Student's answer: {student_answer}\n\n"
            "Judge whether the student's answer is correct, score it from 0.0 "
            "to 1.0, give short encouraging-but-honest feedback, and suggest "
            "a next topic to study if the student is struggling (otherwise "
            "leave it null)."
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResult,
        ),
    )
    result = response.parsed or EvaluationResult(
        is_correct=False,
        score=0.0,
        feedback="Could not evaluate the answer, please try again.",
        suggested_next_topic=None,
    )
    return result.model_dump()
