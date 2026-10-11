const Station = require("../models/Station");


// Get all stations
const getStations = async (req, res) => {
    try {
        const stations = await Station.find()
            .sort({ stationId: 1 });

        res.json({
            count: stations.length,
            stations
        });

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Failed to fetch stations"
        });
    }
};


// Get one station
const getStationById = async (req, res) => {
    try {
        const station = await Station.findOne({
            stationId: req.params.stationId
        });

        if (!station) {
            return res.status(404).json({
                message: "Station not found"
            });
        }

        res.json(station);

    } catch (error) {
        console.error(error);

        res.status(500).json({
            message: "Failed to fetch station"
        });
    }
};


module.exports = {
    getStations,
    getStationById
};