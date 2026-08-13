import { api } from "../../../services/api.js";

export async function getUsers() {
  const response = await api.get("/users/");
  return response.data;
}

export async function createUser(data) {
  const response = await api.post("/users/", data);
  return response.data;
}

export async function updateUser(id, data) {
  const response = await api.patch(`/users/${id}/`, data);
  return response.data;
}

export async function deactivateUser(id) {
  await api.delete(`/users/${id}/`);
}
