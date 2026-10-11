import pandas as pd
from api.occupancy_service import (
    get_station_hour_rate,
    get_station_avg_duration,
)


CALTECH_TIMEZONE = "America/Los_Angeles"


def create_features(
    station_id: str,
    timestamp: str,
    occupancy_history: list[int]
) -> dict:
    """
    Create the exact 8 features required by the Research Champion XGBoost model (Experiment D).

    occupancy_history must contain 4 values in chronological order:
      [0]: T-120 min
      [1]: T-90 min
      [2]: T-60 min
      [3]: T-30 min
    """

    if len(occupancy_history) != 4:
        raise ValueError(
            "occupancy_history must contain exactly 4 values."
        )

    if any(value not in [0, 1] for value in occupancy_history):
        raise ValueError(
            "occupancy_history values must be either 0 or 1."
        )

    # Convert input timestamp to Caltech local time
    timestamp_ts = pd.Timestamp(timestamp)

    if timestamp_ts.tzinfo is None:
        timestamp_ts = timestamp_ts.tz_localize("UTC")

    local_timestamp = timestamp_ts.tz_convert(CALTECH_TIMEZONE)

    # 1. Temporal Features
    local_hour = int(local_timestamp.hour)
    local_day_of_week = int(local_timestamp.dayofweek)
    is_weekend = int(local_day_of_week >= 5)
    month = int(local_timestamp.month)

    # 2. Historical Occupancy Lag Features (strictly before T)
    previous_occupancy = int(occupancy_history[3])  # T-30 min
    rolling_2hr_occupancy = float(sum(occupancy_history) / 4.0)  # Mean of [T-120, T-90, T-60, T-30]

    # 3. Station Operational Feature (training lookup with fallback)
    station_hour_occupancy_rate = float(get_station_hour_rate(station_id, local_hour))

    # 4. Session Characteristics Feature (training lookup with fallback)
    station_avg_session_duration = float(get_station_avg_duration(station_id))

    return {
        "local_hour": local_hour,
        "local_day_of_week": local_day_of_week,
        "is_weekend": is_weekend,
        "month": month,
        "previous_occupancy": previous_occupancy,
        "rolling_2hr_occupancy": rolling_2hr_occupancy,
        "station_hour_occupancy_rate": station_hour_occupancy_rate,
        "station_avg_session_duration": station_avg_session_duration,
    }