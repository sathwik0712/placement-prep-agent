# PlacementPrep Agent — A Personalized AI Coach for Engineering Interviews

**Subtitle:** Tools + memory + reasoning. Built with Google ADK, Gemini 2.5, and a lot of vibe coding.

---

## Project Description

Every semester, students across Indian engineering colleges scramble for placements with generic YouTube playlists and stale question banks that don't know anything about them. As a CSD student at ANITS, Visakhapatnam, I've watched seniors and classmates repeat the same broken loop: no plan, no adaptive practice, no memory of what they already know. I built PlacementPrep Agent to fix that — a personalized coach that adapts to your target company, timeline, and weak topics, and actually remembers you between sessions.

The agent is built with Google's Agent Development Kit (ADK 2.0) on Gemini 2.5 Flash-Lite. It orchestrates five tools: `save_profile` and `update_profile` for persistent memory across sessions (stored as JSON with atomic writes), `search_interview_questions` for grounded retrieval of real recent company-specific questions via Google Search, `generate_quiz` for structured MCQ generation, and `evaluate_answer` as an LLM-grader. A student states their target company, role, days-to-interview, and weak topics — the agent saves a profile, produces a day-wise plan, runs adaptive diagnostic quizzes, grades answers, updates topic-mastery scores, and picks up exactly where the student left off in the next session.

The trickiest engineering problem was that Gemini doesn't allow combining `google_search` grounding with structured JSON output in the same call. I solved it with a two-step pipeline inside the search tool: one grounded call for retrieval, one structured call for normalization into a clean schema.

Built end-to-end in Google Antigravity IDE using vibe coding — natural language as the primary programming interface.

---

## Links

- **Code:** https://github.com/sathwik0712/placement-prep-agent
- **Video Demo:** _to be added after recording_

## Stack

- Google Agent Development Kit (ADK) 2.0
- Gemini 2.5 Flash-Lite
- Streamlit (UI)
- Python 3.11, Pydantic, uv
- Google Antigravity IDE (vibe coding)