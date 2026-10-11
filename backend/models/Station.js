const mongoose = require("mongoose");

const stationSchema = new mongoose.Schema(
    {
        stationId: {
            type: String,
            required: true,
            unique: true,
            index: true
        },

        name: {
            type: String,
            required: true
        },

        siteId: {
            type: String,
            default: "caltech"
        },

        latitude: {
            type: Number
        },

        longitude: {
            type: Number
        },

        connectorType: {
            type: String,
            default: "AC"
        },

        totalConnectors: {
            type: Number,
            default: 1
        },

        status: {
            type: String,
            enum: ["available", "occupied", "offline"],
            default: "available"
        },

        spaceId: {
            type: String,
            default: null
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model(
    "Station",
    stationSchema
);
