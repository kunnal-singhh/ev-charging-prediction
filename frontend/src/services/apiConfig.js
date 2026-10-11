const productionApiUrl =
    "https://ev-charging-prediction-backend.onrender.com";

export const API_URL =
    import.meta.env.VITE_API_URL ||
    (import.meta.env.DEV ? "http://localhost:5000" : productionApiUrl);
