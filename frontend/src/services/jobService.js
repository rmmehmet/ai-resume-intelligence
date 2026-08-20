import apiClient from "./api";

export async function createJob({ title, description }) {
  const { data } = await apiClient.post("/api/jobs", { title, description });
  return data;
}

export async function listJobs() {
  const { data } = await apiClient.get("/api/jobs");
  return data;
}

export async function getJob(jobId) {
  const { data } = await apiClient.get(`/api/jobs/${jobId}`);
  return data;
}