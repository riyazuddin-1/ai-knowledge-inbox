const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiClient(endpoint, options = {}, retries = 3, delay = 1000) {
  let attempt = 0;

  while (attempt < retries) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        // Retry only on server errors (500 and above)
        if (response.status >= 500 && attempt < retries - 1) {
          attempt++;
          await new Promise((res) => setTimeout(res, delay * Math.pow(2, attempt - 1)));
          continue;
        }

        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Request failed with status ${response.status}`);
      }

      if (response.status === 204) return null;
      
      const json = await response.json();
      // If your backend returns the standard wrapper { success, message, data, pagination }, unpack data & pagination
      return json.data !== undefined ? json : json;
    } catch (error) {
      // Retry on network/connection drops if attempts remain
      if (attempt < retries - 1 && (error.name === "TypeError" || error.message.includes("fetch"))) {
        attempt++;
        await new Promise((res) => setTimeout(res, delay * Math.pow(2, attempt - 1)));
        continue;
      }
      throw error;
    }
  }
}
