import { API_URL } from "./apiConfig";


export async function registerUser(
    name,
    email,
    password
) {

    const response = await fetch(
        `${API_URL}/api/auth/register`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name,
                email,
                password
            })
        }
    );


    const data = await response.json();


    if (!response.ok) {
        throw new Error(
            data.message ||
            "Registration failed"
        );
    }


    return data;
}


export async function loginUser(
    email,
    password
) {

    const response = await fetch(
        `${API_URL}/api/auth/login`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email,
                password
            })
        }
    );


    const data = await response.json();


    if (!response.ok) {
        throw new Error(
            data.message ||
            "Login failed"
        );
    }


    return data;
}


export async function getProfile(token) {

    const response = await fetch(
        `${API_URL}/api/users/profile`,
        {
            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );


    const data = await response.json();


    if (!response.ok) {
        throw new Error(
            data.message ||
            "Failed to fetch profile"
        );
    }


    return data;
}