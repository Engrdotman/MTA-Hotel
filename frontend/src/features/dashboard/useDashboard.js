import { useState, useEffect } from 'react';
import { dashboardService } from './dashboardService';

export function useDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [occupancy, setOccupancy] = useState(null);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getDashboardMetrics();
      setDashboard(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    }
  };

  const fetchOccupancy = async () => {
    try {
      const data = await dashboardService.getOccupancyData();
      setOccupancy(data);
    } catch (err) {
      console.error('Occupancy error:', err);
    }
  };

  const fetchReservations = async () => {
    try {
      const data = await dashboardService.getRecentReservations({ limit: 5 });
      setReservations(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      console.error('Reservations error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([fetchDashboard(), fetchOccupancy(), fetchReservations()]);
  }, []);

  return {
    dashboard,
    occupancy,
    reservations,
    loading,
    error,
    refetch: () => Promise.all([fetchDashboard(), fetchOccupancy(), fetchReservations()]),
  };
}

export default useDashboard;
