import apiClient from "./api";

export async function createMatch(resumeId, jobId) {
  const { data } = await apiClient.post(`/api/matching/resumes/${resumeId}/jobs/${jobId}`);
  return data;
}

export async function listMatchesForResume(resumeId) {
  const { data } = await apiClient.get(`/api/matching/resumes/${resumeId}/results`);
  return data;
}