# LogLens AI 🔎

A **GitHub-ready AI/ML portfolio project** for anomaly detection in structured application and HTTP logs. It uses **Isolation Forest**, an unsupervised machine-learning algorithm, to flag unusual activity and explains obvious warning indicators. Includes a Streamlit UI, FastAPI endpoint, CLI, reproducible sample data, saved model, and automated tests.

> **Scope:** Educational prototype, not a security monitoring replacement. Synthetic examples and unsupervised scores are **not calibrated probabilities** or evidence of an attack. Models must be validated on representative real-world data.

## Features
- Upload CSV logs and view flagged records, anomaly trend, and investigation hints.
- REST API (`POST /analyze`) for software integrations.
- CLI for batch CSV processing.
- Completely offline; no API key or cloud service required.
- Fixed-seed synthetic demo data and local trained model.

## Requirements
Python 3.10+ (recommended 3.11 or 3.12); Windows/macOS/Linux.

## Installation
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run from the **repository root**:

```bash
python -m streamlit run app/streamlit_app.py
```
Streamlit: http://localhost:8501

API:
```bash
python -m uvicorn api.main:app --reload
```
Interactive API docs: http://127.0.0.1:8000/docs

CLI:
```bash
python -m loglens.cli --input data/sample_logs.csv --output analyzed_logs.csv
```

Train your own model:
```bash
python -m loglens.train
```

Test:
```bash
python -m pytest -q
```

## Expected CSV fields
| Column | Example | Notes |
|--|--|--|
| timestamp | 2026-10-24T08:00:00Z | ISO timestamp |
| level | ERROR | INFO/WARN/ERROR/etc |
| service | checkout | Component name |
| status | 503 | HTTP status 100-599 |
| duration_ms | 2500 | Request duration in milliseconds |
| bytes_sent | 950 | Response size |
| message | gateway timeout | Human-readable text |

## Approach
1. Parse and validate CSV values.
2. Derive features: HTTP status, duration, bytes, hour, error flag, slow flag, message length.
3. Apply a saved unsupervised `IsolationForest` model to score each event.
4. Flag anomalies where the model predicts `-1`; a larger `anomaly_score` means more unusual relative to training data.
5. Add transparent investigation hints (HTTP errors, slow requests, ERROR severity), which are **not** model explanations.

**Model limitation:** The demonstration model is trained on synthetic logs that contain injected unusual events; it does not recognize real threats reliably. Model files use joblib/pickle under the hood: **only load trusted model files**.

## Project layout
```
loglens-ai/
├── app/streamlit_app.py
├── api/main.py
├── loglens/engine.py
├── loglens/cli.py
├── loglens/train.py
├── data/sample_logs.csv
├── models/isolation_forest.joblib
├── tests/
├── .github/workflows/test.yml
├── requirements.txt
└── README.md
```

## Example API body
```json
{"events":[{"timestamp":"2026-10-24T08:00:00Z","level":"ERROR","service":"checkout","status":503,"duration_ms":3000,"bytes_sent":1200,"message":"Gateway timeout"}]}
```

## License
MIT
