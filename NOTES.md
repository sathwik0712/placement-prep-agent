# Deferred verification (post-UI)

Prompt 8 (system-instruction reasoning loop) is considered functionally implemented — 
save_profile auto-fires on turn 1, tool-use contract is respected, session-resume 
scaffolding is in place. However, we have NOT yet observed a clean full-loop run:
  Turn 1: profile save        ✅ observed
  Turn 2: search_interview_questions   ✅ observed (then hit 429)
  Turn 3: generate_quiz       ❌ never reached
  Turn 4: evaluate_answer     ❌ never reached
  Turn 5: update_profile      ❌ never reached
  Turn 6: returning-student profile load into first LLM turn   ❌ not verified

Both failed attempts were external (429 quota exhaustion, 503 model overload) — 
not code defects. Do NOT modify the agent, tools, or system instruction to "fix" 
this. The verification is a runtime observation, pending fresh quota + stable model.

TODO after Prompt 9 (Streamlit UI) is built:
  1. Reset quota window (wait for daily reset or use fresh account).
  2. Run one clean 5-turn session through the UI.
  3. Confirm all 5 [TOOL CALLED] log lines appear in order.
  4. Confirm returning-student turn loads profile and references topic_scores.
  5. If any tool doesn't fire → THEN revisit system instruction, not before.

For now: proceed to Prompt 9 (Streamlit UI build) with no changes to Prompt 8 code.
