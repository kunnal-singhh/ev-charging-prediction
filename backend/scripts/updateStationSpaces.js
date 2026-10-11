require("dotenv").config();

const fs = require("fs");
const path = require("path");
const mongoose = require("mongoose");

const connectDB = require("../config/db");
const Station = require("../models/Station");


const DATA_PATH = path.join(
    __dirname,
    "..",
    "data",
    "raw",
    "acn_data.json"
);


const updateStationSpaces = async () => {

    try {

        await connectDB();

        console.log(
            "Connected to MongoDB."
        );


        const rawData =
            fs.readFileSync(
                DATA_PATH,
                "utf-8"
            );


        const data =
            JSON.parse(rawData);


        const items =
            data._items || [];


        const stationSpaces = new Map();


        /*
         * Build:
         *
         * stationID -> spaceID
         */

        for (const item of items) {

            if (
                !item.stationID ||
                !item.spaceID
            ) {
                continue;
            }


            if (
                stationSpaces.has(
                    item.stationID
                )
            ) {

                const existingSpace =
                    stationSpaces.get(
                        item.stationID
                    );


                /*
                 * Each station should have
                 * exactly one space.
                 */

                if (
                    existingSpace !==
                    item.spaceID
                ) {

                    console.warn(
                        `Warning: Station ${item.stationID} ` +
                        `has multiple spaces: ` +
                        `${existingSpace}, ${item.spaceID}`
                    );

                }

                continue;
            }


            stationSpaces.set(
                item.stationID,
                item.spaceID
            );

        }


        console.log(
            `Found ${stationSpaces.size} station-space mappings.`
        );


        let updated = 0;

        const notFound = [];


        /*
         * Update MongoDB
         */

        for (
            const [
                stationId,
                spaceId
            ] of stationSpaces
        ) {

            const result =
                await Station.updateOne(
                    {
                        stationId
                    },
                    {
                        $set: {
                            spaceId
                        }
                    }
                );


            if (
                result.matchedCount === 0
            ) {

                console.warn(
                    `Station not found in MongoDB: ${stationId}`
                );

                notFound.push(stationId);

                continue;
            }


            updated++;


            console.log(
                `Updated ${stationId} → ${spaceId}`
            );

        }


        console.log("");
        console.log(
            "================================"
        );
        console.log(
            "Station space update completed"
        );
        console.log(
            "================================"
        );
        console.log(
            `Mappings found: ${stationSpaces.size}`
        );
        console.log(
            `Stations updated: ${updated}`
        );
        console.log(
            `Stations not found: ${notFound.length}`
        );

        if (notFound.length > 0) {
            console.log(
                `Missing station IDs: ${notFound.join(", ")}`
            );
        }

        await mongoose.disconnect();

    } catch (error) {

        console.error(
            "Failed to update station spaces:",
            error
        );


        await mongoose.disconnect();
        process.exitCode = 1;

    }

};


updateStationSpaces();
