const ChargingSession =
    require("../models/ChargingSession");


// CREATE SESSION

const createSession = async (req, res) => {

    try {

        const {
            stationId,
            startTime
        } = req.body;


        if (!stationId || !startTime) {

            return res.status(400).json({
                message:
                    "stationId and startTime are required"
            });
        }


        const session =
            await ChargingSession.create({

                userId: req.user._id,

                stationId,

                startTime,

                status: "scheduled"

            });


        res.status(201).json({

            message:
                "Charging session created",

            session

        });

    } catch (error) {

        console.error(
            "Create session error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to create charging session"
        });
    }
};


// GET USER SESSIONS

const getSessions = async (req, res) => {

    try {

        const sessions =
            await ChargingSession
                .find({
                    userId: req.user._id
                })
                .sort({
                    startTime: -1
                });


        res.json({

            count: sessions.length,

            sessions

        });

    } catch (error) {

        console.error(
            "Get sessions error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to get charging sessions"
        });
    }
};


// GET SINGLE SESSION

const getSession = async (req, res) => {

    try {

        const session =
            await ChargingSession.findOne({

                _id: req.params.id,

                userId: req.user._id

            });


        if (!session) {

            return res.status(404).json({
                message:
                    "Charging session not found"
            });
        }


        res.json({
            session
        });

    } catch (error) {

        console.error(
            "Get session error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to get charging session"
        });
    }
};


// UPDATE SESSION

const updateSession = async (req, res) => {

    try {

        const {
            status,
            endTime,
            energyConsumedKwh
        } = req.body;


        const session =
            await ChargingSession.findOne({

                _id: req.params.id,

                userId: req.user._id

            });


        if (!session) {

            return res.status(404).json({
                message:
                    "Charging session not found"
            });
        }


        if (status !== undefined) {
            session.status = status;
        }


        if (endTime !== undefined) {
            session.endTime = endTime;
        }


        if (
            energyConsumedKwh !== undefined
        ) {
            session.energyConsumedKwh =
                energyConsumedKwh;
        }


        await session.save();


        res.json({

            message:
                "Charging session updated",

            session

        });

    } catch (error) {

        console.error(
            "Update session error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to update charging session"
        });
    }
};


module.exports = {
    createSession,
    getSessions,
    getSession,
    updateSession
};