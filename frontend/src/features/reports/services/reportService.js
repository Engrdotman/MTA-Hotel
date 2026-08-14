import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const client = axios.create({
  baseURL: `${API_BASE}/reports`,
});

// Add auth token to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const reportService = {
  // Dashboard
  getDashboardSummary: () =>
    client.get('/dashboard/'),

  // Occupancy
  getOccupancyReport: (params = {}) =>
    client.get('/occupancy/', { params }),

  // Reservations
  getReservationReport: (params = {}) =>
    client.get('/reservations/', { params }),

  // Revenue
  getRevenueReport: (params = {}) =>
    client.get('/revenue/', { params }),

  // Outstanding
  getOutstandingReport: (params = {}) =>
    client.get('/outstanding/', { params }),
};

export default reportService;
