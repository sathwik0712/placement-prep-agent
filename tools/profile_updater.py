"""ADK tools that create and update a student's persisted profile."""
from agent.schemas import StudentProfile
from memory.profile_store import (
    load_profile,
    save_profile as persist_profile,
    update_topic_score,
)


def update_profile(student_id: str, topic: str, score: float) -> dict:
    """Updates a student's score for a topic and returns their latest scores.

    Args:
        student_id: The unique identifier for the student.
        topic: The topic whose score is being updated.
        score: The new score for the topic, from 0.0 to 1.0.

    Returns:
        The student's updated topic_scores dict.
    """
    update_topic_score(student_id, topic, score)
    return load_profile(student_id).topic_scores


def save_profile(
    student_id: str,
    target_company: str,
    target_role: str,
    days_to_interview: int,
    weak_topics: list[str],
) -> dict:
    """Creates and persists a new student profile.

    Args:
        student_id: The unique identifier for the student.
        target_company: The company the student is preparing for.
        target_role: The role the student is targeting.
        days_to_interview: Number of days remaining until the interview.
        weak_topics: Topics the student says they are weak in.

    Returns:
        The newly created StudentProfile as a dict.
    """
    profile = StudentProfile(
        student_id=student_id,
        target_company=target_company,
        target_role=target_role,
        days_to_interview=days_to_interview,
        weak_topics=weak_topics,
        attempted_questions=[],
        topic_scores={},
        last_updated="",
    )
    persist_profile(profile)
    return profile.model_dump()
