const express = require("express");

const {
    getStations,
    getStationById
} = require("../controllers/stationController");

const router = express.Router();


// GET /api/stations
router.get("/", getStations);


// GET /api/stations/:stationId
router.get("/:stationId", getStationById);


module.exports = router;