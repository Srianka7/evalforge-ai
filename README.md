
# EvalForge AI

### AI Response Evaluation & Quality Assurance Platform

EvalForge AI is an AI-powered evaluation platform designed to assess the quality of AI-generated responses using automated scoring, weighted evaluation criteria, and detailed explanations.

The project combines a local Large Language Model (LLM) with a FastAPI backend and an interactive web dashboard to provide a structured AI response evaluation workflow.

## Features

- **Automatic AI Evaluation:** Uses Qwen 3 4B through Ollama to evaluate AI-generated responses.
- **Manual Evaluation:** Allows users to assign scores to evaluation criteria.
- **Multi-Criteria Scoring:** Evaluates accuracy, relevance, completeness, and clarity.
- **Weighted Scoring:** Calculates an overall score out of 100.
- **AI-Generated Explanations:** Provides individual explanations for each evaluation criterion.
- **Evaluation History:** Stores and retrieves previous evaluations.
- **Analytics Dashboard:** Displays total evaluations, average scores, and grade distribution.
- **Performance Trends:** Tracks average evaluation scores over time.
- **Responsive Interface:** Provides a dashboard optimized for desktop and mobile screens.
- **SQLite Database:** Persists evaluation results and explanations.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI Model | Qwen 3 4B |
| Local LLM Runtime | Ollama |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Testing | Pytest |
| API Documentation | Swagger UI |

## Evaluation Criteria

| Criterion | Weight |
|---|---:|
| Accuracy | 40% |
| Relevance | 25% |
| Completeness | 20% |
| Clarity | 15% |

Each criterion receives a score from 0 to 5. The weighted result is converted into a score out of 100.

### Grade Classification

| Score | Grade |
|---|---|
| 90–100 | Excellent |
| 75–89.99 | Good |
| 60–74.99 | Fair |
| 40–59.99 | Poor |
| Below 40 | Very Poor |

## Project Architecture

```text
evalforge-ai/
├── backend/
│   ├── src/
│   │   └── evalforge/
│   │       ├── main.py
│   │       ├── database.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── scoring.py
│   │       └── ai_evaluator.py
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Ollama
- Qwen 3 4B model

### 1. Clone the repository

```bash
git clone https://github.com/Srianka7/evalforge-ai.git
cd evalforge-ai
```

### 2. Set up the backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

If your project dependencies are not configured with a `dev` optional dependency group, install the packages listed in `pyproject.toml` instead.

### 3. Install the AI model

Install Ollama from:

https://ollama.com/

Download the model:

```bash
ollama pull qwen3:4b
```

Ensure Ollama is running locally.

### 4. Start the backend

From the backend directory:

```bash
PYTHONPATH=src uvicorn evalforge.main:app --reload
```

Backend URL:

http://127.0.0.1:8001

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
python3 -m http.server 5501
```

Open the dashboard:

http://127.0.0.1:5501/index.html

## API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

http://127.0.0.1:8001/docs

### Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/evaluations/score` | Manual evaluation |
| POST | `/evaluations/auto` | Automatic AI evaluation |
| GET | `/evaluations` | Retrieve evaluation history |
| GET | `/evaluations/{id}` | Retrieve evaluation details |
| GET | `/analytics` | Dashboard analytics |
| GET | `/analytics/trends` | Evaluation performance trends |

## Testing

Run backend tests:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=src pytest -v
```

## Current Project Status

The project includes working manual and automatic evaluation workflows, persistent evaluation history, AI-generated explanations, analytics, and responsive dashboard components.

## Future Enhancements

- Advanced evaluation metrics
- Exportable evaluation reports
- Additional AI model integrations
- More detailed historical analytics
- User authentication and role management

## Author

**Srianka**

GitHub: [Srianka7](https://github.com/Srianka7)

---

*EvalForge AI — Building reliable AI response evaluation workflows.*
