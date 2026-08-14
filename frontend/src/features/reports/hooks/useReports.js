import { useState, useCallback } from 'react';
import reportService from '../services/reportService';

export const useReports = () => {
  const [dashboard, setDashboard] = useState(null);
  const [occupancy, setOccupancy] = useState(null);
  const [reservations, setReservations] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [outstanding, setOutstanding] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch dashboard summary
  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await reportService.getDashboardSummary();
      setDashboard(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch dashboard';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch occupancy report
  const fetchOccupancy = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await reportService.getOccupancyReport(params);
      setOccupancy(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch occupancy';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch reservations report
  const fetchReservations = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await reportService.getReservationReport(params);
      setReservations(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch reservations';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch revenue report
  const fetchRevenue = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await reportService.getRevenueReport(params);
      setRevenue(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch revenue';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch outstanding report
  const fetchOutstanding = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await reportService.getOutstandingReport(params);
      setOutstanding(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to fetch outstanding';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    // State
    dashboard,
    occupancy,
    reservations,
    revenue,
    outstanding,
    loading,
    error,

    // Actions
    fetchDashboard,
    fetchOccupancy,
    fetchReservations,
    fetchRevenue,
    fetchOutstanding,
  };
};

export default useReports;
