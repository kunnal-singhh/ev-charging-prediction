const express = require("express");

const {
    createSession,
    getSessions,
    getSession,
    updateSession
} = require("../controllers/sessionController");

const {
    protect
} = require("../middleware/authMiddleware");


const router = express.Router();


// Create session
router.post(
    "/",
    protect,
    createSession
);


// Get current user's sessions
router.get(
    "/",
    protect,
    getSessions
);


// Get one session
router.get(
    "/:id",
    protect,
    getSession
);


// Update one session
router.patch(
    "/:id",
    protect,
    updateSession
);


module.exports = router;