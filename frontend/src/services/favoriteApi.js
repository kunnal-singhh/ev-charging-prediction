const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";


function getToken() {

    return localStorage.getItem(
        "token"
    );
}


export async function getFavorites() {

    const token = getToken();


    const response = await fetch(
        `${API_URL}/api/favorites`,
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
            "Failed to get favorites"
        );
    }


    return data;
}


export async function addFavorite(
    stationId
) {

    const token = getToken();


    const response = await fetch(
        `${API_URL}/api/favorites/${stationId}`,
        {
            method: "POST",

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
            "Failed to add favorite"
        );
    }


    return data;
}


export async function removeFavorite(
    stationId
) {

    const token = getToken();


    const response = await fetch(
        `${API_URL}/api/favorites/${stationId}`,
        {
            method: "DELETE",

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
            "Failed to remove favorite"
        );
    }


    return data;
}