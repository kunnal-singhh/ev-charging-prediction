"""
build_features.py
=================
Phase 1 — Reproducible Feature Engineering Pipeline

Project : Machine Learning-Based Prediction of EV Charging Station
          Occupancy and Demand Using ACN-Data

Purpose : Build the research feature set from the raw processed CSVs.
          Outputs three artefacts:
            1. data/processed/station_hour_rates_train.csv
               — station x local_hour occupancy rates (training data only)
            2. data/processed/station_session_stats_train.csv
               — per-station average session duration (training data only)
            3. data/processed/occupancy_features_v2.csv
               — full feature dataset with split labels for model training

Chronological split
-------------------
    TRAIN      : 2019-10-10 -> 2021-06-30 (inclusive, UTC midnight)
    VALIDATION : 2021-07-01 -> 2021-08-14 (inclusive, UTC midnight)
    TEST       : 2021-08-15 -> 2021-09-14 (inclusive)

Feature categories
------------------
    1. TEMPORAL               — local_hour, local_day_of_week, is_weekend, month
    2. HISTORICAL OCCUPANCY   — previous_occupancy, occupancy_1hr_ago,
                                occupancy_2hr_ago, rolling_2hr_occupancy
    3. STATION OPERATIONAL    — station_hour_occupancy_rate
    4. SESSION / CHARGING     — station_avg_session_duration

Leakage policy
--------------
    All aggregate features (categories 3 and 4) are computed on TRAINING
    DATA ONLY and frozen before being joined to validation / test rows.
    The script verifies this with explicit assertions.

    Lag features use only timestamps strictly before T.
    The target uses T + 30 min (the next row in the regular grid).

Storage decision
----------------
    The base occupancy grid is 1,861,585 rows x 5 cols ~92 MB.
    occupancy_features_v2.csv adds ~10 columns and is expected to be
    ~200-220 MB — similar to the existing occupancy_features.csv (180 MB).
    This size is acceptable for a local research pipeline.
    The two lookup tables are tiny (<= 1,500 rows each) and are saved
    separately so they can be audited, reused, and joined independently
    without re-running the full pipeline.

Usage
-----
    python src/features/build_features.py

    Run from the project root directory.

Author  : EVConnect Minor Project Team
Version : 1.0.0
"""

import os
import sys
import time

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OCCUPANCY_GRID_PATH = os.path.join(ROOT_DIR, "data", "processed", "station_occupancy_30min.csv")
SESSIONS_PATH       = os.path.join(ROOT_DIR, "data", "processed", "acn_sessions_basic.csv")

OUTPUT_DIR           = os.path.join(ROOT_DIR, "data", "processed")
HOUR_RATES_OUT       = os.path.join(OUTPUT_DIR, "station_hour_rates_train.csv")
SESSION_STATS_OUT    = os.path.join(OUTPUT_DIR, "station_session_stats_train.csv")
FEATURES_V2_OUT      = os.path.join(OUTPUT_DIR, "occupancy_features_v2.csv")

LOCAL_TZ = "America/Los_Angeles"

TRAIN_END_UTC  = pd.Timestamp("2021-06-30 23:59:59", tz="UTC")
VAL_START_UTC  = pd.Timestamp("2021-07-01 00:00:00", tz="UTC")
VAL_END_UTC    = pd.Timestamp("2021-08-14 23:59:59", tz="UTC")
TEST_START_UTC = pd.Timestamp("2021-08-15 00:00:00", tz="UTC")

LAG_1_STEPS  = 1
LAG_2_STEPS  = 2
LAG_3_STEPS  = 3
LAG_4_STEPS  = 4
TARGET_STEPS = -1


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print()
    print("=" * 60)
    print("  " + title)
    print("=" * 60)


def assert_no_future_in_aggregate(agg_source_timestamps, split_boundary, agg_name):
    future_rows = (agg_source_timestamps > split_boundary).sum()
    if future_rows > 0:
        sys.exit(
            "\n[LEAKAGE DETECTED] '{}' was computed using "
            "{} rows whose timestamp exceeds the training "
            "boundary {}. Aborting.".format(agg_name, future_rows, split_boundary)
        )
    print("  [LEAKAGE CHECK PASSED] '{}' — all source rows <= {}".format(
        agg_name, split_boundary.date()))


# ============================================================
# STEP 1 — LOAD OCCUPANCY GRID
# ============================================================

def load_occupancy_grid(path):
    section("STEP 1 — Loading occupancy grid")
    print("  Path : " + path)

    df = pd.read_csv(
        path,
        usecols=["stationID", "timestamp", "occupied"],
        dtype={"stationID": str, "occupied": "int8"},
    )

    print("  Raw rows loaded : {:,}".format(len(df)))

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["stationID", "timestamp"]).reset_index(drop=True)

    print("  Unique stations : {}".format(df["stationID"].nunique()))
    print("  Date range (UTC): {} -> {}".format(df["timestamp"].min(), df["timestamp"].max()))
    print("  occupied=1 total: {:,}".format(df["occupied"].sum()))
    print("  occupied=0 total: {:,}".format((df["occupied"] == 0).sum()))

    return df


# ============================================================
# STEP 2 — TEMPORAL FEATURES
# ============================================================

def add_temporal_features(df):
    section("STEP 2 — Deriving temporal features (local time)")

    local_ts = df["timestamp"].dt.tz_convert(LOCAL_TZ)

    df["local_timestamp"]   = local_ts
    df["local_hour"]        = local_ts.dt.hour.astype("int8")
    df["local_day_of_week"] = local_ts.dt.dayofweek.astype("int8")
    df["is_weekend"]        = (local_ts.dt.dayofweek >= 5).astype("int8")
    df["month"]             = local_ts.dt.month.astype("int8")

    print("  local_hour range       : {} - {}".format(
        df["local_hour"].min(), df["local_hour"].max()))
    print("  local_day_of_week range: {} - {}".format(
        df["local_day_of_week"].min(), df["local_day_of_week"].max()))
    print("  is_weekend sum         : {:,}".format(int(df["is_weekend"].sum())))
    print("  month unique values    : {}".format(sorted(df["month"].unique())))

    return df


# ============================================================
# STEP 3 — CHRONOLOGICAL SPLIT LABELS
# ============================================================

def add_split_labels(df):
    section("STEP 3 — Assigning chronological split labels")

    conditions = [
        df["timestamp"] <= TRAIN_END_UTC,
        (df["timestamp"] >= VAL_START_UTC) & (df["timestamp"] <= VAL_END_UTC),
        df["timestamp"] >= TEST_START_UTC,
    ]
    choices = ["train", "val", "test"]
    df["split"] = np.select(conditions, choices, default="discard")

    counts = df["split"].value_counts()
    for label in ["train", "val", "test", "discard"]:
        n = int(counts.get(label, 0))
        pct = 100.0 * n / len(df)
        print("  {:<8}: {:>10,} rows  ({:.2f}%)".format(label, n, pct))

    discarded = int((df["split"] == "discard").sum())
    assert discarded == 0, "[ERROR] {} rows fell outside all split windows.".format(discarded)
    print("  [OK] No rows discarded — split windows cover entire dataset.")

    return df


# ============================================================
# STEP 4 — HISTORICAL LAG FEATURES
# ============================================================

def add_lag_features(df):
    section("STEP 4 — Computing historical occupancy lag features")

    grp = df.groupby("stationID", sort=False)["occupied"]

    df["previous_occupancy"]     = grp.shift(LAG_1_STEPS)
    df["occupancy_1hr_ago"]      = grp.shift(LAG_2_STEPS)
    df["occupancy_2hr_ago"]      = grp.shift(LAG_4_STEPS)

    lag1 = grp.shift(LAG_1_STEPS)
    lag2 = grp.shift(LAG_2_STEPS)
    lag3 = grp.shift(LAG_3_STEPS)
    lag4 = grp.shift(LAG_4_STEPS)
    df["rolling_2hr_occupancy"]  = (lag1 + lag2 + lag3 + lag4) / 4.0

    df["target_occupancy"] = grp.shift(TARGET_STEPS)

    print("  Rows before dropping NaNs : {:,}".format(len(df)))

    lag_cols   = ["previous_occupancy", "occupancy_1hr_ago",
                  "occupancy_2hr_ago", "rolling_2hr_occupancy"]
    drop_mask  = df[lag_cols + ["target_occupancy"]].isna().any(axis=1)
    n_dropped  = int(drop_mask.sum())
    df = df[~drop_mask].copy()

    print("  Rows dropped (NaN lags/target): {:,}".format(n_dropped))
    print("  Rows remaining               : {:,}".format(len(df)))

    for col in lag_cols:
        df[col] = df[col].astype("int8")
    df["target_occupancy"]      = df["target_occupancy"].astype("int8")
    df["rolling_2hr_occupancy"] = df["rolling_2hr_occupancy"].astype("float32")

    sample_station = df["stationID"].iloc[10]
    ss = df[df["stationID"] == sample_station].head(5)
    print("  Lag alignment spot check (station {}):".format(sample_station))
    print("    occupied[0:5]          : {}".format(ss["occupied"].tolist()))
    print("    previous_occupancy[0:5]: {}".format(ss["previous_occupancy"].tolist()))

    return df


# ============================================================
# STEP 5 — STATION-HOUR OCCUPANCY RATE
# ============================================================

def build_station_hour_rates(df):
    section("STEP 5 — Building station-hour occupancy rate (train only)")

    train_mask = df["split"] == "train"
    train_df   = df[train_mask].copy()

    print("  Training rows used for aggregation: {:,}".format(len(train_df)))

    assert_no_future_in_aggregate(
        train_df["timestamp"], TRAIN_END_UTC, "station_hour_occupancy_rate"
    )

    hour_rates = (
        train_df.groupby(["stationID", "local_hour"])["occupied"]
        .mean()
        .rename("station_hour_occupancy_rate")
        .reset_index()
    )

    print("  (station, hour) combinations computed: {:,}".format(len(hour_rates)))
    print("  Possible max (55 stations x 24 hours) : {}".format(55 * 24))
    print("  Rate range: {:.4f} - {:.4f}".format(
        hour_rates["station_hour_occupancy_rate"].min(),
        hour_rates["station_hour_occupancy_rate"].max()))

    station_fallback = (
        train_df.groupby("stationID")["occupied"]
        .mean()
        .rename("station_fallback_rate")
        .reset_index()
    )

    global_fallback = float(train_df["occupied"].mean())
    print("  Global training occupancy rate (ultimate fallback): {:.6f}".format(global_fallback))

    df = df.merge(
        hour_rates[["stationID", "local_hour", "station_hour_occupancy_rate"]],
        on=["stationID", "local_hour"],
        how="left",
    )

    unseen_combos = int(df["station_hour_occupancy_rate"].isna().sum())
    if unseen_combos > 0:
        print("  [INFO] {:,} rows have unseen (station, hour) combos. "
              "Applying station-level fallback.".format(unseen_combos))
        df = df.merge(station_fallback, on="stationID", how="left")
        df["station_hour_occupancy_rate"] = df["station_hour_occupancy_rate"].fillna(
            df["station_fallback_rate"]
        )
        df.drop(columns=["station_fallback_rate"], inplace=True, errors="ignore")
    else:
        print("  [OK] All (station, hour) combinations present in training data.")

    remaining_nan = int(df["station_hour_occupancy_rate"].isna().sum())
    if remaining_nan > 0:
        print("  [INFO] {:,} rows still NaN after station fallback. "
              "Applying global fallback.".format(remaining_nan))
        df["station_hour_occupancy_rate"] = df["station_hour_occupancy_rate"].fillna(
            global_fallback
        )

    df["station_hour_occupancy_rate"] = df["station_hour_occupancy_rate"].astype("float32")

    final_nan = int(df["station_hour_occupancy_rate"].isna().sum())
    assert final_nan == 0, \
        "[ERROR] station_hour_occupancy_rate still has {:,} NaN values.".format(final_nan)
    print("  [OK] station_hour_occupancy_rate: 0 NaN values in final dataset.")

    return df, hour_rates[["stationID", "local_hour", "station_hour_occupancy_rate"]]


# ============================================================
# STEP 6 — STATION AVERAGE SESSION DURATION
# ============================================================

def build_session_stats(df):
    section("STEP 6 — Building station average session duration (train only)")

    sessions = pd.read_csv(
        SESSIONS_PATH,
        usecols=["stationID", "connectionTime", "session_duration_minutes"],
        dtype={"stationID": str},
    )
    sessions["connectionTime"] = pd.to_datetime(sessions["connectionTime"], utc=True)

    print("  Total sessions loaded     : {:,}".format(len(sessions)))
    print("  Sessions with NaN duration: {:,}".format(
        int(sessions["session_duration_minutes"].isna().sum())))

    train_sessions = sessions[sessions["connectionTime"] <= TRAIN_END_UTC].copy()
    print("  Sessions in training period: {:,}".format(len(train_sessions)))

    assert_no_future_in_aggregate(
        train_sessions["connectionTime"], TRAIN_END_UTC, "station_avg_session_duration"
    )

    n_before = len(train_sessions)
    train_sessions = train_sessions.dropna(subset=["session_duration_minutes"])
    n_after = len(train_sessions)
    if n_before > n_after:
        print("  [INFO] Dropped {:,} sessions with NaN duration.".format(n_before - n_after))

    global_mean_duration = float(train_sessions["session_duration_minutes"].mean())
    print("  Global training mean session duration: {:.2f} min".format(global_mean_duration))

    station_stats = (
        train_sessions.groupby("stationID")["session_duration_minutes"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "station_avg_session_duration",
                         "count": "session_count_train"})
        .reset_index()
    )
    station_stats["station_avg_session_duration"] = (
        station_stats["station_avg_session_duration"].astype("float32")
    )

    print("  Stations with session data: {} / {}".format(
        len(station_stats), df["stationID"].nunique()))
    print("  Duration range: {:.1f} - {:.1f} min".format(
        float(station_stats["station_avg_session_duration"].min()),
        float(station_stats["station_avg_session_duration"].max())))

    all_stations     = set(df["stationID"].unique())
    stations_with_s  = set(station_stats["stationID"].unique())
    missing_stations = all_stations - stations_with_s
    if missing_stations:
        print("  [INFO] {:,} station(s) have no training sessions — global fallback:".format(
            len(missing_stations)))
        for s in sorted(missing_stations):
            print("    " + s)

    df = df.merge(
        station_stats[["stationID", "station_avg_session_duration"]],
        on="stationID",
        how="left",
    )

    nan_count = int(df["station_avg_session_duration"].isna().sum())
    if nan_count > 0:
        print("  [INFO] Filling {:,} NaN values with global mean ({:.2f} min).".format(
            nan_count, global_mean_duration))
        df["station_avg_session_duration"] = df["station_avg_session_duration"].fillna(
            global_mean_duration
        )

    df["station_avg_session_duration"] = df["station_avg_session_duration"].astype("float32")

    final_nan = int(df["station_avg_session_duration"].isna().sum())
    assert final_nan == 0, \
        "[ERROR] station_avg_session_duration has {:,} NaN values after fallback.".format(final_nan)
    print("  [OK] station_avg_session_duration: 0 NaN values in final dataset.")

    return df, station_stats


# ============================================================
# STEP 7 — VALIDATION REPORT
# ============================================================

def print_validation_report(df):
    section("STEP 7 — Validation Report")

    final_feature_cols = [
        "local_hour", "local_day_of_week", "is_weekend", "month",
        "previous_occupancy", "occupancy_1hr_ago", "occupancy_2hr_ago",
        "rolling_2hr_occupancy", "station_hour_occupancy_rate",
        "station_avg_session_duration", "target_occupancy",
    ]

    print("  Total output rows        : {:,}".format(len(df)))
    print("  Unique stationIDs        : {}".format(df["stationID"].nunique()))
    print("  Feature columns          : {}".format(len(final_feature_cols)))
    print("  All columns in dataset   : {}".format(list(df.columns)))

    print()
    print("  -- Split Summary --------------------------------------------------")
    for label in ["train", "val", "test"]:
        split_df = df[df["split"] == label]
        n = len(split_df)
        ts_min = split_df["timestamp"].min()
        ts_max = split_df["timestamp"].max()
        n_pos  = int(split_df["target_occupancy"].sum())
        n_neg  = n - n_pos
        pct_pos = 100.0 * n_pos / n if n > 0 else 0
        print("  {:<5}: {:>10,} rows | {} -> {} | target=1: {:,} ({:.2f}%) | target=0: {:,} ({:.2f}%)".format(
            label.upper(), n, ts_min.date(), ts_max.date(),
            n_pos, pct_pos, n_neg, 100.0 - pct_pos))

    print()
    print("  -- Missing Value Report -------------------------------------------")
    for col in final_feature_cols:
        n_nan = int(df[col].isna().sum())
        status = "[OK]" if n_nan == 0 else "[WARNING — {:,} NaN]".format(n_nan)
        print("  {:<32} {}".format(status, col))

    print()
    print("  -- Dtype Report ---------------------------------------------------")
    for col in final_feature_cols:
        print("  {:<35}: {}".format(col, df[col].dtype))


# ============================================================
# STEP 8 — LEAKAGE ASSERTIONS
# ============================================================

def run_leakage_assertions(df):
    section("STEP 8 — Leakage Assertions")

    target_vals = set(df["target_occupancy"].unique())
    assert target_vals <= {0, 1}, \
        "[LEAKAGE] target_occupancy contains unexpected values: {}".format(target_vals)
    print("  [OK] target_occupancy is strictly binary {0, 1}")

    prev_vals = set(df["previous_occupancy"].unique())
    assert prev_vals <= {0, 1}, \
        "[LEAKAGE] previous_occupancy contains values outside {0,1}: {}".format(prev_vals)
    print("  [OK] previous_occupancy is strictly binary {0, 1}")

    roll_min = float(df["rolling_2hr_occupancy"].min())
    roll_max = float(df["rolling_2hr_occupancy"].max())
    assert 0.0 <= roll_min and roll_max <= 1.0, \
        "[LEAKAGE] rolling_2hr_occupancy out of [0,1]: min={}, max={}".format(roll_min, roll_max)
    print("  [OK] rolling_2hr_occupancy in [0,1]  (actual: [{:.3f}, {:.3f}])".format(
        roll_min, roll_max))

    rate_min = float(df["station_hour_occupancy_rate"].min())
    rate_max = float(df["station_hour_occupancy_rate"].max())
    assert 0.0 <= rate_min and rate_max <= 1.0, \
        "[LEAKAGE] station_hour_occupancy_rate out of [0,1]: min={}, max={}".format(
            rate_min, rate_max)
    print("  [OK] station_hour_occupancy_rate in [0,1]  (actual: [{:.4f}, {:.4f}])".format(
        rate_min, rate_max))

    dur_min = float(df["station_avg_session_duration"].min())
    assert dur_min > 0, \
        "[LEAKAGE / ERROR] station_avg_session_duration has non-positive value: {}".format(dur_min)
    print("  [OK] station_avg_session_duration > 0 for all rows  (min: {:.2f} min)".format(dur_min))

    train_rates = (
        df[df["split"] == "train"]
        .groupby(["stationID", "local_hour"])["station_hour_occupancy_rate"]
        .first()
    )
    val_test_df = df[df["split"].isin(["val", "test"])].copy()
    val_test_agg = val_test_df.groupby(
        ["stationID", "local_hour"])["station_hour_occupancy_rate"].first()

    mismatch = 0
    for idx, val_rate in val_test_agg.items():
        if idx in train_rates.index:
            train_rate = float(train_rates.loc[idx])
            if abs(float(val_rate) - train_rate) > 1e-4:
                mismatch += 1
    assert mismatch == 0, \
        "[LEAKAGE] {:,} (station, hour) combos in val/test differ from training lookup.".format(
            mismatch)
    print("  [OK] Val/test station_hour_occupancy_rate values match training lookup exactly")

    print("  [OK] station_hour_occupancy_rate — training data only (verified in Step 5)")
    print("  [OK] station_avg_session_duration — training sessions only (verified in Step 6)")
    print()
    print("  == ALL LEAKAGE ASSERTIONS PASSED ==")


# ============================================================
# STEP 9 — SAVE OUTPUTS
# ============================================================

def save_outputs(df, hour_rates, session_stats):
    section("STEP 9 — Saving output artefacts")

    hour_rates_out = hour_rates.sort_values(["stationID", "local_hour"])
    hour_rates_out.to_csv(HOUR_RATES_OUT, index=False)
    size_kb = os.path.getsize(HOUR_RATES_OUT) / 1024
    print("  Saved : " + HOUR_RATES_OUT)
    print("          {:,} rows | {:.1f} KB".format(len(hour_rates_out), size_kb))

    session_stats_out = session_stats.sort_values("stationID")
    session_stats_out.to_csv(SESSION_STATS_OUT, index=False)
    size_kb = os.path.getsize(SESSION_STATS_OUT) / 1024
    print("  Saved : " + SESSION_STATS_OUT)
    print("          {:,} rows | {:.1f} KB".format(len(session_stats_out), size_kb))

    output_cols = [
        "stationID", "timestamp", "occupied", "split",
        "local_hour", "local_day_of_week", "is_weekend", "month",
        "previous_occupancy", "occupancy_1hr_ago", "occupancy_2hr_ago",
        "rolling_2hr_occupancy",
        "station_hour_occupancy_rate",
        "station_avg_session_duration",
        "target_occupancy",
    ]

    df_out = df[output_cols]
    print("  Writing features_v2.csv ({:,} rows x {} columns)...".format(
        len(df_out), len(output_cols)))
    t0 = time.time()
    df_out.to_csv(FEATURES_V2_OUT, index=False)
    elapsed = time.time() - t0
    size_mb = os.path.getsize(FEATURES_V2_OUT) / (1024 * 1024)
    print("  Saved : " + FEATURES_V2_OUT)
    print("          {:,} rows | {:.1f} MB | {:.1f}s".format(len(df_out), size_mb, elapsed))

    print()
    print("  -- Output Column Order --------------------------------------------")
    for i, col in enumerate(output_cols, 1):
        print("  {:>2}. {}".format(i, col))


# ============================================================
# STEP 10 — FINAL SUMMARY
# ============================================================

def print_final_summary(df, t_start):
    section("STEP 10 — Final Summary")
    elapsed = time.time() - t_start
    print("  Total pipeline runtime       : {:.1f}s".format(elapsed))
    print("  Input rows (occupancy grid)  : 1,861,585  (station_occupancy_30min.csv)")
    print("  Output rows (features_v2)    : {:,}".format(len(df)))
    print()
    for label in ["train", "val", "test"]:
        sub = df[df["split"] == label]
        n_pos = int(sub["target_occupancy"].sum())
        n = len(sub)
        print("  {:<5}: {:>10,} rows | target=1: {:>6,} ({:.2f}%)".format(
            label.upper(), n, n_pos, 100.0 * n_pos / n))
    print()
    print("  Recommended model training feature set:")
    for f in ["local_hour", "local_day_of_week", "is_weekend", "month",
              "previous_occupancy", "rolling_2hr_occupancy",
              "station_hour_occupancy_rate", "station_avg_session_duration"]:
        print("    - " + f)
    print()
    print("  Also available for ablation experiments:")
    print("    - occupancy_1hr_ago")
    print("    - occupancy_2hr_ago")
    print()
    print("  Phase 1 Complete.")
    print("  Await user review before proceeding to Phase 2 (model training).")


# ============================================================
# MAIN
# ============================================================

def main():
    t_start = time.time()
    print()
    print("=============================================================")
    print("  EVConnect -- Phase 1: build_features.py")
    print("  Feature Engineering Pipeline (Leakage-Safe)")
    print("=============================================================")
    print("  ROOT_DIR : " + ROOT_DIR)

    for path in [OCCUPANCY_GRID_PATH, SESSIONS_PATH]:
        if not os.path.isfile(path):
            sys.exit("\n[ERROR] Required input file not found:\n  " + path)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = load_occupancy_grid(OCCUPANCY_GRID_PATH)
    df = add_temporal_features(df)
    df = add_split_labels(df)
    df = add_lag_features(df)
    df, hour_rates    = build_station_hour_rates(df)
    df, session_stats = build_session_stats(df)

    print_validation_report(df)
    run_leakage_assertions(df)
    save_outputs(df, hour_rates, session_stats)
    print_final_summary(df, t_start)


if __name__ == "__main__":
    main()
