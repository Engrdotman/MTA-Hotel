import { api } from "../../../services/api.js";

export async function getReservations(params) {
  const response = await api.get("/reservations/", { params });
  return response.data;
}

export async function createReservation(data) {
  const response = await api.post("/reservations/", data);
  return response.data;
}

export async function updateReservation(id, data) {
  const response = await api.patch(`/reservations/${id}/`, data);
  return response.data;
}

export async function deleteReservation(id) {
  await api.delete(`/reservations/${id}/`);
}

export async function updateReservationStatus(id, status) {
  const response = await api.patch(`/reservations/${id}/status/`, { status });
  return response.data;
}

export async function getReservationSummary() {
  const response = await api.get("/reservations/summary/");
  return response.data;
}
