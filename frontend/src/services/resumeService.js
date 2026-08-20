import apiClient from "./api";

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/api/resumes/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listResumes() {
  const { data } = await apiClient.get("/api/resumes");
  return data;
}

export async function getResume(resumeId) {
  const { data } = await apiClient.get(`/api/resumes/${resumeId}`);
  return data;
}