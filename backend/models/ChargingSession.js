const mongoose = require("mongoose");


const chargingSessionSchema = new mongoose.Schema(
    {
        userId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true
        },

        stationId: {
            type: String,
            required: true,
            trim: true
        },

        startTime: {
            type: Date,
            required: true
        },

        endTime: {
            type: Date,
            default: null
        },

        status: {
            type: String,
            enum: [
                "scheduled",
                "active",
                "completed",
                "cancelled"
            ],
            default: "scheduled"
        },

        energyConsumedKwh: {
            type: Number,
            default: 0,
            min: 0
        }
    },
    {
        timestamps: true
    }
);


module.exports = mongoose.model(
    "ChargingSession",
    chargingSessionSchema
);