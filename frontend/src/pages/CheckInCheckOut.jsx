import { useState, useEffect } from 'react';
import { api } from '../services/api.js';
import '../styles/checkin.css';

export const CheckInCheckOut = () => {
  const [stays, setStays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('checked_in');

  useEffect(() => {
    loadStays();
  }, [filterStatus]);

  const loadStays = async () => {
    try {
      setLoading(true);
      setError(null);
      // Map UI status to API status
      const statusMap = {
        checked_in: 'CHECKED_IN',
        checked_out: 'CHECKED_OUT',
      };
      const apiStatus = statusMap[filterStatus];
      const response = await api.get(`/stays/`, { params: { status: apiStatus } });
      setStays(response.data.results || response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load stays');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async (stayId) => {
    if (!window.confirm('Confirm check-out?')) return;
    
    try {
      setLoading(true);
      await api.post(`/stays/${stayId}/check-out/`, { notes: '' });
      setError(null);
      loadStays();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to check out');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Check-in / Check-out Management</h1>
        <p>Manage guest check-ins and check-outs</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="filter-tabs">
        <button
          className={`tab ${filterStatus === 'checked_in' ? 'active' : ''}`}
          onClick={() => setFilterStatus('checked_in')}
        >
          Checked In
        </button>
        <button
          className={`tab ${filterStatus === 'checked_out' ? 'active' : ''}`}
          onClick={() => setFilterStatus('checked_out')}
        >
          Checked Out
        </button>
      </div>

      {loading && <div className="loading-state">Loading...</div>}

      {stays.length === 0 && !loading && (
        <div className="empty-state">
          <p>No stays found for {filterStatus} status</p>
        </div>
      )}

      {stays.length > 0 && (
        <div className="stays-table">
          <table>
            <thead>
              <tr>
                <th>Guest</th>
                <th>Room</th>
                <th>Check-in</th>
                <th>Check-out</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {stays.map((stay) => (
                <tr key={stay.id}>
                  <td>{stay.guest_name || 'N/A'}</td>
                  <td>{stay.room_number || 'N/A'}</td>
                  <td>{new Date(stay.actual_check_in).toLocaleDateString()}</td>
                  <td>{stay.actual_check_out ? new Date(stay.actual_check_out).toLocaleDateString() : 'Pending'}</td>
                  <td><span className={`status ${stay.status?.toLowerCase()}`}>{stay.status}</span></td>
                  <td>
                    {stay.status === 'CHECKED_IN' && (
                      <button 
                        className="btn-small danger" 
                        onClick={() => handleCheckOut(stay.id)}
                        disabled={loading}
                      >
                        Check Out
                      </button>
                    )}
                    {stay.status === 'CHECKED_OUT' && <span className="text-muted">Completed</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default CheckInCheckOut;
