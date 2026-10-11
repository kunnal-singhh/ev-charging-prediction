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

The service does not require an `.env` file. Render supplies `PORT`
automatically. Set `FRONTEND_URL` to the deployed Vercel URL if browser
requests need to call this service directly; normally browser traffic goes
through the backend.
