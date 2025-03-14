# Logic Lens

A Python application for generating text using Google's Gemini AI model and LangSmith tracing.

## Project Overview

This project is a text generation application that:

- Uses Google's Gemini 2.0 Flash model for text generation
- Includes LangSmith for tracing and monitoring generation pipelines
- Has potential for API development with FastAPI (not yet implemented)

## Prerequisites

- Python 3.8+ installed
- Google Generative AI API key
- LangSmith account (for tracing functionality)

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd logic-lens
   ```

2. Create a virtual environment using Mamba:

   ```
   # For Windows
   mamba create -n venv python=3.8
   conda activate venv

   # For macOS/Linux
   mamba create -n venv python=3.8
   conda activate venv
   ```

3. Install the required dependencies:

   ```
   pip install -r requirement.txt
   ```

## Environment Setup

1. Rename `.env.example` to `.env` and fill up with data.

```
   GENAI_API_KEY=your_google_genai_api_key
```

2. Where to get the API keys:
   - **Google Generative AI API Key**: Sign up at [Google AI Studio](https://makersuite.google.com/)
   - **LangSmith**: Sign up at [LangSmith](https://smith.langchain.com/) and follow their documentation to set up tracing

## Running the Application

Currently, the application has a test function in `main.py` that can be used to verify the setup:

1. Ensure your `.env` file is properly configured
2. Run the main script:

```python
cd api
uvicorn server:app --reload
```

3. If successful, you should see output from the Weaviate connection test

## Development Notes

- The current implementation includes a basic pipeline for text generation with the Gemini model
- The generation config is set up with a playful system instruction
- LangSmith tracing is implemented via the `@traceable` decorator
- FastAPI is included in the requirements but not yet implemented in the code

## Extending the Application

- To build an API around the current functionality, implement FastAPI routes
- Customize the generation config parameters to adjust the model's output style and length

## Troubleshooting

- If you have issues with the Gemini API, ensure that the `GENAI_API_KEY` is correctly set in your `.env` file.
- If you have issues with LangSmith tracing, ensure that you have set up your LangSmith environment variables correctly.
