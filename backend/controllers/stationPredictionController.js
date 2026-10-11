const Station = require("../models/Station");

const {
    predictBatch
} = require("../services/mlService");


const ML_API_URL =
    process.env.ML_API_URL ||
    "http://localhost:8000";


const getLatestTimestamp = async () => {

    const response = await fetch(
        `${ML_API_URL}/latest-timestamp`
    );


    if (!response.ok) {

        const errorText =
            await response.text();

        throw new Error(
            `Failed to get latest timestamp: ${errorText}`
        );
    }


    const data =
        await response.json();


    if (!data.timestamp) {

        throw new Error(
            "Latest timestamp was not returned by ML service"
        );
    }


    return data.timestamp;
};


const getStationPredictions = async (
    req,
    res
) => {

    try {

        /*
         * Get all stations
         */

        const stations =
            await Station.find()
                .sort({
                    stationId: 1
                });


        if (stations.length === 0) {

            return res.json({

                count: 0,

                stations: []

            });
        }


        /*
         * Use timestamp supplied by the user
         * only when explicitly provided.
         *
         * Otherwise get the latest valid
         * timestamp from FastAPI.
         */

        const timestamp =
            req.query.timestamp ||
            await getLatestTimestamp();


        /*
         * Prepare batch prediction input
         */

        const predictionInput =
            stations.map(
                (station) => ({

                    station_id:
                        station.stationId,

                    timestamp

                })
            );


        /*
         * Call FastAPI once for all stations
         */

        const predictionResult =
            await predictBatch(
                predictionInput
            );


        /*
         * Convert predictions into a Map
         */

        const predictionMap =
            new Map(

                predictionResult.predictions.map(
                    (prediction) => [

                        prediction.station_id,

                        prediction

                    ]
                )

            );


        /*
         * Combine MongoDB station data
         * with ML prediction data
         */

        const result =
            stations.map(
                (station) => {

                    const prediction =
                        predictionMap.get(
                            station.stationId
                        );

                    const occupancyProbability =
                        Number(
                            prediction
                                ?.occupancy_probability
                        );

                    const availabilityProbability =
                        Number(
                            prediction
                                ?.availability_probability
                        );

                    const availabilityScore =
                        (Number.isFinite(
                            availabilityProbability
                        )
                            ? availabilityProbability
                            : 0) * 100;

                    const statusScore =
                        prediction?.status === "available"
                            ? 100
                            : 0;

                    const predictionScore =
                        (1 -
                            (Number.isFinite(
                                occupancyProbability
                            )
                                ? occupancyProbability
                                : 0)) * 100;

                    const recommendationScore =
                        Number(
                            (
                                availabilityScore * 0.60 +
                                statusScore * 0.25 +
                                predictionScore * 0.15
                            ).toFixed(1)
                        );


                    return {

                        stationId:
                            station.stationId,

                        name:
                            station.name,

                        siteId:
                            station.siteId,

                        spaceId:
                            station.spaceId,

                        connectorType:
                            station.connectorType,

                        totalConnectors:
                            station.totalConnectors,

                        prediction:
                            prediction?.prediction ??
                            null,

                        status:
                            prediction?.status ??
                            "unknown",

                        occupancyProbability:
                            Number.isFinite(
                                occupancyProbability
                            )
                                ? occupancyProbability
                                : null,

                        availabilityProbability:
                            Number.isFinite(
                                availabilityProbability
                            )
                                ? availabilityProbability
                                : null,

                        predictionHorizonMinutes:
                            prediction
                                ?.prediction_horizon_minutes ??
                            30,

                        recommendationScore

                    };

                }
            );


        result.sort(
            (a, b) =>
                b.recommendationScore -
                a.recommendationScore ||
                a.stationId.localeCompare(
                    b.stationId
                )
        );

        const rankedResult =
            result.map(
                (station, index) => ({
                    ...station,
                    recommendationRank: index + 1
                })
            );


        /*
         * Send response
         */

        res.json({

            count:
                rankedResult.length,

            timestamp,

            stations:
                rankedResult

        });

    } catch (error) {

        console.error(
            "Station prediction error:",
            error
        );


        res.status(500).json({

            message:
                "Failed to generate station predictions"

        });

    }

};


module.exports = {

    getStationPredictions

};
