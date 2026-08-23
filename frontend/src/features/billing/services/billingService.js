import { api } from '../../../services/api.js';

export const billingService = {
  // Invoice operations
  getInvoices: (params = {}) =>
    api.get('/billing/invoices/', { params }),

  getInvoice: (id) =>
    api.get(`/billing/invoices/${id}/`),

  createInvoice: (data) =>
    api.post('/billing/invoices/', data),

  updateInvoice: (id, data) =>
    api.patch(`/billing/invoices/${id}/`, data),

  issueInvoice: (id) =>
    api.post(`/billing/invoices/${id}/issue/`),

  voidInvoice: (id) =>
    api.post(`/billing/invoices/${id}/void/`),

  // Payment operations
  getPayments: (invoiceId) =>
    api.get(`/billing/invoices/${invoiceId}/payments/`),

  recordPayment: (invoiceId, data) =>
    api.post(`/billing/invoices/${invoiceId}/record_payment/`, data),

  getCharges: (params = {}) =>
    api.get('/billing/charges/', { params }),

  createCharge: (data) =>
    api.post('/billing/charges/', data),

  // Search and filter
  searchInvoices: (query) =>
    api.get('/billing/invoices/', {
      params: { search: query },
    }),

  filterInvoices: (filters) =>
    api.get('/billing/invoices/', { params: filters }),
};

export default billingService;
