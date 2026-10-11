const ML_API_URL =
    process.env.ML_API_URL ||
    "http://127.0.0.1:8000";

const ML_REQUEST_TIMEOUT_MS = 30000;


async function predictBatch(predictions) {

    const response = await fetch(
        `${ML_API_URL}/predict/batch`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                predictions
            }),
            signal: AbortSignal.timeout(ML_REQUEST_TIMEOUT_MS)
        }
    );

    if (!response.ok) {
        throw new Error(
            `ML API error: ${response.status}`
        );
    }

    return await response.json();
}


module.exports = {
    predictBatch
};