from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import joblib
import json
import os
import pandas as pd
import numpy as np

from app.feature_engineering import create_features
from app.occupancy_service import (
    get_occupancy_history,
    get_batch_occupancy_history,
    get_latest_timestamp
)


# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="EV Charging Occupancy Prediction API",
    description=(
        "Predicts EV charging station occupancy "
        "30 minutes into the future using the Research Champion XGBoost model."
    ),
    version="1.0.0"
)


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin
        for origin in [
            "http://localhost:5173",
            os.getenv("FRONTEND_URL")
        ]
        if origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================
# PATHS
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

FINAL_MODELS_DIR = os.path.join(
    BASE_DIR,
    "models",
    "final"
)

MODEL_PATH = os.path.join(
    FINAL_MODELS_DIR,
    "ev_occupancy_xgboost.pkl"
)

FEATURES_JSON_PATH = os.path.join(
    FINAL_MODELS_DIR,
    "features.json"
)

THRESHOLD_JSON_PATH = os.path.join(
    FINAL_MODELS_DIR,
    "threshold.json"
)




# ============================================
# LOAD MODEL & CONFIGURATION
# ============================================

print(f"Loading final model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

with open(FEATURES_JSON_PATH, "r", encoding="utf-8") as f:
    FEATURE_NAMES = json.load(f)

with open(THRESHOLD_JSON_PATH, "r", encoding="utf-8") as f:
    threshold_config = json.load(f)

THRESHOLD = float(threshold_config.get("threshold", 0.50))
HORIZON_MINUTES = int(threshold_config.get("prediction_horizon_minutes", 30))

print(f"Loaded features ({len(FEATURE_NAMES)}): {FEATURE_NAMES}")
print(f"Decision threshold: {THRESHOLD:.2f} | Horizon: {HORIZON_MINUTES}m")




# ============================================
# REQUEST MODELS
# ============================================

class PredictionRequest(BaseModel):
    station_id: str
    timestamp: str


class BatchPredictionRequest(BaseModel):
    predictions: List[PredictionRequest]


# ============================================
# ROOT & HEALTH
# ============================================

@app.get("/")
def root():
    return {
        "message": "EV Charging Occupancy Prediction API",
        "model": "XGBoost Experiment D (Full Features)",
        "features_count": len(FEATURE_NAMES),
        "threshold": THRESHOLD,
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
        "features": FEATURE_NAMES,
        "threshold": THRESHOLD
    }


# ============================================
# LATEST DATASET TIMESTAMP
# ============================================

@app.get("/latest-timestamp")
def latest_timestamp():
    try:
        latest = get_latest_timestamp()
        if pd.isna(latest):
            raise HTTPException(
                status_code=404,
                detail="No occupancy timestamp found"
            )
        return {
            "timestamp": latest.isoformat()
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Latest timestamp error:", error)
        raise HTTPException(
            status_code=500,
            detail="Failed to get latest timestamp"
        )


# ============================================
# SINGLE PREDICTION
# ============================================

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        occupancy_history = get_occupancy_history(
            request.station_id,
            request.timestamp
        )

        features = create_features(
            station_id=request.station_id,
            timestamp=request.timestamp,
            occupancy_history=occupancy_history
        )

        input_data = np.array(
            [[features[f] for f in FEATURE_NAMES]],
            dtype=np.float32
        )

        probability = float(model.predict_proba(input_data)[0][1])
        prediction = int(probability >= THRESHOLD)

        return {
            "station_id": request.station_id,
            "prediction": prediction,
            "status": "occupied" if prediction == 1 else "available",
            "occupancy_probability": round(probability, 4),
            "availability_probability": round(1.0 - probability, 4),
            "prediction_horizon_minutes": HORIZON_MINUTES,
            "occupancy_history": occupancy_history,
            "features_used": features
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    except Exception as error:
        print("Prediction error:", error)
        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )


# ============================================
# BATCH PREDICTION
# ============================================

@app.post("/predict/batch")
def predict_batch(request: BatchPredictionRequest):
    try:
        if not request.predictions:
            return {
                "total_stations": 0,
                "predictions": []
            }

        station_ids = [item.station_id for item in request.predictions]
        timestamp = request.predictions[0].timestamp

        histories = get_batch_occupancy_history(
            station_ids,
            timestamp
        )

        feature_rows = []
        all_features = []

        for item in request.predictions:
            occupancy_history = histories[item.station_id]
            features = create_features(
                station_id=item.station_id,
                timestamp=item.timestamp,
                occupancy_history=occupancy_history
            )
            feature_rows.append([features[f] for f in FEATURE_NAMES])
            all_features.append(features)

        input_matrix = np.array(feature_rows, dtype=np.float32)
        probabilities = model.predict_proba(input_matrix)[:, 1]

        results = []
        for index, item in enumerate(request.predictions):
            prob = float(probabilities[index])
            prediction = int(prob >= THRESHOLD)

            results.append({
                "station_id": item.station_id,
                "prediction": prediction,
                "status": "occupied" if prediction == 1 else "available",
                "occupancy_probability": round(prob, 4),
                "availability_probability": round(1.0 - prob, 4),
                "prediction_horizon_minutes": HORIZON_MINUTES,
                "occupancy_history": histories[item.station_id],
                "features_used": all_features[index]
            })

        return {
            "total_stations": len(results),
            "predictions": results
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    except Exception as error:
        print("Batch prediction error:", error)
        raise HTTPException(
            status_code=500,
            detail="Batch prediction failed"
        )