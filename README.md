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
   ```
