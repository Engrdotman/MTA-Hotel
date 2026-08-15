import { api } from '../../services/api';

export const dashboardService = {
  async getDashboardMetrics(params = {}) {
    try {
      const response = await api.get('/reports/dashboard/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard metrics:', error);
      throw error;
    }
  },

  async getOccupancyData(params = {}) {
    try {
      const response = await api.get('/reports/occupancy/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching occupancy data:', error);
      throw error;
    }
  },

  async getRecentReservations(params = {}) {
    try {
      const response = await api.get('/reservations/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching reservations:', error);
      throw error;
    }
  },
};
