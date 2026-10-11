const express = require("express");

const {
    getSingleStationPrediction
} = require(
    "../controllers/singleStationPredictionController"
);

const router = express.Router();


router.get(
    "/:stationId/prediction",
    getSingleStationPrediction
);


module.exports = router;