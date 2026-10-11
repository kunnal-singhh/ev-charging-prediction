const express = require("express");

const {
    getStationPredictions
} = require("../controllers/stationPredictionController");

const router = express.Router();

router.get("/", getStationPredictions);

module.exports = router;