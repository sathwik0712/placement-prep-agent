# Placement Prep Agent

An autonomous AI agent powered by Gemini designed to assist students with job placement preparation.

## Folder Structure

- `agent/`: Core agent logic and decision-making modules.
- `tools/`: Built-in tools and actions the agent can perform.
- `memory/`: Short-term and long-term memory management for user context.
- `ui/`: Streamlit user interface components.
- `tests/`: Automated unit and integration tests.

## Setup Instructions

1. **Prerequisites**: Ensure you have Python 3.11 installed.
2. **Environment Setup**:
   Create a virtual environment (named `myenv` as configured):
   ```bash
   uv venv myenv --python 3.11
   ```
3. **Activation**:
   Activate the virtual environment:
   ```bash
   source myenv/bin/activate
   ```
4. **Install Dependencies**:
   Install the required packages:
   ```bash
   uv pip install google-adk google-genai streamlit python-dotenv pydantic
   ```
5. **Configure Environment Variables**:
   Open `.env` and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```

## Run Streamlit UI

Launch the chat UI (sidebar for student_id / profile viewer, main panel for the coach chat):

```bash
streamlit run ui/app.py
```

Enter a `student_id` in the sidebar (defaults to `demo_student`) to load or start a profile,
or click **New session** to reset the current conversation. Existing students see their
saved profile (target company, days left, topic scores) in the sidebar, and the coach
greets them based on their previous progress.
