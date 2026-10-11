import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "station_occupancy_30min.csv"
)

HOUR_RATES_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "station_hour_rates_train.csv"
)

SESSION_STATS_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "station_session_stats_train.csv"
)

# Training-derived global fallbacks (strictly <= 2021-06-30 UTC)
GLOBAL_HOUR_OCCUPANCY_RATE = 0.091185
GLOBAL_AVG_SESSION_DURATION = 164.55


# ---------------------------------------------------------
# Load occupancy grid ONCE when FastAPI starts
# ---------------------------------------------------------

print("Loading occupancy dataset...")

occupancy_df = pd.read_csv(
    CSV_PATH,
    usecols=[
        "stationID",
        "timestamp",
        "occupied"
    ]
)

occupancy_df["timestamp"] = pd.to_datetime(
    occupancy_df["timestamp"],
    utc=True
)

occupancy_df = occupancy_df.dropna(
    subset=[
        "stationID",
        "timestamp",
        "occupied"
    ]
)

occupancy_df = occupancy_df.set_index(
    ["stationID", "timestamp"]
).sort_index()

# Cache the latest timestamp from the loaded dataset
_LATEST_TIMESTAMP = occupancy_df.index.get_level_values(
    "timestamp"
).max()

print(
    f"Occupancy dataset loaded: "
    f"{len(occupancy_df):,} records"
)


def get_latest_timestamp():
    """
    Return the latest UTC timestamp present in the
    occupancy dataset.  Computed once at startup to
    avoid re-scanning the DataFrame on every request.
    """
    return _LATEST_TIMESTAMP


# ---------------------------------------------------------
# Load Station-Hour Occupancy Rates (Training Data Only)
# ---------------------------------------------------------

print("Loading station-hour rates lookup table...")

hour_rates_df = pd.read_csv(
    HOUR_RATES_PATH,
    dtype={"stationID": str, "local_hour": int, "station_hour_occupancy_rate": float}
)

# Dict for fast (stationID, local_hour) -> rate lookup
hour_rates_dict = {
    (row["stationID"], int(row["local_hour"])): float(row["station_hour_occupancy_rate"])
    for _, row in hour_rates_df.iterrows()
}

# Station-level fallback rates
station_fallback_dict = (
    hour_rates_df.groupby("stationID")["station_hour_occupancy_rate"]
    .mean()
    .to_dict()
)

print(
    f"Station-hour rates loaded: "
    f"{len(hour_rates_dict):,} combinations across {len(station_fallback_dict)} stations"
)


# ---------------------------------------------------------
# Load Station Average Session Duration (Training Data Only)
# ---------------------------------------------------------

print("Loading station session stats lookup table...")

session_stats_df = pd.read_csv(
    SESSION_STATS_PATH,
    dtype={"stationID": str, "station_avg_session_duration": float}
)

session_stats_dict = {
    str(row["stationID"]): float(row["station_avg_session_duration"])
    for _, row in session_stats_df.iterrows()
}

print(
    f"Station session stats loaded: "
    f"{len(session_stats_dict):,} stations"
)


# ---------------------------------------------------------
# Lookup Functions for Operational / Session Features
# ---------------------------------------------------------

def get_station_hour_rate(station_id: str, local_hour: int) -> float:
    """
    Lookup historical occupancy rate for (stationID, local_hour).
    Falls back to station mean rate, then global training mean (0.091185).
    """
    key = (str(station_id), int(local_hour))
    if key in hour_rates_dict:
        return hour_rates_dict[key]
    
    # Station-level fallback
    if str(station_id) in station_fallback_dict:
        return float(station_fallback_dict[str(station_id)])
    
    # Global training fallback
    return GLOBAL_HOUR_OCCUPANCY_RATE


def get_station_avg_duration(station_id: str) -> float:
    """
    Lookup historical average session duration in minutes for stationID.
    Falls back to global training mean (164.55 minutes).
    """
    sid = str(station_id)
    if sid in session_stats_dict:
        return session_stats_dict[sid]
    
    # Global training fallback
    return GLOBAL_AVG_SESSION_DURATION


# ---------------------------------------------------------
# Get occupancy history
# ---------------------------------------------------------

def get_occupancy_history(
    station_id,
    timestamp
):

    timestamp = pd.Timestamp(
        timestamp,
        tz="UTC"
    )


    # Four previous 30-minute intervals
    history_times = [
        timestamp - pd.Timedelta(minutes=120),
        timestamp - pd.Timedelta(minutes=90),
        timestamp - pd.Timedelta(minutes=60),
        timestamp - pd.Timedelta(minutes=30)
    ]


    history = []


    for history_time in history_times:

        key = (
            station_id,
            history_time
        )

        try:

            value = occupancy_df.loc[
                key,
                "occupied"
            ]

            # Handle duplicate rows safely
            if isinstance(value, pd.Series):
                value = value.iloc[0]

            history.append(int(value))

        except KeyError:

            raise ValueError(
                f"No occupancy history found for "
                f"station '{station_id}' at "
                f"{history_time}."
            )


    return history


# ---------------------------------------------------------
# Get histories for multiple stations
# ---------------------------------------------------------

def get_batch_occupancy_history(
    station_ids,
    timestamp
):

    timestamp = pd.Timestamp(
        timestamp,
        tz="UTC"
    )


    history_times = [
        timestamp - pd.Timedelta(minutes=120),
        timestamp - pd.Timedelta(minutes=90),
        timestamp - pd.Timedelta(minutes=60),
        timestamp - pd.Timedelta(minutes=30)
    ]


    # Build MultiIndex for all requested stations/times
    lookup_keys = [
        (station_id, history_time)
        for station_id in station_ids
        for history_time in history_times
    ]


    lookup_index = pd.MultiIndex.from_tuples(
        lookup_keys,
        names=[
            "stationID",
            "timestamp"
        ]
    )


    values = occupancy_df.reindex(
        lookup_index
    )["occupied"]


    results = {}


    for station_id in station_ids:

        station_values = []

        for history_time in history_times:

            value = values.loc[
                (station_id, history_time)
            ]


            if pd.isna(value):

                raise ValueError(
                    f"No occupancy history found "
                    f"for station '{station_id}' "
                    f"at '{history_time}'."
                )


            station_values.append(
                int(value)
            )


        results[station_id] = station_values


    return results