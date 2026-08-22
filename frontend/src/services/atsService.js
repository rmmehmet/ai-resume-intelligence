import apiClient from "./api";

export async function analyzeResume(resumeId, jobId) {
  const params = jobId ? { job_id: jobId } : {};
  const { data } = await apiClient.post(`/api/ats/resumes/${resumeId}/analyze`, null, { params });
  return data;
}

export async function listAtsScores(resumeId) {
  const { data } = await apiClient.get(`/api/ats/resumes/${resumeId}/scores`);
  return data;
}