import { api } from '../../../services/api.js';

export const reportService = {
  // Dashboard
  getDashboardSummary: () =>
    api.get('/reports/dashboard/'),

  // Occupancy
  getOccupancyReport: (params = {}) =>
    api.get('/reports/occupancy/', { params }),

  // Reservations
  getReservationReport: (params = {}) =>
    api.get('/reports/reservations/', { params }),

  // Revenue
  getRevenueReport: (params = {}) =>
    api.get('/reports/revenue/', { params }),

  // Outstanding
  getOutstandingReport: (params = {}) =>
    api.get('/reports/outstanding/', { params }),
};

export default reportService;
