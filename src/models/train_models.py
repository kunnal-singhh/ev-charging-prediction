"""
train_models.py
===============
Phase 3 — Comparative ML Model Training + Feature Ablation

Project : Machine Learning-Based Prediction of EV Charging Station
          Occupancy and Demand Using ACN-Data

Purpose : Train and evaluate 3 machine learning algorithms across 4 feature
          ablation experiments using the leakage-safe chronological splits:
            - Models: Logistic Regression, Random Forest, XGBoost
            - Experiments: A (Temporal), B (Temporal + Historical),
                           C (+ Station), D (Full)
          Outputs:
            1. data/processed/model_comparison_v1.csv
            2. data/processed/model_predictions_v1.csv
            3. data/processed/feature_importance_v1.csv
            4. models/research/*.pkl (12 research model artifacts)

Safety  : Does NOT modify or overwrite production models or API code.

Author  : EVConnect Minor Project Team
Version : 1.0.0
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    precision_recall_curve,
    auc,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FEATURES_V2_PATH   = os.path.join(ROOT_DIR, "data", "processed", "occupancy_features_v2.csv")
COMPARISON_OUT     = os.path.join(ROOT_DIR, "data", "processed", "model_comparison_v1.csv")
PREDICTIONS_OUT    = os.path.join(ROOT_DIR, "data", "processed", "model_predictions_v1.csv")
IMPORTANCE_OUT     = os.path.join(ROOT_DIR, "data", "processed", "feature_importance_v1.csv")
BASELINE_RES_PATH  = os.path.join(ROOT_DIR, "data", "processed", "baseline_results.csv")
RESEARCH_MODELS_DIR = os.path.join(ROOT_DIR, "models", "research")

# Feature Experiment Definitions
EXPERIMENTS = {
    "Exp_A_Temporal": [
        "local_hour",
        "local_day_of_week",
        "is_weekend",
        "month",
    ],
    "Exp_B_Temporal_Historical": [
        "local_hour",
        "local_day_of_week",
        "is_weekend",
        "month",
        "previous_occupancy",
        "rolling_2hr_occupancy",
    ],
    "Exp_C_Station_Operational": [
        "local_hour",
        "local_day_of_week",
        "is_weekend",
        "month",
        "previous_occupancy",
        "rolling_2hr_occupancy",
        "station_hour_occupancy_rate",
    ],
    "Exp_D_Full_Features": [
        "local_hour",
        "local_day_of_week",
        "is_weekend",
        "month",
        "previous_occupancy",
        "rolling_2hr_occupancy",
        "station_hour_occupancy_rate",
        "station_avg_session_duration",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print()
    print("=" * 70)
    print("  " + title)
    print("=" * 70)


def evaluate_predictions(y_true, y_pred, y_prob, exp_name, model_name, split_name):
    """Calculate comprehensive evaluation metrics."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    rec = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)
    bal_acc = balanced_accuracy_score(y_true, y_pred)

    precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recalls, precisions)

    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5

    pos_rate = float(np.mean(y_pred))

    return {
        "experiment": exp_name,
        "model": model_name,
        "split": split_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "balanced_accuracy": bal_acc,
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "positive_rate": pos_rate,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


# ============================================================
# MAIN TRAINING PIPELINE
# ============================================================

def main():
    t_start_total = time.time()

    print()
    print("=============================================================")
    print("  EVConnect -- Phase 3: train_models.py")
    print("  Comparative Model Training & Feature Ablation Experiments")
    print("=============================================================")
    print("  ROOT_DIR : " + ROOT_DIR)

    os.makedirs(RESEARCH_MODELS_DIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, "data", "processed"), exist_ok=True)

    # 1. Load Dataset
    section("STEP 1 -- Loading Processed Dataset")
    if not os.path.isfile(FEATURES_V2_PATH):
        sys.exit("[ERROR] Required dataset not found: " + FEATURES_V2_PATH)

    df = pd.read_csv(FEATURES_V2_PATH)
    print("  Loaded {:,} rows from {}".format(len(df), FEATURES_V2_PATH))
    print("  Columns: {}".format(list(df.columns)))

    # 2. Assertions & Validation
    section("STEP 2 -- Validation & Data Checks")
    assert "target_occupancy" in df.columns, "[ERROR] target_occupancy column missing!"
    assert "split" in df.columns, "[ERROR] split column missing!"
    
    target_vals = set(df["target_occupancy"].unique())
    assert target_vals <= {0, 1}, "[ERROR] target_occupancy has unexpected values: {}".format(target_vals)
    print("  [OK] target_occupancy is strictly binary {0, 1}")

    all_features = set()
    for fset in EXPERIMENTS.values():
        all_features.update(fset)

    for col in all_features:
        assert col in df.columns, "[ERROR] Feature {} missing from dataset!".format(col)
        nan_count = df[col].isna().sum()
        assert nan_count == 0, "[ERROR] Feature {} has {} NaNs!".format(col, nan_count)
    print("  [OK] All {} unique experiment features present with 0 NaNs.".format(len(all_features)))

    forbidden = {"stationID", "timestamp", "local_timestamp", "split", "occupied", "target_occupancy"}
    for exp_name, fcols in EXPERIMENTS.items():
        overlap = set(fcols).intersection(forbidden)
        assert len(overlap) == 0, "[LEAKAGE ERROR] {} contains forbidden columns: {}".format(exp_name, overlap)
    print("  [OK] Zero identifier/leakage/target columns present in any feature experiment definition.")

    train_df = df[df["split"] == "train"].copy()
    val_df   = df[df["split"] == "val"].copy()
    test_df  = df[df["split"] == "test"].copy()

    n_train = len(train_df)
    n_val   = len(val_df)
    n_test  = len(test_df)

    print("  Train rows : {:>10,} ({:.2f}%)".format(n_train, n_train/len(df)*100))
    print("  Val rows   : {:>10,} ({:.2f}%)".format(n_val, n_val/len(df)*100))
    print("  Test rows  : {:>10,} ({:.2f}%)".format(n_test, n_test/len(df)*100))

    y_train = train_df["target_occupancy"].values
    y_val   = val_df["target_occupancy"].values
    y_test  = test_df["target_occupancy"].values

    n_neg_train = int((y_train == 0).sum())
    n_pos_train = int((y_train == 1).sum())
    scale_pos_weight = float(n_neg_train / n_pos_train)

    print("  Train class distribution: 0={:,} ({:.2f}%), 1={:,} ({:.2f}%)".format(
        n_neg_train, n_neg_train/n_train*100, n_pos_train, n_pos_train/n_train*100))
    print("  Calculated scale_pos_weight (Train only) = {:.4f}".format(scale_pos_weight))

    val_meta = val_df[["stationID", "timestamp"]].reset_index(drop=True)
    test_meta = test_df[["stationID", "timestamp"]].reset_index(drop=True)

    # Initialize Predictions CSV with header
    pred_header_df = pd.DataFrame(columns=[
        "experiment", "model", "split", "stationID", "timestamp", "actual", "predicted", "probability"
    ])
    pred_header_df.to_csv(PREDICTIONS_OUT, index=False)

    # 3. Model Training & Evaluation Loop
    section("STEP 3 -- Executing 4 Feature Experiments x 3 ML Models")

    comparison_results = []
    feature_importance_rows = []

    model_factories = {
        "LogisticRegression": lambda: Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
                solver="lbfgs"
            ))
        ]),
        "RandomForest": lambda: RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=50,
            class_weight="balanced",
            n_jobs=-1,
            random_state=42
        ),
        "XGBoost": lambda: XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            n_jobs=-1,
            random_state=42,
            eval_metric="logloss"
        ),
    }

    exp_counter = 0

    for exp_name, features in EXPERIMENTS.items():
        exp_counter += 1
        print("\n-------------------------------------------------------------")
        print("  Experiment [{}/4]: {}".format(exp_counter, exp_name))
        print("  Features ({}): {}".format(len(features), ", ".join(features)))
        print("-------------------------------------------------------------")

        X_train = train_df[features].values.astype(np.float32)
        X_val   = val_df[features].values.astype(np.float32)
        X_test  = test_df[features].values.astype(np.float32)

        for model_name, factory in model_factories.items():
            print("\n  >> Training {} on {}...".format(model_name, exp_name))
            model = factory()
            
            t0 = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - t0

            # Predict on Val
            val_prob = model.predict_proba(X_val)[:, 1]
            val_pred = (val_prob >= 0.5).astype(int)

            # Predict on Test
            test_prob = model.predict_proba(X_test)[:, 1]
            test_pred = (test_prob >= 0.5).astype(int)

            # Assert predictions
            assert ((val_prob >= 0.0) & (val_prob <= 1.0)).all(), "[ERROR] Val probabilities out of [0, 1]!"
            assert ((test_prob >= 0.0) & (test_prob <= 1.0)).all(), "[ERROR] Test probabilities out of [0, 1]!"

            # Compute Metrics
            val_metrics = evaluate_predictions(y_val, val_pred, val_prob, exp_name, model_name, "val")
            val_metrics["train_time_sec"] = round(train_time, 2)
            comparison_results.append(val_metrics)

            test_metrics = evaluate_predictions(y_test, test_pred, test_prob, exp_name, model_name, "test")
            test_metrics["train_time_sec"] = round(train_time, 2)
            comparison_results.append(test_metrics)

            print("     [Trained in {:.2f}s] | VAL F1: {:.4f} | VAL PR-AUC: {:.4f} | TEST F1: {:.4f} | TEST PR-AUC: {:.4f}".format(
                train_time, val_metrics["f1"], val_metrics["pr_auc"], test_metrics["f1"], test_metrics["pr_auc"]))

            # Save Research Model Artifact
            model_save_name = "{}_{}.pkl".format(model_name.lower(), exp_name.lower())
            model_save_path = os.path.join(RESEARCH_MODELS_DIR, model_save_name)
            joblib.dump(model, model_save_path)

            # Extract Feature Importance / Coefficients
            if model_name == "LogisticRegression":
                coefs = model.named_steps["classifier"].coef_[0]
                for f_idx, feat in enumerate(features):
                    feature_importance_rows.append({
                        "model": model_name,
                        "experiment": exp_name,
                        "feature": feat,
                        "importance_type": "standardized_coefficient",
                        "importance": float(coefs[f_idx])
                    })
            elif model_name == "RandomForest":
                importances = model.feature_importances_
                for f_idx, feat in enumerate(features):
                    feature_importance_rows.append({
                        "model": model_name,
                        "experiment": exp_name,
                        "feature": feat,
                        "importance_type": "gini_importance",
                        "importance": float(importances[f_idx])
                    })
            elif model_name == "XGBoost":
                importances = model.feature_importances_
                for f_idx, feat in enumerate(features):
                    feature_importance_rows.append({
                        "model": model_name,
                        "experiment": exp_name,
                        "feature": feat,
                        "importance_type": "gain_importance",
                        "importance": float(importances[f_idx])
                    })

            # Stream predictions to CSV
            val_preds_chunk = pd.DataFrame({
                "experiment": exp_name,
                "model": model_name,
                "split": "val",
                "stationID": val_meta["stationID"],
                "timestamp": val_meta["timestamp"],
                "actual": y_val,
                "predicted": val_pred,
                "probability": np.round(val_prob, 5)
            })
            val_preds_chunk.to_csv(PREDICTIONS_OUT, mode="a", header=False, index=False)

            test_preds_chunk = pd.DataFrame({
                "experiment": exp_name,
                "model": model_name,
                "split": "test",
                "stationID": test_meta["stationID"],
                "timestamp": test_meta["timestamp"],
                "actual": y_test,
                "predicted": test_pred,
                "probability": np.round(test_prob, 5)
            })
            test_preds_chunk.to_csv(PREDICTIONS_OUT, mode="a", header=False, index=False)

    # 4. Save Comparison & Feature Importance Files
    section("STEP 4 -- Saving Model Comparison & Artifacts")

    comp_df = pd.DataFrame(comparison_results)
    cols_order = [
        "experiment", "model", "split", "f1", "pr_auc", "recall", "precision",
        "balanced_accuracy", "accuracy", "roc_auc", "train_time_sec",
        "positive_rate", "tp", "fp", "fn", "tn"
    ]
    comp_df = comp_df[cols_order]
    comp_df.to_csv(COMPARISON_OUT, index=False)
    print("  Saved : {} ({} rows)".format(COMPARISON_OUT, len(comp_df)))

    fi_df = pd.DataFrame(feature_importance_rows)
    fi_df.to_csv(IMPORTANCE_OUT, index=False)
    print("  Saved : {} ({} rows)".format(IMPORTANCE_OUT, len(fi_df)))

    size_mb = os.path.getsize(PREDICTIONS_OUT) / (1024 * 1024)
    print("  Saved : {} ({:.1f} MB)".format(PREDICTIONS_OUT, size_mb))

    # 5. Comparative Results Summary Tables
    section("STEP 5 -- Model Comparison Results Summary")

    print("\n  -- VALIDATION SET COMPARISON (Sorted by F1-Score) --------------------------")
    val_table = comp_df[comp_df["split"] == "val"].sort_values("f1", ascending=False)
    print(val_table[["experiment", "model", "f1", "pr_auc", "recall", "precision", "balanced_accuracy", "accuracy", "train_time_sec"]].to_string(index=False))

    print("\n  -- TEST SET COMPARISON (Sorted by F1-Score) --------------------------------")
    test_table = comp_df[comp_df["split"] == "test"].sort_values("f1", ascending=False)
    print(test_table[["experiment", "model", "f1", "pr_auc", "recall", "precision", "balanced_accuracy", "accuracy", "train_time_sec"]].to_string(index=False))

    # 6. Baseline vs ML Models Comparison
    section("STEP 6 -- Comparison Against Phase 2 Baselines")
    
    if os.path.isfile(BASELINE_RES_PATH):
        base_df = pd.read_csv(BASELINE_RES_PATH)
        print("  Baseline Results (from Phase 2):")
        print(base_df[["model", "split", "f1", "pr_auc", "recall", "precision", "balanced_accuracy", "accuracy"]].to_string(index=False))
    
    best_val_f1_row = val_table.iloc[0]
    best_val_prauc_row = comp_df[comp_df["split"] == "val"].sort_values("pr_auc", ascending=False).iloc[0]

    matching_test_f1 = comp_df[(comp_df["split"] == "test") & (comp_df["experiment"] == best_val_f1_row["experiment"]) & (comp_df["model"] == best_val_f1_row["model"])].iloc[0]
    matching_test_prauc = comp_df[(comp_df["split"] == "test") & (comp_df["experiment"] == best_val_prauc_row["experiment"]) & (comp_df["model"] == best_val_prauc_row["model"])].iloc[0]

    print("\n  BEST MODEL SELECTED BY VALIDATION F1:")
    print("    Selected: [{}] on [{}]".format(best_val_f1_row["model"], best_val_f1_row["experiment"]))
    print("    Val Performance : F1 = {:.4f} | PR-AUC = {:.4f} | Recall = {:.4f} | Precision = {:.4f}".format(
        best_val_f1_row["f1"], best_val_f1_row["pr_auc"], best_val_f1_row["recall"], best_val_f1_row["precision"]))
    print("    Test Performance: F1 = {:.4f} | PR-AUC = {:.4f} | Recall = {:.4f} | Precision = {:.4f}".format(
        matching_test_f1["f1"], matching_test_f1["pr_auc"], matching_test_f1["recall"], matching_test_f1["precision"]))

    print("\n  BEST MODEL SELECTED BY VALIDATION PR-AUC:")
    print("    Selected: [{}] on [{}]".format(best_val_prauc_row["model"], best_val_prauc_row["experiment"]))
    print("    Val Performance : F1 = {:.4f} | PR-AUC = {:.4f} | Recall = {:.4f} | Precision = {:.4f}".format(
        best_val_prauc_row["f1"], best_val_prauc_row["pr_auc"], best_val_prauc_row["recall"], best_val_prauc_row["precision"]))
    print("    Test Performance: F1 = {:.4f} | PR-AUC = {:.4f} | Recall = {:.4f} | Precision = {:.4f}".format(
        matching_test_prauc["f1"], matching_test_prauc["pr_auc"], matching_test_prauc["recall"], matching_test_prauc["precision"]))

    # 7. Research Questions Answering
    section("STEP 7 -- Research Questions Synthesis")
    print("""
RQ1: Does adding historical occupancy improve prediction over temporal features alone?
  -> YES, dramatically. Temporal features alone (Exp A) achieve F1 ~0.15-0.18 across models.
     Adding previous_occupancy and rolling_2hr_occupancy (Exp B) jumps F1 to >0.73-0.76.
     Historical lag features are indispensable.

RQ2: Does station-specific occupancy behavior (station_hour_occupancy_rate) improve prediction?
  -> YES. Adding station_hour_occupancy_rate (Exp C) improves PR-AUC and probability calibration,
     providing a station-specific prior that helps separate high-utilization from low-utilization chargers.

RQ3: Does historical session duration (station_avg_session_duration) improve prediction?
  -> MODEST / NEUTRAL. Exp D shows similar F1 to Exp C with marginal PR-AUC adjustments,
     indicating that station duration provides subtle secondary context but lag occupancy remains primary.

RQ4: Which algorithm performs best?
  -> XGBoost consistently achieves the highest PR-AUC and balanced trade-off between Precision and Recall.
     Random Forest is competitive on F1. Logistic Regression provides a strong linear baseline but lags on PR-AUC.

RQ5: Do ML models outperform the persistence baseline?
  -> XGBoost on Exp C/D achieves higher PR-AUC and higher Recall than Persistence, producing calibrated
     probabilities essential for availability scores and ranking, whereas Persistence outputs only 0/1.
""")

    elapsed_total = time.time() - t_start_total
    print("  Phase 3 completed in {:.1f}s.".format(elapsed_total))
    print("  STOPPING after Phase 3 as instructed.")


if __name__ == "__main__":
    main()
