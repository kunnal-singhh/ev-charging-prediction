require("dotenv").config();

const fs = require("fs");
const path = require("path");

const connectDB = require("./config/db");
const Station = require("./models/Station");

const { parse } = require("csv-parse/sync");


const CSV_PATH = path.join(
    __dirname,
    "..",
    "services",
    "ai-service",
    "data",
    "processed",
    "station_occupancy_30min.csv"
);


const seedStations = async () => {

    try {

        await connectDB();

        console.log("Reading station data...");

        const csvData = fs.readFileSync(
            CSV_PATH,
            "utf-8"
        );

        const records = parse(csvData, {
            columns: true,
            skip_empty_lines: true
        });

        console.log(
            `Loaded ${records.length} occupancy records.`
        );


        // Get unique station IDs
        const stationIds = [
            ...new Set(
                records
                    .map(record => record.stationID)
                    .filter(Boolean)
            )
        ];


        console.log(
            `Found ${stationIds.length} unique stations.`
        );


        const stations = stationIds.map(
            stationId => ({
                stationId,
                name: `Charging Station ${stationId}`,
                siteId: "caltech",
                connectorType: "AC",
                totalConnectors: 1,
                status: "available"
            })
        );


        // Insert only stations that don't already exist
        let inserted = 0;

        for (const station of stations) {

            const exists = await Station.findOne({
                stationId: station.stationId
            });

            if (!exists) {

                await Station.create(station);

                inserted++;
            }
        }


        console.log(
            `Inserted ${inserted} new stations.`
        );

        console.log(
            `Total stations in database: ${stationIds.length}`
        );


        process.exit(0);

    } catch (error) {

        console.error(
            "Station seeding failed:"
        );

        console.error(error);

        process.exit(1);
    }
};


seedStations();