const Station = require("../models/Station");
const { predictBatch } = require("../services/mlService");

const ML_API_URL =
    process.env.ML_API_URL ||
    "http://localhost:8000";

const getLatestTimestamp = async () => {
    const response = await fetch(
        `${ML_API_URL}/latest-timestamp`
    );

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
            `Failed to get latest timestamp: ${errorText}`
        );
    }

    const data = await response.json();

    if (!data.timestamp) {
        throw new Error(
            "Latest timestamp was not returned by ML service"
        );
    }

    return data.timestamp;
};

const getSingleStationPrediction = async (req, res) => {
    try {
        const { stationId } = req.params;

        // Find station in MongoDB
        const station = await Station.findOne({
            stationId
        });

        if (!station) {
            return res.status(404).json({
                message: "Station not found"
            });
        }

        // Use query timestamp if provided, else get latest dataset timestamp from FastAPI
        const timestamp =
            req.query.timestamp ||
            (await getLatestTimestamp());

        // Ask ML service for prediction
        const result = await predictBatch([
            {
                station_id: stationId,
                timestamp
            }
        ]);

        const prediction = result.predictions[0];

        res.json({
            stationId: station.stationId,
            name: station.name,
            siteId: station.siteId,
            spaceId: station.spaceId,
            connectorType: station.connectorType,
            totalConnectors: station.totalConnectors,
            prediction: {
                prediction: prediction.prediction,
                status: prediction.status,
                occupancyProbability: prediction.occupancy_probability,
                availabilityProbability: prediction.availability_probability,
                predictionHorizonMinutes: prediction.prediction_horizon_minutes,
                horizonMinutes: prediction.prediction_horizon_minutes
            },
            timestamp
        });
    } catch (error) {
        console.error(
            "Single station prediction error:",
            error
        );

        res.status(500).json({
            message: "Failed to generate station prediction"
        });
    }
};

module.exports = {
    getSingleStationPrediction
};