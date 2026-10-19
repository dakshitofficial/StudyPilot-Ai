# 🎓 StudyPilot AI

**Turn Your Notes into Knowledge.**

StudyPilot AI is a local GenAI-powered study assistant built with Python, Streamlit, and Ollama.

## Features
- 📚 AI Notes Summarizer
- 🧠 Interactive MCQ Quiz with Scoring
- 📅 7-Day Study Planner
- 💬 AI Doubt Solver
- 📄 PDF Text Extraction
- 🔒 Local AI using Ollama — no paid API required

## Tech Stack
Python · Streamlit · Ollama · Qwen 2.5 1.5B · Requests · pypdf

## Installation

Install [Python](https://www.python.org/) and [Ollama](https://ollama.com/download).

Install the model:

```bash
ollama pull qwen2.5:1.5b
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal.

## Limitations
- Ollama must be installed and running locally.
- Scanned PDFs requiring OCR are not supported in this version.
- Large documents may be truncated before processing.

## Author
**Daksh Verma**

A student-built GenAI portfolio project.
