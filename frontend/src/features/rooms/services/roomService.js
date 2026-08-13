import { api } from "../../../services/api.js";

export async function getRooms(params) {
  const response = await api.get("/rooms/", { params });
  return response.data;
}

export async function getRoom(id) {
  const response = await api.get(`/rooms/${id}/`);
  return response.data;
}

export async function createRoom(data) {
  const response = await api.post("/rooms/", data);
  return response.data;
}

export async function updateRoom(id, data) {
  const response = await api.patch(`/rooms/${id}/`, data);
  return response.data;
}

export async function deleteRoom(id) {
  await api.delete(`/rooms/${id}/`);
}

export async function updateRoomStatus(id, status) {
  const response = await api.patch(`/rooms/${id}/status/`, { status });
  return response.data;
}

export async function getRoomSummary() {
  const response = await api.get("/rooms/summary/");
  return response.data;
}

export async function getRoomTypes(params) {
  const response = await api.get("/room-types/", { params });
  return response.data;
}

export async function getRoomType(id) {
  const response = await api.get(`/room-types/${id}/`);
  return response.data;
}

export async function createRoomType(data) {
  const response = await api.post("/room-types/", data);
  return response.data;
}

export async function updateRoomType(id, data) {
  const response = await api.patch(`/room-types/${id}/`, data);
  return response.data;
}

export async function deleteRoomType(id) {
  await api.delete(`/room-types/${id}/`);
}
