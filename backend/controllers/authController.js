const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const User = require("../models/User");


const generateToken = (user) => {

    return jwt.sign(
        {
            userId: user._id,
            role: user.role
        },

        process.env.JWT_SECRET,

        {
            expiresIn: "7d"
        }
    );
};


// REGISTER

const register = async (req, res) => {

    try {

        const {
            name,
            email,
            password
        } = req.body;


        if (!name || !email || !password) {

            return res.status(400).json({
                message:
                    "Name, email and password are required"
            });
        }


        const existingUser =
            await User.findOne({ email });


        if (existingUser) {

            return res.status(409).json({
                message:
                    "User with this email already exists"
            });
        }


        const hashedPassword =
            await bcrypt.hash(password, 10);


        const user =
            await User.create({

                name,

                email,

                password: hashedPassword

            });


        const token =
            generateToken(user);


        res.status(201).json({

            message:
                "User registered successfully",

            token,

            user: {

                id: user._id,

                name: user.name,

                email: user.email,

                role: user.role

            }

        });

    } catch (error) {

        console.error(
            "Registration error:",
            error
        );

        res.status(500).json({

            message:
                "Registration failed"

        });
    }
};


// LOGIN

const login = async (req, res) => {

    try {

        const {
            email,
            password
        } = req.body;


        if (!email || !password) {

            return res.status(400).json({

                message:
                    "Email and password are required"

            });
        }


        const user =
            await User.findOne({ email });


        if (!user) {

            return res.status(401).json({

                message:
                    "Invalid email or password"

            });
        }


        const passwordMatch =
            await bcrypt.compare(
                password,
                user.password
            );


        if (!passwordMatch) {

            return res.status(401).json({

                message:
                    "Invalid email or password"

            });
        }


        const token =
            generateToken(user);


        res.json({

            message:
                "Login successful",

            token,

            user: {

                id: user._id,

                name: user.name,

                email: user.email,

                role: user.role

            }

        });

    } catch (error) {

        console.error(
            "Login error:",
            error
        );

        res.status(500).json({

            message:
                "Login failed"

        });
    }
};


module.exports = {
    register,
    login
};