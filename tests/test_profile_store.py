import unittest
import os
import shutil
from pathlib import Path
from agent.schemas import StudentProfile
from memory.profile_store import (
    load_profile,
    save_profile,
    update_topic_score,
    add_attempted_question,
    DATA_DIR
)

class TestProfileStore(unittest.TestCase):
    def setUp(self):
        # Use a separate test directory or clean up target directory
        self.student_id = "test_student_123"
        self.profile_path = DATA_DIR / f"{self.student_id}.json"
        if self.profile_path.exists():
            os.remove(self.profile_path)

    def tearDown(self):
        if self.profile_path.exists():
            os.remove(self.profile_path)

    def test_save_and_load(self):
        profile = StudentProfile(
            student_id=self.student_id,
            target_company="Amazon",
            target_role="SDE",
            days_to_interview=10,
            weak_topics=["OS", "DBMS"],
            attempted_questions=[],
            topic_scores={"OS": 0.0},
            last_updated=""
        )
        
        # Test save
        save_profile(profile)
        self.assertTrue(self.profile_path.exists())
        
        # Test load
        loaded = load_profile(self.student_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.target_company, "Amazon")
        self.assertEqual(loaded.target_role, "SDE")
        self.assertIn("OS", loaded.weak_topics)

    def test_update_score(self):
        profile = StudentProfile(
            student_id=self.student_id,
            target_company="Amazon",
            target_role="SDE",
            days_to_interview=10,
            weak_topics=["OS"],
            attempted_questions=[],
            topic_scores={},
            last_updated=""
        )
        save_profile(profile)
        
        update_topic_score(self.student_id, "OS", 0.85)
        loaded = load_profile(self.student_id)
        self.assertEqual(loaded.topic_scores["OS"], 0.85)

    def test_add_attempted_question(self):
        profile = StudentProfile(
            student_id=self.student_id,
            target_company="Amazon",
            target_role="SDE",
            days_to_interview=10,
            weak_topics=["OS"],
            attempted_questions=[],
            topic_scores={},
            last_updated=""
        )
        save_profile(profile)
        
        question = {"id": "q1", "correct": True}
        add_attempted_question(self.student_id, question)
        
        loaded = load_profile(self.student_id)
        self.assertEqual(len(loaded.attempted_questions), 1)
        self.assertEqual(loaded.attempted_questions[0]["id"], "q1")

if __name__ == "__main__":
    unittest.main()
