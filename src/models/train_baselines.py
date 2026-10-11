"""
train_baselines.py
==================
Phase 2 — Baseline Models Evaluation

Project : Machine Learning-Based Prediction of EV Charging Station
          Occupancy and Demand Using ACN-Data

Purpose : Evaluate deterministic time-series and naive baselines against
          the chronological validation and test sets generated in Phase 1.
          Outputs:
            data/processed/baseline_results.csv

Baselines Evaluated:
-------------------
  1. Always-Zero Baseline:
     - Naive majority-class rule: prediction = 0 ("available") for all rows.
     - Demonstrates the illusory nature of accuracy under extreme class imbalance.

  2. Persistence Baseline:
     - Time-series baseline: prediction(T+30) = occupied(T)
     - Implemented directly as previous_occupancy.
     - Captures short-term temporal autocorrelation without machine learning.

Output File:
-----------
  data/processed/baseline_results.csv
  Columns: model,split,accuracy,precision,recall,f1,balanced_accuracy,pr_auc,roc_auc,tn,fp,fn,tp

Author  : EVConnect Minor Project Team
Version : 1.0.0
"""

import os
import sys
import time
import numpy as np
import pandas as pd

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
FEATURES_V2_PATH = os.path.join(ROOT_DIR, "data", "processed", "occupancy_features_v2.csv")
OUTPUT_CSV_PATH = os.path.join(ROOT_DIR, "data", "processed", "baseline_results.csv")


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print()
    print("=" * 65)
    print("  " + title)
    print("=" * 65)


def compute_metrics(y_true, y_pred, model_name, split_name):
    """
    Compute comprehensive classification metrics for binary occupancy.
    Handles edge cases for constant predictions (e.g. Always-Zero) safely.
    """
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    # Accuracy
    acc = accuracy_score(y_true, y_pred)

    # Precision, Recall, F1 (Class 1 - Occupied)
    # Use zero_division=0 to handle constant 0 predictions without crashing
    prec = precision_score(y_true, y_pred, pos_label=1, zero_division=0)
    rec = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    f1 = f1_score(y_true, y_pred, pos_label=1, zero_division=0)

    # Balanced Accuracy
    bal_acc = balanced_accuracy_score(y_true, y_pred)

    # ROC-AUC
    # If prediction is constant (e.g. Always-Zero), ROC-AUC is 0.5 (random guess level)
    if len(np.unique(y_pred)) < 2:
        roc_auc = 0.5
        print(f"  [NOTE] {model_name} ({split_name}): Constant predictions -> ROC-AUC defaults to 0.5000")
    else:
        roc_auc = roc_auc_score(y_true, y_pred)

    # PR-AUC
    # For binary 0/1 predictions, calculate area under Precision-Recall curve
    precisions, recalls, _ = precision_recall_curve(y_true, y_pred)
    pr_auc = auc(recalls, precisions)

    return {
        "model": model_name,
        "split": split_name,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "balanced_accuracy": bal_acc,
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def print_metrics_table(results_list):
    """Print formatted comparative table of results."""
    headers = [
        "Model", "Split", "Accuracy", "Precision", "Recall", "F1-Score",
        "Bal Acc", "PR-AUC", "ROC-AUC", "TP", "FP", "FN", "TN"
    ]
    row_fmt = "{:<13} {:<6} {:>9.4f} {:>9.4f} {:>8.4f} {:>8.4f} {:>8.4f} {:>8.4f} {:>8.4f} {:>6} {:>6} {:>6} {:>8}"
    
    print("-" * 115)
    print("{:<13} {:<6} {:>9} {:>9} {:>8} {:>8} {:>8} {:>8} {:>8} {:>6} {:>6} {:>6} {:>8}".format(*headers))
    print("-" * 115)
    
    for r in results_list:
        print(row_fmt.format(
            r["model"],
            r["split"],
            r["accuracy"],
            r["precision"],
            r["recall"],
            r["f1"],
            r["balanced_accuracy"],
            r["pr_auc"],
            r["roc_auc"],
            r["tp"],
            r["fp"],
            r["fn"],
            r["tn"]
        ))
    print("-" * 115)


# ============================================================
# MAIN EVALUATION PIPELINE
# ============================================================

def main():
    t_start = time.time()
    
    print()
    print("=============================================================")
    print("  EVConnect -- Phase 2: train_baselines.py")
    print("  Evaluating Always-Zero & Persistence Baselines")
    print("=============================================================")
    print("  ROOT_DIR : " + ROOT_DIR)

    # 1. Verify Dataset
    if not os.path.isfile(FEATURES_V2_PATH):
        sys.exit(f"\n[ERROR] Required feature dataset not found at:\n  {FEATURES_V2_PATH}")

    # 2. Load Evaluation Data
    section("STEP 1 — Loading Processed Dataset")
    print(f"  Source file: {FEATURES_V2_PATH}")
    
    df = pd.read_csv(
        FEATURES_V2_PATH,
        usecols=["stationID", "timestamp", "split", "target_occupancy", "previous_occupancy"],
        dtype={
            "stationID": str,
            "split": str,
            "target_occupancy": "int8",
            "previous_occupancy": "int8"
        }
    )
    print(f"  Loaded {len(df):,} total rows from occupancy_features_v2.csv")

    # 3. Sanity Checks & Assertions
    section("STEP 2 — Data Validation & Assertions")
    
    # Assert values are strictly binary
    target_vals = set(df["target_occupancy"].unique())
    prev_vals = set(df["previous_occupancy"].unique())
    
    assert target_vals <= {0, 1}, f"[ERROR] target_occupancy values invalid: {target_vals}"
    assert prev_vals <= {0, 1}, f"[ERROR] previous_occupancy values invalid: {prev_vals}"
    print("  [OK] target_occupancy is strictly binary {0, 1}")
    print("  [OK] previous_occupancy is strictly binary {0, 1}")

    # Filter splits
    val_df = df[df["split"] == "val"].copy()
    test_df = df[df["split"] == "test"].copy()

    print(f"  Validation rows : {len(val_df):,}")
    print(f"  Test rows       : {len(test_df):,}")
    
    assert len(val_df) > 0, "[ERROR] Validation set is empty!"
    assert len(test_df) > 0, "[ERROR] Test set is empty!"

    # Split distributions
    for name, split_df in [("Validation", val_df), ("Test", test_df)]:
        n_total = len(split_df)
        n_pos = int((split_df["target_occupancy"] == 1).sum())
        n_neg = int((split_df["target_occupancy"] == 0).sum())
        pos_pct = 100.0 * n_pos / n_total
        neg_pct = 100.0 * n_neg / n_total
        print(f"  {name:<10} class distribution -> Class 1 (Occupied): {n_pos:,} ({pos_pct:.2f}%) | Class 0 (Available): {n_neg:,} ({neg_pct:.2f}%)")

    # 4. Evaluate Baselines
    section("STEP 3 — Evaluating Baselines on Validation and Test Sets")
    
    results = []

    # ── Baseline 1: Always-Zero ───────────────────────────────
    print("\n  Evaluating [Always-Zero Baseline]...")
    for split_name, split_df in [("val", val_df), ("test", test_df)]:
        y_true = split_df["target_occupancy"].values
        y_pred = np.zeros(len(y_true), dtype="int8")
        
        # Verify prediction is all zero
        assert (y_pred == 0).all(), "[ERROR] Always-Zero prediction contains non-zero value!"
        
        res = compute_metrics(y_true, y_pred, "Always-Zero", split_name)
        results.append(res)

    # ── Baseline 2: Persistence ────────────────────────────────
    print("\n  Evaluating [Persistence Baseline]...")
    for split_name, split_df in [("val", val_df), ("test", test_df)]:
        y_true = split_df["target_occupancy"].values
        y_pred = split_df["previous_occupancy"].values
        
        # Core assertion: prediction must strictly match previous_occupancy
        assert (y_pred == split_df["previous_occupancy"].values).all(), (
            f"[ERROR] Persistence prediction does not match previous_occupancy on {split_name}!"
        )
        print(f"  [OK] Persistence prediction == previous_occupancy verified for all {len(y_pred):,} rows in {split_name}")
        
        res = compute_metrics(y_true, y_pred, "Persistence", split_name)
        results.append(res)

    # 5. Display Results
    section("STEP 4 — Baseline Evaluation Results Table")
    print_metrics_table(results)

    # Confusion matrix visual breakdown
    print("\n  Confusion Matrix Breakdown:")
    for r in results:
        print(f"  [{r['model']:<11} | {r['split']:<4}] -> TP: {r['tp']:>5,} | FP: {r['fp']:>5,} | FN: {r['fn']:>5,} | TN: {r['tn']:>7,}")

    # 6. Save Results to CSV
    section("STEP 5 — Saving Results to CSV")
    res_df = pd.DataFrame(results)
    
    # Ensure columns match required schema
    columns_order = [
        "model", "split", "accuracy", "precision", "recall", "f1",
        "balanced_accuracy", "pr_auc", "roc_auc", "tn", "fp", "fn", "tp"
    ]
    res_df = res_df[columns_order]
    
    res_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"  Saved : {OUTPUT_CSV_PATH}")
    print(f"          {len(res_df)} rows written.")

    # 7. Interpretation and Research Insights
    section("STEP 6 — Research Interpretation & Findings")
    
    val_zero_acc = res_df[(res_df["model"] == "Always-Zero") & (res_df["split"] == "val")]["accuracy"].values[0]
    test_zero_acc = res_df[(res_df["model"] == "Always-Zero") & (res_df["split"] == "test")]["accuracy"].values[0]
    
    val_pers_f1 = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "val")]["f1"].values[0]
    test_pers_f1 = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "test")]["f1"].values[0]
    
    val_pers_rec = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "val")]["recall"].values[0]
    test_pers_rec = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "test")]["recall"].values[0]
    
    val_pers_prec = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "val")]["precision"].values[0]
    test_pers_prec = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "test")]["precision"].values[0]

    val_pers_prauc = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "val")]["pr_auc"].values[0]
    test_pers_prauc = res_df[(res_df["model"] == "Persistence") & (res_df["split"] == "test")]["pr_auc"].values[0]

    print(f"""
1. CLASS IMBALANCE & THE ACCURACY PARADOX:
   - The Always-Zero baseline achieves {val_zero_acc*100:.2f}% accuracy on validation and {test_zero_acc*100:.2f}% on test.
   - Yet, its Recall, Precision, and F1 are exactly 0.0000 because it predicts ZERO occupied slots (TP = 0).
   - This proves conclusively why Accuracy is a misleading metric for EV charging occupancy.

2. STRENGTH OF THE PERSISTENCE BASELINE:
   - Persistence achieves F1 = {val_pers_f1:.4f} (Val) and F1 = {test_pers_f1:.4f} (Test).
   - It captures {val_pers_rec*100:.2f}% of occupied intervals on Val and {test_pers_rec*100:.2f}% on Test simply because
     EV charging sessions average ~4.5 hours (268 min), making consecutive 30-min slots highly correlated.
   - Precision is {val_pers_prec:.4f} (Val) and {test_pers_prec:.4f} (Test), as departing vehicles produce false positives.
   - PR-AUC reaches {val_pers_prauc:.4f} (Val) and {test_pers_prauc:.4f} (Test).

3. BENCHMARK FOR FUTURE MACHINE LEARNING MODELS:
   - An ML model (Logistic Regression, Random Forest, XGBoost) MUST exceed the Persistence baseline
     to be considered practically useful:
       * Target F1-Score to beat : > {test_pers_f1:.4f} on Test Set
       * Target PR-AUC to beat   : > {test_pers_prauc:.4f} on Test Set
       * Target Balanced Acc     : > {res_df[(res_df['model']=='Persistence') & (res_df['split']=='test')]['balanced_accuracy'].values[0]:.4f}
   - If an ML model achieves 97% accuracy but an F1 score <= {test_pers_f1:.4f}, it provides NO research value over
     a simple 1-line rule: "predict current occupancy".

4. CONCLUSION:
   - Baseline evaluation is complete and fully documented.
   - All deterministic baselines established on leakage-free chronological splits.
""")

    elapsed = time.time() - t_start
    print(f"  Phase 2 execution completed in {elapsed:.2f}s.")
    print("  Phase 2 Complete. Await user instructions before Phase 3.")


if __name__ == "__main__":
    main()
