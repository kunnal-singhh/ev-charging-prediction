require("dotenv").config();

const express = require("express");
const cors = require("cors");

const connectDB = require("./config/db");

const authRoutes =
    require("./routes/authRoutes");

const userRoutes =
    require("./routes/userRoutes");    

const stationPredictionRoutes = require(
    "./routes/stationPredictionRoutes"
);

const singleStationPredictionRoutes = require(
    "./routes/singleStationPredictionRoutes"
);

const predictionRoutes = require(
    "./routes/predictionRoutes"
);
const stationRoutes = require(
    "./routes/stationRoutes"
);

const favoriteRoutes =
    require("./routes/favoriteRoutes");

const sessionRoutes =
    require("./routes/sessionRoutes");    

const app = express();

const PORT = process.env.PORT || 5000;


// Connect MongoDB
connectDB();


// Middleware
app.use(cors());
app.use(express.json());


// Root route
app.get("/", (req, res) => {
    res.json({
        message: "EV Charging Backend API",
        status: "running"
    });
});


// Routes

app.use(
    "/api/auth",
    authRoutes
);

app.use(
    "/api/users",
    userRoutes
);


app.use(
    "/api",
    predictionRoutes
);



app.use(
    "/api/stations/predictions",
    stationPredictionRoutes
);


app.use(
    "/api/stations",
    singleStationPredictionRoutes
);


app.use(
    "/api/stations",
    stationRoutes
);

app.use(
    "/api/favorites",
    favoriteRoutes
);

app.use(
    "/api/sessions",
    sessionRoutes
);

// Start server
app.listen(PORT, () => {
    console.log(
        `Backend running on http://localhost:${PORT}`
    );
});