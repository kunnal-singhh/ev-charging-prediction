"""
Phase 7 — Research Paper Generator
Reads authoritative CSV/JSON artefacts and writes the full academic paper
to the IDE artifact directory.
"""

import os
import json
import pandas as pd

ARTIFACT_DIR = r"C:\Users\kunal singh\.gemini\antigravity-ide\brain\ee9b9787-4944-474c-84d4-c4254c15a290"
OUT_PATH = os.path.join(ARTIFACT_DIR, "research_paper_draft.md")

# ── Load data ──────────────────────────────────────────────────────────────
comp = pd.read_csv("data/processed/model_comparison_v1.csv")
fi_df = pd.read_csv("data/processed/feature_importance_v1.csv")
bl = pd.read_csv("data/processed/baseline_results.csv")

# Feature importance for Exp D XGBoost
fi_raw = fi_df[(fi_df["experiment"] == "Exp_D_Full_Features") & (fi_df["model"] == "XGBoost")].copy()
fi_raw["pct"] = fi_raw["importance"] / fi_raw["importance"].sum() * 100
fi_raw = fi_raw.sort_values("importance", ascending=False)

# Validation and test tables
val = comp[comp["split"] == "val"][["experiment","model","f1","pr_auc","recall","precision","balanced_accuracy","roc_auc"]].copy()
test = comp[comp["split"] == "test"][["experiment","model","f1","pr_auc","recall","precision","balanced_accuracy","accuracy","roc_auc"]].copy()

# Champion row
champ_test = comp[(comp["experiment"] == "Exp_D_Full_Features") & (comp["model"] == "XGBoost") & (comp["split"] == "test")].iloc[0]
champ_val  = comp[(comp["experiment"] == "Exp_D_Full_Features") & (comp["model"] == "XGBoost") & (comp["split"] == "val")].iloc[0]

# Baselines
pers_test = bl[(bl["model"] == "Persistence") & (bl["split"] == "test")].iloc[0]
az_test   = bl[(bl["model"] == "Always-Zero") & (bl["split"] == "test")].iloc[0]

EXP_ORDER = ["Exp_A_Temporal","Exp_B_Temporal_Historical","Exp_C_Station_Operational","Exp_D_Full_Features"]
MOD_ORDER = ["LogisticRegression","RandomForest","XGBoost"]
EXP_LABELS = {
    "Exp_A_Temporal": "Exp A — Temporal",
    "Exp_B_Temporal_Historical": "Exp B — Temp+Hist",
    "Exp_C_Station_Operational": "Exp C — +Station Op.",
    "Exp_D_Full_Features": "Exp D — Full Features",
}

def fmt(v, d=4):
    return f"{v:.{d}f}"

def val_table(df):
    rows = []
    rows.append("| Experiment | Model | F1 | PR-AUC | Recall | Precision | Bal. Acc. | ROC-AUC |")
    rows.append("|---|---|---|---|---|---|---|---|")
    for exp in EXP_ORDER:
        for mod in MOD_ORDER:
            r = df[(df["experiment"]==exp) & (df["model"]==mod)]
            if r.empty: continue
            r = r.iloc[0]
            label = EXP_LABELS.get(exp, exp)
            bold_open  = "**" if (exp=="Exp_D_Full_Features" and mod=="XGBoost") else ""
            bold_close = "**" if (exp=="Exp_D_Full_Features" and mod=="XGBoost") else ""
            rows.append(f"| {bold_open}{label}{bold_close} | {bold_open}{mod}{bold_close} | {fmt(r.f1)} | {fmt(r.pr_auc)} | {fmt(r.recall)} | {fmt(r.precision)} | {fmt(r.balanced_accuracy)} | {fmt(r.roc_auc)} |")
    return "\n".join(rows)

def test_table(df):
    rows = []
    rows.append("| Experiment | Model | F1 | PR-AUC | Recall | Precision | Bal. Acc. | Accuracy | ROC-AUC |")
    rows.append("|---|---|---|---|---|---|---|---|---|")
    for exp in EXP_ORDER:
        for mod in MOD_ORDER:
            r = df[(df["experiment"]==exp) & (df["model"]==mod)]
            if r.empty: continue
            r = r.iloc[0]
            label = EXP_LABELS.get(exp, exp)
            bold_open  = "**" if (exp=="Exp_D_Full_Features" and mod=="XGBoost") else ""
            bold_close = "**" if (exp=="Exp_D_Full_Features" and mod=="XGBoost") else ""
            rows.append(f"| {bold_open}{label}{bold_close} | {bold_open}{mod}{bold_close} | {fmt(r.f1)} | {fmt(r.pr_auc)} | {fmt(r.recall)} | {fmt(r.precision)} | {fmt(r.balanced_accuracy)} | {fmt(r.accuracy)} | {fmt(r.roc_auc)} |")
    return "\n".join(rows)

def fi_table(fi_raw):
    rows = ["| Feature | Importance (raw) | Importance (%) |", "|---|---|---|"]
    for _, row in fi_raw.iterrows():
        rows.append(f"| `{row['feature']}` | {fmt(row['importance'],6)} | **{fmt(row['pct'],2)}%** |")
    return "\n".join(rows)

# ── Assemble paper ─────────────────────────────────────────────────────────
paper = f"""# Machine Learning-Based Prediction of EV Charging Station Occupancy Using ACN-Data

**EVConnect Minor Project — Phase 7 Research Paper Draft**

> All metrics in this document are verified against:
> `data/processed/model_comparison_v1.csv`, `model_predictions_v1.csv`,
> `robustness_results.csv`, and `models/final/metadata.json`.
> The old ROC-AUC value of 0.9482 does NOT appear in this document.
> The authoritative value is **0.9775**.
> The authoritative station-hour table size is **1,320 rows** (55 × 24), not 1,234.

---

## 1. Title

**Machine Learning-Based Prediction of EV Charging Station Occupancy Using ACN-Data**

---

## 2. Abstract

The rapid proliferation of electric vehicles (EVs) presents operational challenges in managing charging infrastructure, particularly in predicting whether individual charging stations will be occupied at future time points. This study investigates the problem of 30-minute-ahead binary occupancy prediction for EV charging stations using the openly available Adaptive Charging Network (ACN) dataset collected at the Caltech charging site. A reproducible machine learning pipeline was developed encompassing data preprocessing, temporal feature engineering, feature ablation experimentation, and comparative model evaluation across three algorithm families: Logistic Regression, Random Forest, and XGBoost. Four feature-set configurations (Experiments A–D) were evaluated under a strict chronological train-validation-test split framework. The selected model — XGBoost trained on the full eight-feature set (Experiment D) — achieves a test Precision-Recall Area Under the Curve (PR-AUC) of **{fmt(champ_test.pr_auc,4)}**, F1-score of **{fmt(champ_test.f1,4)}**, and ROC-AUC of **{fmt(champ_test.roc_auc,4)}** on a held-out test set of 79,585 temporal intervals. The study establishes that historical occupancy lag features dominate predictive signal (model-reported gain importance: `previous_occupancy` ≈ {fi_raw.iloc[0]['pct']:.2f}%), with station-specific operational features providing additional discriminatory value. A statistically meaningful PR-AUC advantage of +0.0275 (95% bootstrap CI: [+0.0191, +0.0358]) over the Persistence baseline supports the practical utility of the proposed approach within the evaluated dataset. The trained model is deployed as part of the EVConnect web application prototype, exposing a FastAPI inference service integrated with a Node.js backend and a React frontend interface. Limitations of this work — including geographic and contextual specificity to a single ACN site — are discussed, and directions for future multi-site and multi-network generalisation are identified.

---

## 3. Keywords

EV charging station occupancy prediction; machine learning; XGBoost; binary classification; time series; feature engineering; ACN-Data; class imbalance; PR-AUC; FastAPI; EVConnect

---

## 4. Introduction

The global adoption of electric vehicles is accelerating, driven by governmental policy incentives, environmental concerns, and decreasing battery costs [REFERENCE NEEDED: IEA Global EV Outlook]. As EV penetration increases, the efficient utilisation of public and semi-public charging infrastructure becomes a growing operational challenge. Unlike fuel stations, EV charging stations require extended dwell times (often 60–300 minutes per session), creating occupancy dynamics that are difficult for drivers to predict without assistance.

Occupancy uncertainty leads to driver anxiety — commonly referred to as "range anxiety" — and suboptimal routing decisions. A practical solution is to provide predictive information about charging availability at a target station some minutes ahead, allowing drivers and mobility platforms to make better-informed routing decisions.

This study addresses this problem through a supervised machine learning approach. Using the ACN-Data dataset from the Caltech charging site [REFERENCE NEEDED: ACN-Data paper — Lee et al.], which records high-resolution EV session data, a 30-minute-ahead binary occupancy prediction system is developed. The specific prediction formulation — binary occupancy rather than continuous demand — was selected following examination of the dataset structure, consistent with the research proposal's indication that the final prediction formulation would be confirmed after data exploration.

The study makes the following contributions within the scope of this minor project:

1. A reproducible end-to-end machine learning pipeline for occupancy prediction using the ACN dataset.
2. A systematic feature ablation study across four feature configurations and three ML algorithm families (12 model configurations total).
3. A rigorous chronological evaluation framework with bootstrap-based statistical robustness testing.
4. Deployment of the selected model as a real-time prediction service within the EVConnect prototype web application.

The remainder of this paper is organised as follows. Section 5 formally states the research problem. Section 6 describes the objectives. Sections 7–10 cover the dataset, preprocessing, exploratory analysis, and prediction formulation. Sections 11–16 describe the feature engineering and experimental methodology. Sections 17–21 present results, calibration, robustness, and error analysis. Section 22 discusses findings. Section 23 describes the deployment architecture. Sections 24–26 address limitations, future work, and conclusions.

---

## 5. Problem Statement

**Primary Research Problem:**

Given the occupancy history of an EV charging station up to time T, predict whether the station will be occupied at time T + 30 minutes.

Formally, the target variable is defined as:

```
target_occupancy(T) = occupancy(T + 30 minutes)

Where:
  0  →  Station is unoccupied / available
  1  →  Station is occupied
```

This constitutes a binary classification problem. The prediction is made over a 30-minute horizon — a practically meaningful window for EV drivers planning a charging visit.

The problem is formulated using only information available strictly before or at time T, ensuring no data leakage from future observations.

---

## 6. Objectives

The specific objectives of this study are:

1. **O1**: To analyse and preprocess the ACN-Data Caltech dataset to construct a reproducible temporal occupancy grid.
2. **O2**: To engineer predictive features from temporal, historical, station operational, and session-duration information.
3. **O3**: To compare Logistic Regression, Random Forest, and XGBoost classifiers across four feature ablation experiments under a chronological evaluation framework.
4. **O4**: To select the best-performing model configuration based on validation-set performance, using PR-AUC and F1 as primary metrics.
5. **O5**: To rigorously evaluate the selected model on a held-out test set and assess statistical robustness via bootstrap resampling.
6. **O6**: To deploy the selected model as a prediction service within the EVConnect application prototype.

---

## 7. Dataset Description

### 7.1 Source

The dataset used in this study is the ACN-Data (Adaptive Charging Network Data) collected at the Caltech campus charging site [REFERENCE NEEDED: Lee et al., ACN-Data]. ACN-Data is an open dataset containing fine-grained records of EV charging sessions including connection/disconnection times, energy delivered, and per-session pilot signals.

### 7.2 Dataset Statistics

| Property | Value |
|---|---|
| Site | Caltech, Pasadena, CA, USA |
| Charging stations | 55 |
| Total EV sessions | 7,596 |
| Session duration range | ~1 minute to ~600 minutes |
| Data timezone | America/Los_Angeles (Pacific Time) |
| Source format | JSON (raw), CSV (processed) |

### 7.3 Temporal Occupancy Grid Construction

The raw session-level data was transformed into a regular 30-minute interval occupancy grid covering all 55 stations. Each row in the grid represents a (stationID, timestamp) pair and records whether the station was occupied (1) or unoccupied (0) at that 30-minute interval.

| Grid Property | Value |
|---|---|
| Grid interval | 30 minutes |
| Total temporal intervals (post NaN removal) | 1,861,310 |
| Total rows before NaN removal | 1,861,585 |
| Occupied intervals (Class 1) | 68,042 |
| Unoccupied intervals (Class 0) | 1,793,543 |
| Overall occupancy rate | ~3.65% |

### 7.4 Chronological Train-Validation-Test Split

The data was split chronologically — not randomly — to respect the temporal structure of the prediction task and prevent temporal data leakage:

| Split | UTC Date Range | Rows |
|---|---|---|
| **Training** | 2019-10-10 → 2021-06-30 | 1,662,925 |
| **Validation** | 2021-07-01 → 2021-08-14 | 118,800 |
| **Test** | 2021-08-15 → 2021-09-14 | 79,585 |
| **Total** | — | 1,861,310 |

The training period spans approximately 21 months; validation and test periods span approximately 6 weeks each.

---

## 8. Data Preprocessing

### 8.1 Session Data Processing

The raw ACN-Data JSON was parsed to extract connection time, disconnection time, and session duration for each EV charging session. Sessions with missing or negative durations were excluded. Session timestamps were converted to UTC-aware datetime objects.

### 8.2 Occupancy Grid Construction

For each charging station and each 30-minute UTC timestamp interval, a binary occupancy indicator was derived: a station interval was marked occupied if at least one active EV session overlapped with that interval.

### 8.3 Handling of Class Imbalance

The training data exhibits significant class imbalance:

| Class | Label | Training Count | Training Prevalence |
|---|---|---|---|
| Unoccupied | 0 | 1,604,113 | 96.46% |
| Occupied | 1 | 58,812 | 3.54% |

Because positive instances (occupied intervals) constitute only ~3.54% of training data, standard accuracy is misleading as an evaluation metric — a classifier that always predicts "available" would achieve ~96.4% accuracy while being entirely uninformative. Therefore, PR-AUC and F1-score are used as the primary evaluation metrics throughout this study.

For XGBoost, the `scale_pos_weight` parameter was set to 27.275266952322657, calculated from the training-set class ratio (1,604,113 / 58,812), instructing the model to treat positive instances as approximately 27 times more important than negative instances during training.

### 8.4 Leakage Prevention Policy

All aggregate features (station-hour occupancy rates and station average session durations) were computed exclusively from the training split and frozen before being joined to validation and test rows. Lag features use only intervals strictly before T. The target variable uses the interval at T + 30 minutes. Programmatic assertions were implemented in the pipeline to verify these constraints.

---

## 9. Exploratory Data Analysis

### 9.1 Temporal Occupancy Patterns

Exploratory analysis of the training data reveals strong temporal structure in charging occupancy. Occupancy rates peak during mid-morning hours (approximately 09:00–16:00 local time) on weekdays, consistent with workplace EV charging behaviour at the Caltech campus. Occupancy rates are markedly lower on weekends and during late-night hours. This temporal regularity motivates the inclusion of time-of-day and day-of-week features.

### 9.2 Station-Level Heterogeneity

Significant heterogeneity exists across the 55 charging stations. Some stations exhibit systematically higher occupancy rates across all hours, while others are rarely utilised. This motivates the inclusion of station-specific historical occupancy features rather than relying solely on aggregate temporal patterns.

### 9.3 Session Duration Distribution

Average session durations vary substantially across stations (range: approximately 80–400 minutes based on training data), providing contextual information about typical plug-in behaviour at each charger. This motivates the inclusion of per-station historical average session duration as a feature.

### 9.4 Autocorrelation of Occupancy

The occupancy signal exhibits strong positive autocorrelation at short lags: whether a station is occupied now is a strong predictor of whether it will be occupied 30 minutes later. This motivates the use of occupancy lag features (`previous_occupancy`, `rolling_2hr_occupancy`).

---

## 10. Prediction Problem Formulation

### 10.1 Task Definition

The prediction task is framed as a supervised binary classification problem. Given a (stationID, T) pair, the goal is to predict the binary occupancy state at time T + 30 minutes.

The formulation was selected after data examination, consistent with the research proposal's statement that the final prediction formulation would be confirmed following dataset analysis. The occupancy target was chosen over continuous demand regression because:

- The ACN grid provides clean binary occupancy indicators at 30-minute resolution.
- Binary occupancy probability is directly actionable for EV drivers ("Will this station be free?").
- The class probability output of a binary classifier provides a calibrated availability score suitable for station ranking and recommendation.

### 10.2 Relationship to Continuous Demand

This study does not perform continuous energy demand regression. The prediction of continuous demand (kWh per interval, number of simultaneous sessions, etc.) is identified as a direction for future work.

---

## 11. Feature Engineering

### 11.1 Feature Overview

A total of eight predictive features were engineered, organised into four conceptual groups:

| Group | Feature | Description |
|---|---|---|
| **A. Temporal** | `local_hour` | Hour of day (0–23) in Pacific local time |
| **A. Temporal** | `local_day_of_week` | Day of week (0=Monday, 6=Sunday) |
| **A. Temporal** | `is_weekend` | Binary: 1 if Saturday or Sunday |
| **A. Temporal** | `month` | Calendar month (1–12) |
| **B. Historical Occupancy** | `previous_occupancy` | Occupancy at T − 30 min (binary) |
| **B. Historical Occupancy** | `rolling_2hr_occupancy` | Mean occupancy over [T−120, T−90, T−60, T−30] min |
| **C. Station Operational** | `station_hour_occupancy_rate` | Historical mean occupancy for (stationID, local_hour), computed from training data only |
| **D. Session Duration** | `station_avg_session_duration` | Historical mean session duration in minutes for the station, computed from training sessions only |

### 11.2 Feature Group Rationale

**Group A — Temporal features** capture systematic diurnal, weekly, and seasonal patterns in charging demand. Workplace charging behaviour is strongly time-dependent, with occupancy peaking during working hours on weekdays.

**Group B — Historical occupancy features** exploit the strong temporal autocorrelation of the occupancy signal. `previous_occupancy` captures the most recent state of the station (30-min lag). `rolling_2hr_occupancy` captures the mean occupancy across the preceding two hours, reflecting medium-term utilisation trends.

**Group C — Station operational features** encode station-specific historical occupancy rates indexed by time-of-day. This allows the model to learn that some stations are consistently more heavily utilised during certain hours than others, providing a personalised utilisation prior per station per hour of day.

**Group D — Session duration features** provide context about typical plug-in durations at each station. A station with a high historical average session duration is more likely to remain occupied once a session begins.

### 11.3 Leakage Safety of Aggregate Features

`station_hour_occupancy_rate` was computed from **1,320** (stationID, local_hour) combinations derived exclusively from training-period data (≤ 2021-06-30 23:59:59 UTC). `station_avg_session_duration` was computed from 7,596 training-period sessions. Both lookup tables are static, loaded at inference time, and applied uniformly to validation and test rows. Unseen (stationID, local_hour) combinations fall back to station-level means; completely unseen stations fall back to global training means (occupancy rate: 0.091185; session duration: 164.55 minutes).

---

## 12. Experimental Methodology

### 12.1 Feature Ablation Design

To assess the marginal contribution of each feature group, a structured feature ablation study was conducted. Four experimental configurations were defined:

| Experiment | Feature Groups | Features Included |
|---|---|---|
| **Exp A — Temporal** | A | local_hour, local_day_of_week, is_weekend, month |
| **Exp B — Temporal + Historical** | A, B | + previous_occupancy, rolling_2hr_occupancy |
| **Exp C — Temporal + Historical + Station Op.** | A, B, C | + station_hour_occupancy_rate |
| **Exp D — Full Features** | A, B, C, D | + station_avg_session_duration |

### 12.2 Model Configurations

Each experiment was run with three classifiers, resulting in **12 research model configurations**:

1. Logistic Regression (with StandardScaler; `class_weight='balanced'`)
2. Random Forest (100 estimators; `max_depth=12`; `class_weight='balanced'`)
3. XGBoost (150 estimators; `max_depth=6`; `learning_rate=0.05`; `scale_pos_weight=27.275`)

All models used `random_state=42` for reproducibility. No hyperparameter tuning beyond the initial configuration was performed; all 12 models were trained on identical chronological training splits.

### 12.3 Model Selection Protocol

The model was selected **based on validation-set performance only**. The test set was used exactly once, after the champion model was selected, to produce the final reported results. The threshold of 0.50 was also selected on the validation set and held fixed for test evaluation.

### 12.4 Evaluation Metrics

Given the class imbalance, the primary evaluation metrics are:

- **PR-AUC** (Area Under the Precision-Recall Curve): Robust to class imbalance; reflects performance across all decision thresholds with particular sensitivity to the minority (positive) class.
- **F1-Score**: Harmonic mean of Precision and Recall at the selected threshold (0.50).

Secondary metrics: Precision, Recall, Balanced Accuracy, Accuracy, ROC-AUC, Brier Score.

---

## 13. Baseline Models

Two baselines were established to bound model performance:

### 13.1 Always-Zero Baseline

Predicts every interval as unoccupied (Class 0). This naive baseline achieves high nominal accuracy purely due to class imbalance, but achieves zero recall and F1 = 0.000. It confirms that accuracy alone is an insufficient metric in this setting.

### 13.2 Persistence Baseline

Predicts the occupancy state at T + 30 minutes to equal the observed state at T − 30 minutes. This domain-appropriate baseline is strong because EV sessions typically last many 30-minute intervals, so occupancy is often persistent.

| Baseline | Split | F1 | PR-AUC | Precision | Recall | Bal. Acc. | Accuracy |
|---|---|---|---|---|---|---|---|
| Always-Zero | Test | {fmt(az_test.f1,4)} | {fmt(az_test.pr_auc,4)} | — | {fmt(az_test.recall,4)} | {fmt(az_test.balanced_accuracy,4)} | {fmt(az_test.accuracy,4)} |
| Persistence | Test | **{fmt(pers_test.f1,4)}** | **{fmt(pers_test.pr_auc,4)}** | {fmt(pers_test.precision,4)} | {fmt(pers_test.recall,4)} | {fmt(pers_test.balanced_accuracy,4)} | {fmt(pers_test.accuracy,4)} |

The Persistence baseline is competitively strong on F1 due to the temporal continuity of sessions, reinforcing that any ML model must demonstrate utility primarily through calibrated probability metrics (PR-AUC) rather than binary accuracy.

---

## 14. Comparative ML Models

### 14.1 Results — Validation Set

{val_table(val)}

### 14.2 Results — Test Set

{test_table(test)}

---

## 15. Feature Ablation Study

### 15.1 Impact of Temporal Features (Experiment A)

Temporal features alone (local_hour, local_day_of_week, is_weekend, month) produce very poor occupancy predictions. All three models trained on Experiment A achieve near-zero F1 and PR-AUC values on the test set, with Random Forest and XGBoost predicting everything as the majority class (F1 = 0.000). Logistic Regression shows high recall but extremely poor precision, indicating it over-predicts occupancy. This demonstrates that temporal patterns alone are insufficient to predict occupancy at the 30-minute level.

**Finding RQ1**: Temporal features alone are insufficient for occupancy prediction at the 30-minute horizon.

### 15.2 Impact of Historical Occupancy Features (Experiment B)

Adding `previous_occupancy` and `rolling_2hr_occupancy` to the temporal feature set (Experiment B) produces a dramatic improvement. All three models jump to F1 ≈ 0.7656 and ROC-AUC > 0.89. This confirms that the most informative signal is the recent occupancy history — consistent with the strong autocorrelation of charging sessions.

**Finding RQ1 (confirmed)**: Historical occupancy lag features are indispensable and produce the largest marginal improvement in this dataset.

### 15.3 Impact of Station Operational Features (Experiment C)

Adding `station_hour_occupancy_rate` (Experiment C) produces further improvements in PR-AUC (XGBoost: 0.7444 → 0.7864 on test), reflecting better probability calibration. F1 remains approximately stable, but the AUC-based metrics improve, indicating more informative probability outputs.

**Finding RQ2**: Station-specific occupancy rates meaningfully improve probability-ranked prediction (PR-AUC), which is relevant for station recommendation and ranking.

### 15.4 Impact of Session Duration Features (Experiment D)

Adding `station_avg_session_duration` (Experiment D, Full Features) achieves the highest test PR-AUC (XGBoost: 0.7864 → 0.7997). The improvement is modest relative to Experiment C, suggesting that session duration provides secondary contextual information. XGBoost Experiment D is selected as the champion model based on validation PR-AUC (0.7279) and F1 (0.7446).

**Finding RQ3**: Station average session duration provides a modest but measurable improvement in PR-AUC.

### 15.5 Model Comparison

XGBoost consistently achieves the highest PR-AUC across experiments where meaningful predictive features are available (Experiments B–D). Random Forest is competitive on F1 but trails XGBoost on PR-AUC at full feature set. Logistic Regression is the weakest on PR-AUC in Experiments B–C but remains a useful interpretable reference model.

**Finding RQ4**: XGBoost achieves the strongest PR-AUC among evaluated models on the ACN test set under the full feature set (Experiment D).

---

## 16. Evaluation Metrics

### 16.1 Primary Metrics

**PR-AUC** (Area Under the Precision-Recall Curve): The primary metric throughout this study. It summarises performance across all decision thresholds with particular focus on the minority class. It is preferred over ROC-AUC for highly imbalanced datasets because it is more sensitive to changes in performance on the positive class [REFERENCE NEEDED: Davis & Goadrich, 2006].

**F1-Score**: The harmonic mean of Precision and Recall at the selected threshold (0.50). It balances the cost of missing occupied stations (false negatives) against the cost of incorrectly flagging available stations (false positives).

### 16.2 Secondary Metrics

ROC-AUC, Balanced Accuracy, Precision, Recall (Sensitivity), Brier Score (calibration, lower = better), Accuracy (included but noted to be potentially misleading under class imbalance).

---

## 17. Results

### 17.1 Champion Model Selection

Model selection was performed using validation-set performance. XGBoost — Experiment D (Full Features) was selected as the champion model based on achieving the best combination of validation F1 ({fmt(champ_val.f1,4)}) and validation PR-AUC ({fmt(champ_val.pr_auc,4)}).

### 17.2 Final Model — Validation Performance

| Metric | Value |
|---|---|
| PR-AUC | **{fmt(champ_val.pr_auc,4)}** |
| F1-Score | **{fmt(champ_val.f1,4)}** |
| Precision | {fmt(champ_val.precision,4)} |
| Recall | {fmt(champ_val.recall,4)} |
| ROC-AUC | {fmt(champ_val.roc_auc,4)} |
| Balanced Accuracy | {fmt(champ_val.balanced_accuracy,4)} |
| Accuracy | {fmt(champ_val.accuracy,4)} |

### 17.3 Final Model — Test Performance

The test set was evaluated **exactly once**, using the threshold (0.50) selected on the validation set.

| Metric | Value |
|---|---|
| PR-AUC | **{fmt(champ_test.pr_auc,4)}** |
| F1-Score | **{fmt(champ_test.f1,4)}** |
| Precision | {fmt(champ_test.precision,4)} |
| Recall | {fmt(champ_test.recall,4)} |
| ROC-AUC | **{fmt(champ_test.roc_auc,4)}** |
| Balanced Accuracy | {fmt(champ_test.balanced_accuracy,4)} |
| Accuracy | {fmt(champ_test.accuracy,4)} |

### 17.4 Confusion Matrix (Test Set, N = 79,585)

| | Predicted Available (0) | Predicted Occupied (1) |
|---|---|---|
| **Actual Available (0)** | TN = {int(champ_test.tn):,} | FP = {int(champ_test.fp):,} |
| **Actual Occupied (1)** | FN = {int(champ_test.fn):,} | TP = {int(champ_test.tp):,} |

Of {int(champ_test.tp + champ_test.fn):,} truly occupied intervals in the test set, the model correctly identifies {int(champ_test.tp):,} ({champ_test.recall*100:.1f}% recall). Of {int(champ_test.fp):,} false alarms raised, these represent a false positive rate of approximately {champ_test.fp/(champ_test.fp+champ_test.tn)*100:.2f}% relative to the true negative pool.

### 17.5 Feature Importance (XGBoost Experiment D — Gain-Based)

{fi_table(fi_raw)}

> **Note on interpretation:** Feature importance values reflect model-reported predictive importance (gain) within the XGBoost tree structure. They should not be interpreted as causal factors or as universally applicable rankings across different datasets or models.

The dominant contribution of `previous_occupancy` is consistent with the strong temporal autocorrelation of occupancy states. Group B features (historical occupancy) account for approximately {fi_raw[fi_raw['feature'].isin(['previous_occupancy','rolling_2hr_occupancy'])]['pct'].sum():.2f}% of model-reported importance, underscoring the ablation study findings.

---

## 18. Threshold Analysis

### 18.1 Threshold Selection

The decision threshold of 0.50 was selected based on validation-set performance. At this threshold, the validation F1 is {fmt(champ_val.f1,4)}. Threshold selection was performed exclusively on the validation set — the test set was not consulted — ensuring that the test evaluation is unbiased.

### 18.2 Test Performance at Selected Threshold

At threshold = 0.50 on the test set: Precision = {fmt(champ_test.precision,4)}, Recall = {fmt(champ_test.recall,4)}, F1 = {fmt(champ_test.f1,4)}. The near-equal Precision and Recall values reflect a balanced trade-off appropriate for an application where both false negatives and false positives carry operational costs.

---

## 19. Calibration Analysis

### 19.1 Brier Score

| Model | Split | Brier Score |
|---|---|---|
| XGBoost (Exp D) | Test | **0.0238** |
| Persistence | Test | 0.0263 |

The XGBoost model achieves a lower Brier score than the Persistence baseline, indicating better-calibrated probability outputs. This is particularly important for downstream station ranking and recommendation, where the continuous probability is used directly.

---

## 20. Statistical Robustness

### 20.1 Bootstrap Confidence Intervals (1,000 resamples, 95% level)

| Metric | Point Estimate | 95% CI Lower | 95% CI Upper |
|---|---|---|---|
| PR-AUC | 0.7997 | 0.7872 | 0.8120 |
| F1-Score | 0.7665 | 0.7570 | 0.7759 |
| Precision | 0.7677 | 0.7563 | 0.7801 |
| Recall | 0.7652 | 0.7524 | 0.7774 |

### 20.2 Comparison Against Persistence Baseline (Bootstrap)

| Metric | XGBoost | Persistence | Difference | 95% CI |
|---|---|---|---|---|
| PR-AUC | 0.7997 | 0.7722 | **+0.0275** | [+0.0191, +0.0358] |
| F1-Score | 0.7665 | 0.7656 | +0.0008 | [−0.0000, +0.0017] |

**PR-AUC:** The 95% bootstrap CI for the PR-AUC difference ([+0.0191, +0.0358]) is strictly positive, providing statistical support for a meaningful PR-AUC advantage of XGBoost over Persistence within the evaluated sample.

**F1-Score:** The 95% CI for the F1 difference ([−0.0000, +0.0017]) includes values near zero. **The study does not claim a statistically significant F1 improvement** over the Persistence baseline. The practical advantage of XGBoost lies in its superior probability calibration (PR-AUC) rather than in binary classification performance at the 0.50 threshold.

---

## 21. Error Analysis

### 21.1 False Negatives (FN = {int(champ_test.fn):,} in test set)

A false negative occurs when the model predicts a station as available but it is actually occupied at T + 30 minutes. False negatives are concentrated during periods of rapid occupancy onset — particularly during morning arrival periods — when the historical occupancy history provides limited advance warning.

**Operational consequence:** A driver may route to a station that becomes occupied before arrival.

### 21.2 False Positives (FP = {int(champ_test.fp):,} in test set)

A false positive occurs when the model predicts a station as occupied but it is actually available. This is associated with sessions that terminate earlier than the historical average for that station.

**Operational consequence:** A driver is warned that a station may be occupied, but it is available upon arrival — a conservative false alarm with lower operational cost than a false negative.

### 21.3 Caveat

The error patterns described above are observed correlates in this dataset and should not be interpreted as universal causal explanations.

---

## 22. Discussion

### 22.1 Key Findings

The results lead to the following observations within the context of the ACN-Caltech dataset:

1. **Historical occupancy is the dominant predictive signal.** Adding `previous_occupancy` and `rolling_2hr_occupancy` to the temporal baseline produces the largest single improvement (F1 from ~0.00 to ~0.77). This reflects the strong temporal autocorrelation of EV charging sessions.

2. **XGBoost achieves the strongest probability calibration.** On the full feature set (Experiment D), XGBoost achieves the highest test PR-AUC ({fmt(champ_test.pr_auc,4)}), important for ranking and recommendation applications where the continuous probability is used by downstream systems.

3. **The Persistence baseline is competitively strong.** The near-zero F1 margin between XGBoost (+0.0008) and Persistence demonstrates that the baseline has already captured much of the binary structure. The clearer advantage lies in calibrated probability outputs (PR-AUC advantage: +0.0275, 95% CI: [+0.0191, +0.0358]).

4. **Station-specific features improve probability calibration.** Adding `station_hour_occupancy_rate` and `station_avg_session_duration` improves PR-AUC without substantially changing binary classification accuracy.

5. **Accuracy is an unreliable metric under class imbalance.** The Always-Zero baseline achieves {az_test.accuracy*100:.1f}% accuracy without identifying a single occupied interval. PR-AUC and F1 must be primary metrics.

### 22.2 Context and Scope

These findings are specific to the ACN-Caltech dataset. The Caltech site represents a workplace EV charging network with specific usage patterns (weekday-dominant, mid-day peak). Generalisation to other site types — including public highway chargers, residential charging, or Indian urban networks — cannot be assumed without validation on additional datasets.

---

## 23. Deployment Architecture

The trained model is deployed as part of the EVConnect web application prototype:

```
ACN Historical Data (data/processed/station_occupancy_30min.csv)
                         ↓
         Feature Engineering (api/feature_engineering.py)
           • Temporal features from query timestamp
           • Historical lags from occupancy lookup
           • Station rates from training lookup tables
                         ↓
     XGBoost Inference (models/final/ev_occupancy_xgboost.pkl)
                         ↓
         FastAPI Prediction Service (api/main.py)
             • POST /predict (single station)
             • POST /predict/batch (all stations)
             • GET /latest-timestamp
             • GET /health
                         ↓
         Node.js Backend (backend/server.js)
             • Authenticates users (JWT)
             • Manages station & session records (MongoDB)
             • Routes prediction requests to FastAPI
                         ↓
         React Frontend (frontend/src/)
             • Dashboard: station grid with availability predictions
             • Station Details: 30-min forecast visualisation
             • Recommendations: ranked by availability score
             • Sessions & Favourites management
```

| Property | Value |
|---|---|
| Production model | `models/final/ev_occupancy_xgboost.pkl` |
| Feature list | `models/final/features.json` (8 features) |
| Decision threshold | 0.50 (`models/final/threshold.json`) |
| Prediction horizon | 30 minutes |
| Inference API | FastAPI (Python 3.x) |
| Backend | Node.js + Express + MongoDB |
| Frontend | React + Vite |

> **Important:** The EVConnect application is a research prototype demonstrating the prediction pipeline. It is not a production-scale commercial EV charging management system.

---

## 24. Limitations

1. **Single-site dataset.** All findings are specific to the Caltech campus charging network. User demographics (academic community), session duration distributions, and temporal utilisation patterns are not representative of all EV charging contexts.
2. **No generalisation to Indian charging networks.** The original research proposal references the context of Indian EV infrastructure. This study does not demonstrate generalisation to Indian charging networks.
3. **No exogenous variables.** Weather conditions, traffic data, campus events, and real-time station telemetry were not incorporated.
4. **No geographic/spatial features.** Station location, proximity to amenities, and distance from user homes or workplaces were not included.
5. **30-minute fixed prediction horizon.** Only a single prediction horizon is evaluated. Multi-step forecasting or other horizon lengths are not explored.
6. **Binary occupancy formulation.** The study predicts occupancy (occupied/available) rather than continuous energy demand, number of concurrent sessions, or charging power profiles.
7. **Historical occupancy signal dominance.** The model relies heavily on recent occupancy history. In cold-start scenarios (new stations with no history), model performance would likely degrade significantly.
8. **Static lookup tables.** Station-specific features are computed once from the training split and not updated dynamically. Model performance may degrade if underlying station usage patterns shift substantially over time.
9. **Dataset temporal scope.** The dataset covers October 2019 to September 2021, including the COVID-19 pandemic period. Generalisation to other periods may be limited.

---

## 25. Future Work

1. **Validation on Indian charging datasets.** Applying and retraining the pipeline on public or partner EV charging datasets from Indian networks.
2. **Multi-site validation.** Extending evaluation to multiple ACN sites and other public charging networks.
3. **Geographic and spatial features.** Incorporating station location coordinates, proximity to workplaces, parking zones.
4. **Exogenous variable integration.** Including weather data (temperature, precipitation) and traffic density.
5. **Real-time station telemetry.** Replacing the historical occupancy grid with live station status streams.
6. **Multi-step forecasting.** Extending prediction to multiple future horizons simultaneously.
7. **Wait-time and queue prediction.** Predicting how long a currently occupied station will remain occupied.
8. **Continuous demand forecasting.** Predicting total energy demand (kWh) or number of active sessions.
9. **Larger and more diverse networks.** Validating on datasets with hundreds or thousands of stations.
10. **Online and adaptive learning.** Exploring models that update continuously with new session data.

> None of the above directions have been implemented in this study. They are identified as research opportunities for extension.

---

## 26. Conclusion

This study presents a reproducible machine learning pipeline for 30-minute-ahead binary EV charging station occupancy prediction using the ACN-Data Caltech dataset. A feature ablation study across four configurations (Experiments A–D) and three algorithm families (Logistic Regression, Random Forest, XGBoost) — yielding 12 model configurations — demonstrates that historical occupancy lag features are the most critical predictors, with station-specific operational features providing additional discrimination.

The selected champion model — XGBoost trained on the full eight-feature set (Experiment D) — achieves a test PR-AUC of **{fmt(champ_test.pr_auc,4)}** (95% CI: [0.7872, 0.8120]), F1 of **{fmt(champ_test.f1,4)}**, and ROC-AUC of **{fmt(champ_test.roc_auc,4)}** on a held-out chronological test set of 79,585 intervals. The model demonstrates a statistically meaningful PR-AUC advantage of +0.0275 (95% bootstrap CI: [+0.0191, +0.0358]) over the Persistence baseline, supporting the practical utility of calibrated probability outputs for station ranking and recommendation.

Within the acknowledged limitations of a single-site, historically-bounded dataset, the results indicate that machine learning approaches — particularly gradient boosting with historical occupancy features — can provide useful occupancy probability estimates for EV charging station management systems. Generalisation to geographically and operationally diverse networks, including Indian EV charging infrastructure, requires further validation and remains an important direction for future research.

---

## 27. References

> [REFERENCE NEEDED]: Lee, Z. J., et al. "ACN-Data: Analysis and Applications of an Open EV Charging Dataset." ACM e-Energy. (Exact year and full citation needed.)

> [REFERENCE NEEDED]: IEA. "Global EV Outlook." International Energy Agency. (Annual report; year-specific citation needed.)

> [REFERENCE NEEDED]: Davis, J., & Goadrich, M. (2006). "The relationship between Precision-Recall and ROC curves." ICML 2006.

> [REFERENCE NEEDED]: Chen, T., & Guestrin, C. (2016). "XGBoost: A scalable tree boosting system." KDD 2016.

> [REFERENCE NEEDED]: Breiman, L. (2001). "Random Forests." Machine Learning, 45(1), 5–32.

> [REFERENCE NEEDED]: Reference for chronological cross-validation / time series evaluation methodology.

> [REFERENCE NEEDED]: Efron, B., & Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall. (Bootstrap CI methodology.)

> [REFERENCE NEEDED]: General EV charging demand prediction / occupancy prediction survey paper reference for Introduction related work.

> [REFERENCE NEEDED]: FastAPI reference (if required by examiner).

---
---

# SUPPORTING MATERIALS

---

## B. SOP-to-Paper Alignment Table

| SOP Section | Implementation | Paper Section | Status |
|---|---|---|---|
| ACN-Data analysis | Full session + occupancy grid analysis | §7, §8, §9 | ✅ Implemented |
| Data preprocessing | Occupancy grid, timezone, chronological splits | §8 | ✅ Implemented |
| EDA | Temporal patterns, station heterogeneity, session duration | §9 | ✅ Implemented |
| Feature engineering | 8 features, 4 groups, leakage-safe | §11 | ✅ Implemented |
| Occupancy/demand prediction | Binary occupancy (confirmed post-data review) | §10 | ✅ Implemented (binary) |
| Baseline models | Always-Zero, Persistence | §13 | ✅ Implemented |
| Multiple ML models | LR, RF, XGBoost × 4 experiments = 12 configs | §14 | ✅ Implemented |
| Comparative evaluation | Ablation study, full results tables | §14, §15 | ✅ Implemented |
| Best model selection | XGBoost Exp D selected on validation set only | §17 | ✅ Implemented |
| Saving model artifact | `models/final/ev_occupancy_xgboost.pkl` | §23 | ✅ Implemented |
| FastAPI exposure | FastAPI `/predict`, `/predict/batch`, `/health` | §23 | ✅ Implemented |
| Documentation | Phase 7 paper draft | §1–27 | ✅ This document |

---

## C. Recommended Tables and Figures

### Tables for Paper

| # | Title | Source | Paper Section |
|---|---|---|---|
| T1 | Dataset Summary Statistics | `station_occupancy_30min.csv` | §7 |
| T2 | Chronological Train/Val/Test Split | Split row counts | §7.4 |
| T3 | Feature Engineering Summary (8 features, 4 groups) | `features.json`, `build_features.py` | §11 |
| T4 | Baseline Results (Always-Zero, Persistence) | `baseline_results.csv` | §13 |
| T5 | Full Validation Set Comparison (12 configs) | `model_comparison_v1.csv` | §14 |
| T6 | Full Test Set Comparison (12 configs) | `model_comparison_v1.csv` | §14 |
| T7 | Champion Model — Validation & Test Metrics | `metadata.json` | §17 |
| T8 | Confusion Matrix (Exp D XGBoost, Test) | `model_comparison_v1.csv` | §17.4 |
| T9 | Feature Importance (Exp D XGBoost) | `feature_importance_v1.csv` | §17.5 |
| T10 | Bootstrap CIs and Baseline Comparison | `robustness_results.csv`, `xgb_vs_persistence_bootstrap.csv` | §20 |

### Figures for Paper

| # | Title | Source | Paper Section |
|---|---|---|---|
| F1 | Hourly Occupancy Rate by Hour of Day | `01_dataset_analysis.ipynb` EDA section | §9.1 |
| F2 | Weekly Occupancy Rate by Day of Week | `01_dataset_analysis.ipynb` EDA section | §9.1 |
| F3 | Station-Level Occupancy Rate Distribution (55 stations) | `01_dataset_analysis.ipynb` EDA section | §9.2 |
| F4 | Session Duration Distribution by Station | `01_dataset_analysis.ipynb` EDA section | §9.3 |
| F5 | PR-AUC Comparison: 12 Model Configurations (Test) | `model_comparison_v1.csv` | §15 |
| F6 | XGBoost Feature Importance Bar Chart (Exp D) | `feature_importance_v1.csv` | §17.5 |
| F7 | Precision-Recall Curve: XGBoost Exp D vs Persistence (Test) | `model_predictions_v1.csv` | §19 |
| F8 | Deployment Architecture Diagram | System design | §23 |

---

## D. Project Artefacts Serving as References

| Artefact | Role in Paper |
|---|---|
| `data/processed/model_comparison_v1.csv` | Ground truth for all 12×2 model metrics |
| `data/processed/model_predictions_v1.csv` | Raw prediction probabilities; source for recalculated ROC-AUC |
| `data/processed/feature_importance_v1.csv` | Feature importance source |
| `data/processed/baseline_results.csv` | Always-Zero and Persistence baseline metrics |
| `data/processed/robustness_results.csv` | Bootstrap CIs for champion model |
| `data/processed/xgb_vs_persistence_bootstrap.csv` | Bootstrap baseline comparison |
| `data/processed/station_hour_rates_train.csv` | 1,320-row lookup table (55 stations × 24 hours) |
| `models/final/metadata.json` | Champion model provenance record |
| `models/final/features.json` | Exact 8-feature list |
| `models/final/threshold.json` | Decision threshold (0.50) |
| `src/features/build_features.py` | Leakage-safe feature engineering methodology |
| `src/models/train_models.py` | Training and evaluation code |
| `notebooks/01_dataset_analysis.ipynb` | EDA and ablation results |

---

## E. External References Requiring Citation

| # | Item | Location Needed |
|---|---|---|
| R1 | ACN-Data paper (Lee et al.) | §4, §7.1, References |
| R2 | IEA Global EV Outlook | §4 Introduction |
| R3 | PR-AUC vs ROC-AUC under imbalance (Davis & Goadrich 2006) | §16.1 |
| R4 | XGBoost algorithm (Chen & Guestrin 2016) | §12.2 |
| R5 | Random Forest algorithm (Breiman 2001) | §12.2 |
| R6 | Logistic Regression textbook reference | §12.2 |
| R7 | Chronological evaluation / time series CV methodology | §12.3 |
| R8 | Bootstrap CI methodology (Efron & Tibshirani 1993) | §20.1 |
| R9 | EV charging demand/occupancy prediction survey | §4 related work |
| R10 | Indian EV charging context | §24, if mentioned |

---

## F. Final Metrics Consistency Checklist

| Metric | Value Used in Paper | Authoritative Source | Check |
|---|---|---|---|
| Test PR-AUC | **0.7997** | `model_comparison_v1.csv`; `metadata.json`; recalculated from `model_predictions_v1.csv` | ✅ |
| Test F1 | **0.7665** | Same | ✅ |
| Test Precision | **0.7677** | Same | ✅ |
| Test Recall | **0.7652** | Same | ✅ |
| Test ROC-AUC | **0.9775** (NOT 0.9482) | Same; direct recalculation confirms 0.977540 | ✅ |
| Test Balanced Acc. | **0.8757** | Same | ✅ |
| Test Accuracy | **0.9738** | Same | ✅ |
| Val PR-AUC | **0.7279** | `model_comparison_v1.csv` | ✅ |
| Val F1 | **0.7446** | Same | ✅ |
| Val ROC-AUC | **0.9646** | Same | ✅ |
| scale_pos_weight | **27.275266952322657** | `metadata.json`; model artifact | ✅ |
| Threshold | **0.50** | `threshold.json` | ✅ |
| Station-hour rows | **1,320** (55×24) (NOT 1,234) | `station_hour_rates_train.csv` direct count | ✅ |
| PR-AUC Bootstrap CI | **[0.7872, 0.8120]** | `robustness_results.csv` | ✅ |
| F1 Bootstrap CI | **[0.7570, 0.7759]** | `robustness_results.csv` | ✅ |
| XGB vs Persistence PR-AUC Δ | **+0.0275 [+0.0191, +0.0358]** | `xgb_vs_persistence_bootstrap.csv` | ✅ |
| Test Brier Score XGB | **0.0238** | `robustness_results.csv` | ✅ |
| Test Brier Score Persistence | **0.0263** | `robustness_results.csv` | ✅ |
| Training rows | **1,662,925** | `occupancy_features_v2.csv` split counts | ✅ |
| Test rows | **79,585** | Confusion matrix sum; `model_predictions_v1.csv` | ✅ |
| TP / FP / FN / TN (Test) | **3,418 / 1,034 / 1,049 / 74,084** | `model_comparison_v1.csv` | ✅ |

---

## G. Viva Preparation — 33 Key Questions

### Research Problem and Formulation

1. **Why was binary occupancy chosen over continuous demand regression?**
   The ACN grid provides clean binary occupancy indicators at 30-minute resolution. Binary probability is directly actionable (Will this station be free?) and provides a calibrated score for ranking and recommendation.

2. **What is `target_occupancy` mathematically?**
   `target_occupancy(T) = occupancy(T + 30 minutes)` where 0 = available, 1 = occupied.

3. **What is a chronological train-validation-test split and why is it critical here?**
   The data is split by time — training ends before validation starts, validation ends before test starts. This prevents temporal leakage: a model cannot use future data to predict the past, which would inflate performance estimates.

4. **Why is the test set evaluated exactly once?**
   To prevent inadvertent optimisation of the model or threshold to the test set. Using the test set multiple times risks overfitting to test noise.

### Class Imbalance

5. **What is the positive (occupied) class prevalence in training data?**
   58,812 / 1,662,925 = **3.54%**

6. **Why is accuracy misleading here?**
   The Always-Zero baseline (predict everything as available) achieves 94.4% test accuracy while correctly identifying zero occupied stations (F1 = 0.000). A metric that rewards ignoring the minority class is uninformative.

7. **What does `scale_pos_weight = 27.275` instruct XGBoost to do?**
   It instructs XGBoost to weight each positive (occupied) sample approximately 27.275× more than each negative sample during gradient computation, compensating for the class imbalance during training.

8. **Why is PR-AUC preferred over ROC-AUC under severe class imbalance?**
   ROC-AUC is computed using the True Positive Rate and False Positive Rate; the FPR denominator (TN + FP) is dominated by the large majority class, making ROC-AUC less sensitive to minority-class errors. PR-AUC focuses on precision and recall, which are directly computed on the minority class, making it more informative about model utility for rare events.

### Feature Engineering

9. **Name all 8 features and their computation.**
   `local_hour` (hour 0–23 Pacific), `local_day_of_week` (0–6), `is_weekend` (binary), `month` (1–12), `previous_occupancy` (occupancy at T−30 min), `rolling_2hr_occupancy` (mean of occupancy at T−30, T−60, T−90, T−120 min), `station_hour_occupancy_rate` (training-only mean occupancy for station×hour), `station_avg_session_duration` (training-only mean session duration per station in minutes).

10. **What is `rolling_2hr_occupancy`? What time offsets does it use?**
    The mean of binary occupancy at T−30, T−60, T−90, and T−120 minutes. It captures the mean occupancy over the preceding 2 hours.

11. **How was `station_hour_occupancy_rate` computed? Why must it come from training data only?**
    For each of the 55 stations × 24 hours = 1,320 combinations, the mean binary occupancy from the training period was computed. If it were computed from all data, information from the validation/test periods would leak into the training features, inflating performance.

12. **What happens when an unseen station is queried at inference time?**
    Fallback to the global training-set mean: occupancy rate = 0.091185; session duration = 164.55 minutes.

13. **What is the data leakage risk and how was it mitigated?**
    If aggregate features (`station_hour_occupancy_rate`, `station_avg_session_duration`) were computed from the full dataset, test-period patterns would contaminate training-time features. Mitigation: both tables are computed exclusively from training rows (≤ 2021-06-30) and programmatic assertions verify no future data was used.

### Experimental Design

14. **What is a feature ablation study?**
    A systematic experiment where feature subsets are progressively expanded (A → B → C → D) to measure the marginal contribution of each feature group to model performance.

15. **What do Experiments A, B, C, D each add?**
    A: temporal only. B: + historical occupancy (previous + rolling). C: + station-hour occupancy rate. D: + station average session duration.

16. **How many total model configurations were evaluated?**
    3 algorithms × 4 experiments = **12 configurations**.

17. **On which split was the champion model selected?**
    **Validation set only.** The test set was not consulted during model selection.

18. **On which split was the decision threshold 0.50 selected?**
    **Validation set.** This threshold was then applied unchanged to test evaluation.

### Model Results

19. **What is the test PR-AUC of XGBoost Exp D?**
    **0.7997**

20. **What is the authoritative test ROC-AUC?**
    **0.9775** (not 0.9482 — the old value from a different model artifact is superseded).

21. **Interpret the confusion matrix in operational terms.**
    TP = 3,418: the model correctly predicted occupied stations. FP = 1,034: the model falsely warned the station was occupied (it was available — conservative error). FN = 1,049: the model missed occupied stations (it said available but was occupied — more costly for driver). TN = 74,084: correctly predicted available stations.

22. **What is the most important feature per XGBoost gain importance?**
    `previous_occupancy` at 88.81% of total gain. This reflects the strong temporal autocorrelation of EV charging sessions.

23. **Why should feature importances not be interpreted causally?**
    XGBoost gain-based importance measures how much each feature reduces loss within the specific tree structure trained on this specific dataset. A different training set, different model architecture, or different feature set would produce different importances. Correlation ≠ causation.

### Baseline Comparison

24. **Why is the Persistence baseline strong on F1 but weaker on PR-AUC?**
    Sessions typically persist across multiple 30-minute intervals, so "predict same as last time" correctly classifies a high proportion of intervals at the 0.50 threshold — giving high F1. But Persistence is a deterministic rule (it only outputs 0 or 1), not a calibrated probability, so its PR-AUC is limited to 0.7722 vs XGBoost's 0.7997.

25. **Is the F1 improvement over Persistence statistically significant?**
    No. The 95% bootstrap CI for the F1 difference is [−0.0000, +0.0017], which includes values near zero. The study explicitly does not claim a statistically significant F1 improvement.

26. **Is the PR-AUC improvement over Persistence statistically meaningful?**
    Yes. The 95% bootstrap CI [+0.0191, +0.0358] is strictly positive, indicating the PR-AUC advantage is consistent across resamples of the test set.

### Statistical Robustness

27. **What is a bootstrap confidence interval and how were they computed?**
    1,000 random samples with replacement were drawn from the test set. The chosen metric was computed on each sample. The 2.5th and 97.5th percentiles of the 1,000 estimates form the 95% CI. This provides an estimate of how stable the metric is with respect to random variation in the test sample.

28. **What does the Brier Score measure and which model has the better score?**
    The Brier Score is the mean squared error between predicted probabilities and true binary labels (0 = perfect). Lower is better. XGBoost (0.0238) < Persistence (0.0263), indicating XGBoost has better-calibrated probability outputs.

### Deployment

29. **What is FastAPI and how does it connect to Node.js?**
    FastAPI is a Python web framework for building REST APIs. In EVConnect, the Node.js backend calls FastAPI's `/predict` or `/predict/batch` endpoints via HTTP, passing station ID and timestamp. FastAPI runs the feature engineering pipeline and returns predicted probabilities.

30. **Where is the final production model stored?**
    `models/final/ev_occupancy_xgboost.pkl`

31. **What lookup tables does FastAPI load at startup?**
    `data/processed/station_hour_rates_train.csv` (1,320 rows: 55 stations × 24 hours) and station average session durations — both derived exclusively from the training split.

32. **What happens when FastAPI receives a `/predict/batch` request?**
    It iterates over all 55 stations, builds the 8-feature vector for each using the provided timestamp, performs inference using the XGBoost model, applies the 0.50 threshold, and returns a list of availability predictions and probabilities.

### Limitations and Scope

33. **Is this model validated for Indian EV charging networks?**
    No. This study uses data exclusively from the Caltech campus charging network in Pasadena, California. Indian charging networks may have fundamentally different temporal patterns, session characteristics, and infrastructure configurations. Validation on Indian data is identified as future work.

---

*Phase 7 documentation complete.*
*All metrics verified against authoritative CSV/JSON artefacts. No project files were modified.*
*Old ROC-AUC value 0.9482 does NOT appear in this document. Old station-hour count 1,234 does NOT appear in this document.*
"""

os.makedirs(ARTIFACT_DIR, exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(paper)

print(f"Paper written to: {OUT_PATH}")
print(f"File size: {os.path.getsize(OUT_PATH):,} bytes")
print(f"Line count: {paper.count(chr(10)):,}")
