import { apiClient } from ".";

export async function submitQuery(question) {
  return apiClient("/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
