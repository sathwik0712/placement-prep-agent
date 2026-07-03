import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from agent.schemas import StudentProfile

# Resolve the storage directory relative to this file
DATA_DIR = Path(__file__).parent / "data"

def _get_path(student_id: str) -> Path:
    """Returns the Path to the student's JSON profile, ensuring parent directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"{student_id}.json"

def load_profile(student_id: str) -> StudentProfile | None:
    """Loads a StudentProfile from the JSON store.

    Args:
        student_id: The unique identifier for the student.

    Returns:
        The StudentProfile object if found and successfully validated, or None.
    """
    path = _get_path(student_id)
    print(f"[PROFILE STORE] Reading profile from {path}")
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return StudentProfile.model_validate(data)
    except Exception:
        return None

def save_profile(profile: StudentProfile) -> None:
    """Saves a StudentProfile to the JSON store using an atomic write.

    Writes to a temporary file in the destination directory and then renames
    the file to the target path. This guarantees atomic replacement and avoids
    file corruption. Last updated timestamp is updated before saving.

    Args:
        profile: The StudentProfile object to save.
    """
    path = _get_path(profile.student_id)
    print(f"[PROFILE STORE] Writing profile to {path}")
    profile.last_updated = datetime.utcnow().isoformat()
    data = profile.model_dump()

    temp_dir = path.parent
    # Create a temp file in the same directory to ensure atomic renaming on the same filesystem mount
    fd, temp_file_path = tempfile.mkstemp(dir=temp_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file_path, path)
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e

def update_topic_score(student_id: str, topic: str, score: float) -> None:
    """Updates the score of a specific topic in the student's profile.

    Loads the profile, updates the scores dictionary, and saves the profile.

    Args:
        student_id: The unique identifier for the student.
        topic: The name of the subject or topic.
        score: The updated performance score.

    Raises:
        ValueError: If no profile exists for the given student_id.
    """
    profile = load_profile(student_id)
    if not profile:
        raise ValueError(f"Student profile with ID {student_id} not found.")
    profile.topic_scores[topic] = score
    save_profile(profile)

def add_attempted_question(student_id: str, question_dict: dict) -> None:
    """Appends a dictionary containing details of an attempted question to the student's history.

    Loads the profile, appends the attempt, and saves the profile.

    Args:
        student_id: The unique identifier for the student.
        question_dict: Dictionary containing metadata/details of the attempted quiz question.

    Raises:
        ValueError: If no profile exists for the given student_id.
    """
    profile = load_profile(student_id)
    if not profile:
        raise ValueError(f"Student profile with ID {student_id} not found.")
    profile.attempted_questions.append(question_dict)
    save_profile(profile)
