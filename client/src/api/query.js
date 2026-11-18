import { apiClient } from ".";

export async function submitQuery(question) {
  const response = await apiClient("/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
  // Automatically unwrap and return just the data payload ({ answer, sources })
  return response.data; 
}
