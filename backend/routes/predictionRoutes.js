const express = require("express");

const {
    predictBatch
} = require("../services/mlService");

const router = express.Router();


router.post("/predict", async (req, res) => {

    try {

        const { predictions } = req.body;

        if (!Array.isArray(predictions)) {
            return res.status(400).json({
                message: "predictions must be an array"
            });
        }

        const result = await predictBatch(
            predictions
        );

        res.json(result);

    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );

        res.status(500).json({
            message: "ML prediction failed"
        });
    }
});


module.exports = router;