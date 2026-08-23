import { api } from "../../../services/api.js";

export async function getGuests(params) {
  const response = await api.get("/guests/", { params });
  return response.data;
}

export async function getGuest(id) {
  const response = await api.get(`/guests/${id}/`);
  return response.data;
}

export async function createGuest(data) {
  const response = await api.post("/guests/", data);
  return response.data;
}

export async function updateGuest(id, data) {
  const response = await api.patch(`/guests/${id}/`, data);
  return response.data;
}

export async function deactivateGuest(id) {
  const response = await api.patch(`/guests/${id}/`, { is_active: false });
  return response.data;
}

export async function deleteGuest(id) {
  await api.delete(`/guests/${id}/`);
}
