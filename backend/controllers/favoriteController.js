const User = require("../models/User");


const getFavorites = async (req, res) => {

    try {

        const user = await User.findById(
            req.user._id
        ).select("favoriteStations");


        res.json({
            favorites:
                user.favoriteStations
        });

    } catch (error) {

        console.error(
            "Get favorites error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to get favorite stations"
        });
    }
};


const addFavorite = async (req, res) => {

    try {

        const { stationId } = req.params;


        if (!stationId) {

            return res.status(400).json({
                message:
                    "Station ID is required"
            });
        }


        const user = await User.findById(
            req.user._id
        );


        if (
            user.favoriteStations.includes(
                stationId
            )
        ) {

            return res.status(409).json({
                message:
                    "Station is already in favorites"
            });
        }


        user.favoriteStations.push(
            stationId
        );


        await user.save();


        res.status(201).json({

            message:
                "Station added to favorites",

            favorites:
                user.favoriteStations

        });

    } catch (error) {

        console.error(
            "Add favorite error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to add favorite station"
        });
    }
};


const removeFavorite = async (req, res) => {

    try {

        const { stationId } = req.params;


        const user = await User.findById(
            req.user._id
        );


        user.favoriteStations =
            user.favoriteStations.filter(
                (id) => id !== stationId
            );


        await user.save();


        res.json({

            message:
                "Station removed from favorites",

            favorites:
                user.favoriteStations

        });

    } catch (error) {

        console.error(
            "Remove favorite error:",
            error
        );

        res.status(500).json({
            message:
                "Failed to remove favorite station"
        });
    }
};


module.exports = {
    getFavorites,
    addFavorite,
    removeFavorite
};