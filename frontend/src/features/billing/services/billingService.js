import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const client = axios.create({
  baseURL: `${API_BASE}/billing`,
});

// Add auth token to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const billingService = {
  // Invoice operations
  getInvoices: (params = {}) =>
    client.get('/invoices/', { params }),

  getInvoice: (id) =>
    client.get(`/invoices/${id}/`),

  createInvoice: (data) =>
    client.post('/invoices/', data),

  updateInvoice: (id, data) =>
    client.patch(`/invoices/${id}/`, data),

  issueInvoice: (id) =>
    client.post(`/invoices/${id}/issue/`),

  voidInvoice: (id) =>
    client.post(`/invoices/${id}/void/`),

  // Payment operations
  getPayments: (invoiceId) =>
    client.get(`/invoices/${invoiceId}/payments/`),

  recordPayment: (invoiceId, data) =>
    client.post(`/invoices/${invoiceId}/record_payment/`, data),

  // Search and filter
  searchInvoices: (query) =>
    client.get('/invoices/', {
      params: { search: query },
    }),

  filterInvoices: (filters) =>
    client.get('/invoices/', { params: filters }),
};

export default billingService;
