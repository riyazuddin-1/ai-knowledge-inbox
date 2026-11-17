import { apiClient } from ".";

export async function fetchKnowledgeItems(page = 1, limit = 25) {
  return apiClient(`/items?page=${page}&limit=${limit}`);
}

export async function ingestContent(type, data) {
  return apiClient("/ingest", {
    method: "POST",
    body: JSON.stringify({ type, data }),
  });
}
