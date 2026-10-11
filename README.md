# EVConnect: Machine Learning-Based EV Charging Station Occupancy Prediction & Full-Stack Research Prototype

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Node.js: 18+](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![XGBoost](https://img.shields.io/badge/Model-XGBoost%20Exp%20D-orange.svg)](https://xgboost.readthedocs.io/)

---

## 1. Project Overview

**EVConnect** is a full-stack research prototype designed to address the challenge of short-term electric vehicle (EV) charging station occupancy forecasting. Using empirical session transaction records from the **Adaptive Charging Network (ACN-Data)**, the project implements a leak-free supervised machine learning pipeline to predict binary station occupancy 30 minutes into the future ($T + 30\text{ min}$).

The system combines:
1. **Machine Learning Pipeline:** A gradient-boosted decision tree (**XGBoost Experiment D**) trained on an 8-feature representation with class-imbalance reweighting (`scale_pos_weight = 27.28`).
2. **FastAPI Microservice:** A high-performance Python inference API serving predictions with sub-10ms model evaluation.
3. **Node.js / Express Backend:** An application server handling JWT authentication, MongoDB data persistence, and dynamic multi-factor station recommendation scoring.
4. **React Frontend:** A modern, responsive dashboard interface providing live station statuses, availability probabilities, and charging session management.

> **Academic Note:** EVConnect is developed as an academic research prototype and demonstration platform. It is not an enterprise-scale commercial dispatch system.

---

## 2. Problem Statement

Public and workplace EV charging infrastructure is characterized by extended session dwell times (typically 1 to 5 hours). Drivers arriving at charging plazas face uncertainty regarding real-time availability, leading to queue delays and range anxiety.

The technical problem is formulated as a **30-minute-ahead binary classification task**:
$$\hat{Y}(s_i, T) = O(s_i, T + 30\text{ min}) \in \{0, 1\}$$

where:
- $s_i \in S$ denotes one of $M = 55$ discrete charging stations.
- $T$ represents the current 30-minute interval.
- $O(s_i, t) = 1$ if station $s_i$ is actively occupied at interval $t$, and $0$ if available.
- Features must be derived **strictly** from observations at or before time $T$ ($\tau \le T$) and static training-split priors, preventing temporal lookahead leakage.

### Key Analytical Challenges
- **Severe Class Imbalance:** In workplace charging, chargers remain unoccupied for long overnight and weekend periods (~3.54% positive occupancy prevalence in training data).
- **Strong Temporal Autocorrelation:** The state at $T-30\text{ min}$ strongly correlates with state at $T+30\text{ min}$, making simple persistence heuristics a formidable baseline.
- **Station Heterogeneity:** Individual chargers exhibit distinct usage intensity based on parking geometry and site layout.

---

## 3. Project Objectives

1. **O1 (Reproducible Data Pipeline):** Ingest raw ACN transaction logs and construct an aligned 30-minute regularized temporal occupancy grid across 55 stations.
2. **O2 (Leak-Free Feature Engineering):** Engineer eight features spanning Temporal, Historical Lag, Station Operational, and Session Duration groups, with all priors frozen from the training partition.
3. **O3 (Systematic Model Benchmarking & Ablation):** Implement 12 distinct model configurations evaluating Logistic Regression, Random Forest, and XGBoost across 4 progressive feature sets (Experiments A–D).
4. **O4 (Validation-Based Model Selection):** Determine the champion model and decision threshold ($\tau = 0.50$) strictly on the validation partition using Precision-Recall AUC (PR-AUC) and F1 metrics.
5. **O5 (Statistical Robustness Verification):** Evaluate the champion model on held-out test data using 1,000 paired bootstrap resamples to establish 95% confidence intervals and test significance against baseline models.
6. **O6 (Full-Stack Prototype Deployment):** Integrate the final serialized model into an end-to-end web platform via FastAPI, Express, and React.

---

## 4. Research Contribution

1. **Leak-Free Chronological Pipeline:** Demonstrated an end-to-end data transformation pipeline enforcing strict chronological boundaries (Train / Validation / Test) without future-data contamination.
2. **Systematic Feature Ablation:** Quantified the predictive contribution of lag features vs. static station operational priors across linear, bagging, and boosting model families.
3. **PR-AUC Calibration Advantage:** Established that while a naive persistence baseline achieves competitive F1 on autocorrelated data, the XGBoost model delivers a statistically significant **+0.0275 PR-AUC gain** (95% CI: `[+0.0191, +0.0358]`), enabling superior continuous probability calibration for ranking.
4. **End-to-End Architectural Integration:** Validated the live operational flow connecting ML inference microservices to a user-facing recommendation interface.

---

## 5. EVConnect Application Capabilities

- **Real-Time Forecasting Dashboard:** Live 30-minute forward occupancy forecasts and availability probabilities for all 55 stations.
- **Intelligent Recommendation Ranking:** Automatic ranking of stations (Rank 1 to 55) based on a weighted multi-factor utility score.
- **Deep Station Inspection:** Detailed station views with connector metadata, historical occupancy state, and feature breakdown.
- **Session Scheduling Lifecycle:** User booking of scheduled charging slots, active session monitoring, and cancellation.
- **Favorites & Personalization:** User-specific bookmarking of preferred charging stations with persistent storage.
- **JWT-Protected Security:** Role-based authentication and secure credential hashing with `bcryptjs`.

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Client (Vite :5173)                   │
│         - Dashboard & Stats       - Station Details             │
│         - Favorites Management     - Session Booking / Cancel    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP (JWT Bearer Auth)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               Node.js / Express Backend (:5000)                 │
│         - Authentication API      - Session Controller          │
│         - Station Metadata        - Recommendation Engine       │
└───────────────┬────────────────────────────────┬────────────────┘
                │                                │
      Mongoose  ▼                      HTTP POST │ AbortSignal 5s
┌──────────────────────────────┐                 ▼
│     MongoDB Atlas Database   │   ┌──────────────────────────────┐
│  - Users (Credentials, Favs) │   │  FastAPI ML Microservice     │
│  - Stations (Metadata, Specs)│   │  (Python :8000)              │
│  - ChargingSessions          │   │  - /health                   │
└──────────────────────────────┘   │  - /latest-timestamp         │
                                   │  - /predict                  │
                                   │  - /predict/batch            │
                                   └──────────────┬───────────────┘
                                                  │
                                       Joblib Load│ Feature Construction
                                                  ▼
                                   ┌──────────────────────────────┐
                                   │   XGBoost Champion Model     │
                                   │   (Exp D: 8 Features)        │
                                   │   - Threshold: 0.50          │
                                   │   - Horizon: 30 minutes      │
                                   └──────────────────────────────┘
```

---

## 7. Machine Learning Pipeline

```
[ Raw ACN Session Logs (JSON/CSV) ]
                 │
                 ▼
[ 30-Min Interval Discretization (1,861,310 records across 55 stations) ]
                 │
                 ▼
[ Chronological Partitioning: Train (89.34%) | Val (6.38%) | Test (4.28%) ]
                 │
                 ▼
[ Feature Engineering (Frozen Training Priors: 1,320 rates, 55 durations) ]
                 │
                 ▼
[ Model Training & Ablation (Logistic Regression, Random Forest, XGBoost) ]
                 │
                 ▼
[ Validation-Set Model Selection & Threshold Tuning (tau = 0.50) ]
                 │
                 ▼
[ Test-Set Robustness Evaluation (1,000 Bootstrap Resamples) ]
                 │
                 ▼
[ Artifact Serialization (PKL, features.json, threshold.json) ]
```

---

## 8. Dataset: ACN-Data (Caltech)

The research utilizes empirical data from the **Adaptive Charging Network (ACN-Data)** recorded at the California Institute of Technology in Pasadena, California:

- **Location:** Caltech Campus Charging Plaza, Pasadena, CA, USA
- **Monitored Chargers ($M$):** 55 discrete charging stations
- **Total Validated Sessions:** 7,596 charging sessions
- **Time Span:** October 10, 2019 to September 14, 2021 (UTC)
- **Granularity:** 30-minute regularized temporal intervals
- **Total Dataset Size:** 1,861,310 station-interval records
- **Local Timezone:** `America/Los_Angeles` (Pacific Time)

---

## 9. Chronological Train / Validation / Test Split

To strictly prevent temporal leakage and simulate realistic forward deployment, data was partitioned chronologically:

| Split | UTC Date Range | 30-Min Intervals | Proportion | Positive Prevalence |
| :--- | :--- | :---: | :---: | :---: |
| **Training (Train)** | 2019-10-10 00:00:00 $\to$ 2021-06-30 23:59:59 | 1,662,925 | 89.34% | 3.54% (58,812 / 1,662,925) |
| **Validation (Val)** | 2021-07-01 00:00:00 $\to$ 2021-08-14 23:59:59 | 118,800 | 6.38% | 3.76% (4,467 / 118,800) |
| **Test (Test)** | 2021-08-15 00:00:00 $\to$ 2021-09-14 23:59:59 | 79,585 | 4.28% | 5.61% (4,467 / 79,585) |
| **Total** | **2019-10-10 $\to$ 2021-09-14** | **1,861,310** | **100.00%** | **—** |

---

## 10. The Eight Production Features

The production model uses exactly eight engineered features:

| # | Group | Feature Name | Type | Description | Computation / Source |
| :-: | :--- | :--- | :---: | :--- | :--- |
| 1 | **A. Temporal** | `local_hour` | Int | Local hour of day (0–23) | Hour in `America/Los_Angeles` |
| 2 | **A. Temporal** | `local_day_of_week` | Int | Day of week (0=Mon, 6=Sun) | Day of week in `America/Los_Angeles` |
| 3 | **A. Temporal** | `is_weekend` | Binary | Weekend flag (0 or 1) | 1 if day $\in \{5, 6\}$, else 0 |
| 4 | **A. Temporal** | `month` | Int | Calendar month (1–12) | Month in `America/Los_Angeles` |
| 5 | **B. Historical Lag** | `previous_occupancy` | Binary | Occupancy at $T-30\text{ min}$ | $O(s_i, T - 30\text{m})$ |
| 6 | **B. Historical Lag** | `rolling_2hr_occupancy` | Float | Mean occupancy past 2 hours | $\frac{1}{4}\sum_{k=1}^4 O(s_i, T - 30k\text{m})$ |
| 7 | **C. Station Operational** | `station_hour_occupancy_rate` | Float | Historical occupancy for station $\times$ hour | Train split prior ($55 \times 24 = 1,320$ rows) |
| 8 | **D. Session Duration** | `station_avg_session_duration` | Float | Mean session length in minutes | Train split prior (55 stations) |

### Inference Fallback Policy
For queries where a station or station-hour combination is not found in the training priors:
- **Global Hour Occupancy Rate Fallback:** `0.091185`
- **Global Avg Session Duration Fallback:** `164.55 minutes`

---

## 11. Feature Ablation Study (Experiments A–D)

Four progressive feature configurations were evaluated across all model families:

- **Experiment A (Temporal):** Features 1–4 (`local_hour`, `local_day_of_week`, `is_weekend`, `month`).
- **Experiment B (Temporal + Historical Lag):** Features 1–6 (+ `previous_occupancy`, `rolling_2hr_occupancy`).
- **Experiment C (Temporal + Lag + Station Operational):** Features 1–7 (+ `station_hour_occupancy_rate`).
- **Experiment D (Full Features):** Features 1–8 (+ `station_avg_session_duration`).

---

## 12. Model Comparison: Logistic Regression vs. Random Forest vs. XGBoost

### Validation Partition Results (Model Selection)

| Experiment | Model Family | F1-Score | PR-AUC | Precision | Recall | Balanced Acc. | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exp A** | Logistic Regression | 0.1252 | 0.0478 | 0.0678 | 0.8145 | 0.6739 | 0.6114 |
| **Exp A** | Random Forest | 0.0000 | 0.0643 | 0.0000 | 0.0000 | 0.5000 | 0.6412 |
| **Exp A** | XGBoost | 0.0000 | 0.0644 | 0.0000 | 0.0000 | 0.5000 | 0.6132 |
| **Exp B** | Logistic Regression | 0.7462 | 0.5282 | 0.7459 | 0.7465 | 0.8680 | 0.8860 |
| **Exp B** | Random Forest | 0.7462 | 0.6838 | 0.7459 | 0.7465 | 0.8680 | 0.9256 |
| **Exp B** | XGBoost | 0.7462 | 0.6845 | 0.7459 | 0.7465 | 0.8680 | 0.9174 |
| **Exp C** | Logistic Regression | 0.6315 | 0.6927 | 0.5220 | 0.7991 | 0.8843 | 0.9495 |
| **Exp C** | Random Forest | 0.7459 | 0.7172 | 0.7450 | 0.7467 | 0.8680 | 0.9683 |
| **Exp C** | XGBoost | 0.7399 | 0.7102 | 0.7445 | 0.7354 | 0.8624 | 0.9593 |
| **Exp D** | Logistic Regression | 0.6410 | 0.6943 | 0.5333 | 0.8033 | 0.8870 | 0.9557 |
| **Exp D** | Random Forest | 0.7462 | 0.7289 | 0.7450 | 0.7474 | 0.8684 | 0.9725 |
| **Exp D** | **XGBoost (Champion)** | **0.7446** | **0.7279** | **0.7488** | **0.7404** | **0.8650** | **0.9646** |

---

## 13. Champion Model: XGBoost Experiment D

### Hyperparameters
```json
{
  "n_estimators": 150,
  "max_depth": 6,
  "learning_rate": 0.05,
  "subsample": 0.8,
  "colsample_bytree": 0.8,
  "scale_pos_weight": 27.275266952322657,
  "eval_metric": "logloss",
  "random_state": 42,
  "n_jobs": -1
}
```

### Feature Importance (Gain-Based)

| Feature Name | Gain Importance | Relative Contribution |
| :--- | :---: | :---: |
| `previous_occupancy` | 0.888103 | **88.81%** |
| `rolling_2hr_occupancy` | 0.069313 | **6.93%** |
| `station_hour_occupancy_rate` | 0.020045 | **2.00%** |
| `local_hour` | 0.006112 | **0.61%** |
| `month` | 0.005662 | **0.57%** |
| `is_weekend` | 0.003915 | **0.39%** |
| `local_day_of_week` | 0.003811 | **0.38%** |
| `station_avg_session_duration` | 0.003039 | **0.30%** |

---

## 14. Authoritative Performance Metrics

### Final Validation & Test Metrics (Frozen Values)

| Metric | Validation Partition ($N=118,800$) | Test Partition ($N=79,585$) |
| :--- | :---: | :---: |
| **PR-AUC** | **0.7279** | **0.7997** |
| **F1-Score** | **0.7446** | **0.7665** |
| **Precision** | **0.7488** | **0.7677** |
| **Recall** | **0.7404** | **0.7652** |
| **ROC-AUC** | **0.9646** | **0.9775** |
| **Balanced Accuracy** | **0.8650** | **0.8757** |
| **Accuracy** | **0.9797** | **0.9738** |
| **Brier Score** | — | **0.0238** |

### Test Set Confusion Matrix ($N = 79,585$)

| | Predicted Available ($\hat{Y} = 0$) | Predicted Occupied ($\hat{Y} = 1$) | Total |
| :--- | :---: | :---: | :---: |
| **Actual Available ($Y = 0$)** | **TN = 74,084** | **FP = 1,034** | 75,118 |
| **Actual Occupied ($Y = 1$)** | **FN = 1,049** | **TP = 3,418** | 4,467 |
| **Total** | 75,133 | 4,452 | 79,585 |

- **True Positive Rate (Recall):** $3,418 / 4,467 = 76.52\%$
- **False Positive Rate:** $1,034 / 75,118 = 1.38\%$
- **Precision:** $3,418 / 4,452 = 76.77\%$

---

## 15. Persistence Baseline Comparison

| Model | Test PR-AUC | Test F1-Score | Test Precision | Test Recall | Test Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Always-Zero Baseline** | 0.5281 | 0.0000 | — | 0.0000 | 0.9439 |
| **Persistence Baseline** | 0.7722 | 0.7656 | 0.7652 | 0.7661 | 0.9737 |
| **XGBoost Exp D (Champion)** | **0.7997** | **0.7665** | **0.7677** | **0.7652** | **0.9738** |
| **$\Delta$ (XGBoost vs Persistence)** | **+0.0275** | **+0.0008** | **+0.0025** | **-0.0009** | **+0.0001** |

---

## 16. Bootstrap Robustness Analysis

Evaluated using **1,000 paired non-parametric bootstrap iterations** on the held-out test split:

| Metric | Point Estimate | 95% Bootstrap Confidence Interval |
| :--- | :---: | :---: |
| **PR-AUC** | 0.7997 | `[0.7872, 0.8120]` |
| **F1-Score** | 0.7665 | `[0.7570, 0.7759]` |
| **Precision** | 0.7677 | `[0.7563, 0.7801]` |
| **Recall** | 0.7652 | `[0.7524, 0.7774]` |
| **$\Delta$PR-AUC (vs Persistence)** | **+0.0275** | **`[+0.0191, +0.0358]`** (Statistically Significant) |
| **$\Delta$F1 (vs Persistence)** | +0.0008 | `[-0.0000, +0.0017]` (Not Significant) |

---

## 17. Probability Calibration (Brier Score)

$$\text{Brier Score} = \frac{1}{N}\sum_{i=1}^N (\hat{p}_i - y_i)^2$$

| Model | Test Brier Score | Calibration Assessment |
| :--- | :---: | :--- |
| **XGBoost Exp D** | **0.0238** | Lower mean squared probability error; calibrated risk estimates |
| **Persistence Baseline** | 0.0263 | Uncalibrated binary step function ($0.0$ or $1.0$) |

---

## 18. FastAPI Microservice Architecture

- **Path:** `api/main.py`
- **Port:** `8000`
- **Features:**
  - Singleton memory load of the 1,861,585-record occupancy dataset and training priors ($1,320$ rates, $55$ session stats).
  - High-performance vectorized batch inference with NumPy matrices.
  - Sub-millisecond evaluation per prediction item.
  - Structured Pydantic request/response schemas with input validation.

---

## 19. Node.js / Express Backend Architecture

- **Path:** `backend/server.js`
- **Port:** `5000`
- **Features:**
  - Express.js REST API with CORS middleware and JSON parsing.
  - JWT-based authentication guards on `/api/favorites` and `/api/sessions`.
  - Resilience features: 5-second `AbortSignal.timeout` on external FastAPI requests.
  - Station aggregation and multi-factor ranking controller.

---

## 20. MongoDB Atlas Database Integration

- **ODM:** Mongoose 9.9+
- **Collections:**
  - `Station`: Station identifier (`stationId`), name, site, connector type, total connectors, status.
  - `User`: Name, email, hashed password (`bcryptjs`), favorite station IDs array (`favoriteStations`).
  - `ChargingSession`: User reference (`userId`), station ID, start time, end time, energy consumed, status (`scheduled`, `completed`, `cancelled`).

---

## 21. React Frontend Application

- **Framework:** React 18 + Vite + Tailwind CSS
- **Port:** `5173`
- **Core Views:**
  - **Dashboard (`/`):** Station overview, dynamic recommendation cards, filterable station grid.
  - **Station Details (`/stations/:id`):** Deep inspection of station forecast, occupancy history, and specs.
  - **Favorites (`/favorites`):** Bookmarked chargers with real-time status indicators.
  - **Sessions (`/sessions`):** Scheduled slot booking and session history manager.
  - **Map View (`/map`):** Interactive visual station layout.
  - **Auth (`/login`, `/register`):** User onboarding and session token persistence.

---

## 22. Recommendation Ranking Algorithm

To rank charging stations for incoming drivers, the Node.js backend combines availability probability, discrete status, and occupancy risk into a composite **Recommendation Score** ($0 \dots 100$):

$$S_{\text{availability}} = P(\text{available}) \times 100$$
$$S_{\text{status}} = \begin{cases} 100 & \text{if status} = \text{"available"} \\ 0 & \text{if status} = \text{"occupied"} \end{cases}$$
$$S_{\text{prediction}} = (1 - P(\text{occupied})) \times 100$$

$$S_{\text{recommendation}} = 0.60 \times S_{\text{availability}} + 0.25 \times S_{\text{status}} + 0.15 \times S_{\text{prediction}}$$

Stations are sorted descending by $S_{\text{recommendation}}$ (with `stationId` as the tie-breaker), assigning sequential `recommendationRank` values ($1 \dots 55$).

---

## 23. API Endpoints Reference

### FastAPI Microservice (`http://127.0.0.1:8000`)

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :---: |
| `GET` | `/` | Service root and model configuration | Public |
| `GET` | `/health` | Health check & model status | Public |
| `GET` | `/latest-timestamp` | Returns the latest available timestamp in dataset | Public |
| `POST` | `/predict` | Single-station 30-min occupancy prediction | Public |
| `POST` | `/predict/batch` | Multi-station batch 30-min occupancy prediction | Public |

### Express Backend API (`http://localhost:5000`)

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register` | User account registration | Public |
| `POST` | `/api/auth/login` | User authentication & JWT issuance | Public |
| `GET` | `/api/stations` | List all 55 station metadata records | Public |
| `GET` | `/api/stations/predictions` | Batch predictions with recommendation ranking | Public |
| `GET` | `/api/stations/:id/prediction`| Single station prediction and details | Public |
| `GET` | `/api/favorites` | Retrieve user favorite stations | JWT |
| `POST` | `/api/favorites/:id` | Add station to user favorites | JWT |
| `DELETE`| `/api/favorites/:id` | Remove station from user favorites | JWT |
| `POST` | `/api/sessions` | Schedule a charging session | JWT |
| `GET` | `/api/sessions` | Retrieve user charging sessions | JWT |
| `GET` | `/api/sessions/:id` | Get specific charging session | JWT |
| `PATCH`| `/api/sessions/:id` | Update / cancel charging session | JWT |

---

## 24. Environment Variables

Create `.env` in the `backend/` directory:

```env
PORT=5000
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.sjyoik7.mongodb.net/ev-charging-db
ML_API_URL=http://127.0.0.1:8000
JWT_SECRET=your_secure_jwt_secret_key_here
```

---

## 25. Installation Instructions

### Prerequisites
- **Python:** 3.10 or 3.11 (with virtual environment support)
- **Node.js:** v18.0.0 or higher (v20+ recommended)
- **MongoDB:** MongoDB Atlas connection string or local MongoDB instance

### 1. Clone Repository & Setup Python Environment
```bash
git clone https://github.com/your-username/ev-charging-prediction.git
cd ev-charging-prediction

# Create and activate Python virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Install Python ML & API dependencies
pip install -r requirements.txt
```

### 2. Setup Node.js Backend
```bash
cd backend
npm install
# Configure backend/.env with your MONGO_URI and JWT_SECRET
```

### 3. Setup React Frontend
```bash
cd ../frontend
npm install
```

---

## 26. How to Run FastAPI ML Service

From the project root (with `venv` activated):

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

---

## 27. How to Run Node.js Backend

From the `backend/` directory:

```bash
cd backend
npm start
# Or for development with automatic restart:
# npm run dev
```

- Backend Server: `http://localhost:5000`

---

## 28. How to Run React Frontend

From the `frontend/` directory:

```bash
cd frontend
npm run dev
```

- Web Interface: `http://localhost:5173`

---

## 29. Example Prediction Request & Response

### FastAPI Single Prediction (`POST /predict`)

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": "2-39-123-23",
    "timestamp": "2021-09-14T03:30:00Z"
  }'
```

**Response:**
```json
{
  "station_id": "2-39-123-23",
  "prediction": 0,
  "status": "available",
  "occupancy_probability": 0.0059,
  "availability_probability": 0.9941,
  "prediction_horizon_minutes": 30,
  "occupancy_history": [0, 0, 0, 0],
  "features_used": {
    "local_hour": 20,
    "local_day_of_week": 0,
    "is_weekend": 0,
    "month": 9,
    "previous_occupancy": 0,
    "rolling_2hr_occupancy": 0.0,
    "station_hour_occupancy_rate": 0.013492,
    "station_avg_session_duration": 286.28882
  }
}
```

---

## 30. Project Directory Structure

```
ev-charging-prediction/
├── .gitignore                      # Git ignore configurations
├── README.md                       # Comprehensive project documentation
├── requirements.txt                # Python dependencies
├── final_minor_project_report.md   # Comprehensive academic project report
├── research_paper_final.md         # Final IEEE-style research manuscript
├── api/                            # FastAPI microservice
│   ├── feature_engineering.py     # 8-feature extraction logic & lookups
│   ├── main.py                     # FastAPI application & endpoints
│   └── occupancy_service.py        # Shared dataset loading & caching
├── backend/                        # Node.js Express backend
│   ├── .env                        # Environment variables
│   ├── package.json                # Node dependencies & scripts
│   ├── server.js                   # Express server entry point
│   ├── config/                     # Database configuration (db.js)
│   ├── controllers/                # Auth, Station, Prediction, Session, Favorite
│   ├── middleware/                 # JWT auth middleware
│   ├── models/                     # Mongoose Schemas (User, Station, Session)
│   ├── routes/                     # Express REST route definitions
│   └── services/                   # ML microservice bridge (mlService.js)
├── data/                           # Data storage
│   ├── raw/                        # Original ACN-Data JSON logs
│   └── processed/                  # Discretized grids & lookup tables
│       ├── station_occupancy_30min.csv
│       ├── station_hour_rates_train.csv
│       └── station_session_stats_train.csv
├── frontend/                       # React client application
│   ├── package.json                # Frontend dependencies
│   ├── vite.config.js              # Vite configuration
│   ├── src/
│   │   ├── App.jsx                 # App routing & layout
│   │   ├── main.jsx                # React root entry
│   │   ├── components/             # UI components (Navbar, Cards, Badges)
│   │   ├── pages/                  # Dashboard, StationDetails, Favorites, Sessions
│   │   └── services/               # API clients (stationApi, authApi, sessionApi)
├── models/                         # Serialized ML artifacts
│   ├── final/                      # Production champion artifacts
│   │   ├── ev_occupancy_xgboost.pkl
│   │   ├── features.json
│   │   ├── metadata.json
│   │   └── threshold.json
│   └── research/                   # Experimental ablation models (A-D)
└── src/                            # Research & offline training pipelines
    ├── features/                   # build_features.py
    └── models/                     # train_models.py, train_baselines.py
```

---

## 31. Limitations

1. **Single-Facility Scope:** Empirical validation is based on the Caltech campus charging network and reflects academic/workplace charging dynamics.
2. **Absence of Exogenous Feeds:** Real-time weather data, local traffic congestion, and dynamic electricity tariff rates were not incorporated.
3. **Fixed 30-Minute Horizon:** The model operates at a single discrete forward lead time ($T + 30\text{ min}$).
4. **Geographic Coordinates:** Physical distances and routing constraints are not part of the validated ML model features.

---

## 32. Future Scope

1. **Multi-Horizon Joint Forecasting:** Extending the architecture to predict $T+15\text{m}$, $T+30\text{m}$, $T+60\text{m}$, and $T+120\text{m}$ simultaneously.
2. **Real-Time OCPP Telemetry:** Integrating Open Charge Point Protocol (OCPP 1.6/2.0.1) live streams for sub-minute state updates.
3. **Energy Demand & Queue Estimation:** Predicting instantaneous power draw (kW) alongside binary occupancy.
4. **Localization & Transfer Learning:** Adapting the model pipeline to diverse commercial, fleet, and highway networks.

---

## 33. Academic & Research Documentation

For detailed mathematical formulations, statistical proofs, and extended literature context:
- **Full Academic Research Paper:** [`research_paper_final.md`](./research_paper_final.md)
- **Comprehensive Minor Project Report:** [`final_minor_project_report.md`](./final_minor_project_report.md)
- **Model Metadata & Manifest:** [`models/final/metadata.json`](./models/final/metadata.json)

---

## 34. Validated Model vs. Future Indian EV Extensions

| Dimension | Validated Research Model (Current) | Future Extension: Indian EV Infrastructure |
| :--- | :--- | :--- |
| **Dataset Source** | Caltech Adaptive Charging Network (ACN-Data) | Indian CPO Telemetry (e.g., BESCOM, Tata Power, Statiq) |
| **Geographic Scope** | Pasadena, California, USA | Urban centers (Bengaluru, Delhi-NCR, Mumbai) |
| **Infrastructure Type**| Workplace / Academic Campus AC Level 2 | Mixed Public DC Fast Charging (CCS2/GB/T) & AC (Type 2) |
| **Vehicle Types** | 4-Wheeler Passenger BEVs / PHEVs | High 2W/3W Fleet Utilization + Commercial 4W Taxis |
| **Validation Status** | **Empirically Validated & Frozen** (Test PR-AUC: 0.7997) | **Future Exploratory Scope** (Requires Indian datasets) |

---

## 35. License & Citation

This project is licensed under the MIT License.

```bibtex
@misc{evconnect2026,
  title={Machine Learning-Based Prediction of EV Charging Station Occupancy Using ACN-Data},
  author={EVConnect Minor Project Team},
  year={2026},
  howpublished={Minor Project Repository, Academic Research Prototype}
}
```
