const express = require("express");

const {
    protect
} = require("../middleware/authMiddleware");


const router = express.Router();


router.get(
    "/profile",
    protect,
    (req, res) => {

        res.json({
            message:
                "Protected route accessed successfully",

            user: {
                id: req.user._id,
                name: req.user.name,
                email: req.user.email,
                role: req.user.role
            }
        });

    }
);


module.exports = router;