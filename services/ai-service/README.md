# EVConnect AI Service

This service exposes the FastAPI occupancy prediction API.

## Run locally

```powershell
cd services/ai-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The model and runtime lookup data are kept inside this service so it can be
deployed independently from the Node backend and React frontend.
