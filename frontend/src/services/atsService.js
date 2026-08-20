import apiClient from "./api";

export async function analyzeResume(resumeId) {
  const { data } = await apiClient.post(`/api/ats/resumes/${resumeId}/analyze`);
  return data;
}

export async function listAtsScores(resumeId) {
  const { data } = await apiClient.get(`/api/ats/resumes/${resumeId}/scores`);
  return data;
}