const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";


export async function getStationPredictions(timestamp = null) {

    const url = timestamp
        ? `${API_URL}/api/stations/predictions?timestamp=${encodeURIComponent(timestamp)}`
        : `${API_URL}/api/stations/predictions`;

    const response = await fetch(url);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message ||
            "Failed to get station predictions"
        );
    }

    return data;
}


export async function getStationPrediction(
    stationId,
    timestamp = null
) {
    const url = timestamp
        ? `${API_URL}/api/stations/${stationId}/prediction?timestamp=${encodeURIComponent(timestamp)}`
        : `${API_URL}/api/stations/${stationId}/prediction`;

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(
            "Failed to fetch station prediction"
        );
    }

    return await response.json();
}
