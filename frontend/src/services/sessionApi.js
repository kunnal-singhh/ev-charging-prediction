const API_URL = "http://localhost:5000";


function getToken() {
    return localStorage.getItem("token");
}


export async function createSession(
    stationId,
    startTime
) {

    const token = getToken();

    const response = await fetch(
        `${API_URL}/api/sessions`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                stationId,
                startTime
            })
        }
    );


    const data = await response.json();


    if (!response.ok) {
        throw new Error(
            data.message ||
            "Failed to create charging session"
        );
    }


    return data;
}


export async function getSessions() {

    const token = getToken();

    const response = await fetch(
        `${API_URL}/api/sessions`,
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
            "Failed to get charging sessions"
        );
    }


    return data;
}


export async function getSession(id) {

    const token = getToken();

    const response = await fetch(
        `${API_URL}/api/sessions/${id}`,
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
            "Failed to get charging session"
        );
    }


    return data;
}


export async function updateSession(
    id,
    updates
) {

    const token = getToken();

    const response = await fetch(
        `${API_URL}/api/sessions/${id}`,
        {
            method: "PATCH",

            headers: {
                "Content-Type": "application/json",
                Authorization:
                    `Bearer ${token}`
            },

            body: JSON.stringify(updates)
        }
    );


    const data = await response.json();


    if (!response.ok) {
        throw new Error(
            data.message ||
            "Failed to update charging session"
        );
    }


    return data;
}