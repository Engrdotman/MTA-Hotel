import { useState, useEffect } from 'react';
import { useAuth } from '../features/auth/authContext.js';
import useReports from '../features/reports/hooks/useReports';
import {
  formatCurrency,
  formatPercent,
  getTodayForAPI,
  getOccupancyColor,
  canAccessFinancialReports,
} from '../features/reports/reportUtils';
import '../styles/reports.css';

export const Reports = () => {
  const { user } = useAuth();
  const {
    dashboard,
    occupancy,
    reservations,
    revenue,
    outstanding,
    loading,
    error,
    fetchDashboard,
    fetchOccupancy,
    fetchReservations,
    fetchRevenue,
    fetchOutstanding,
  } = useReports();

  const [startDate, setStartDate] = useState(getTodayForAPI());
  const [endDate, setEndDate] = useState(getTodayForAPI());
  const [filterApplied, setFilterApplied] = useState(false);

  // Load initial data
  useEffect(() => {
    loadAllReports();
  }, []);

  const loadAllReports = async () => {
    try {
      await fetchDashboard();
      await fetchOccupancy();
      await fetchReservations();
      if (canAccessFinancialReports(user?.role)) {
        try {
          await fetchRevenue();
        } catch {
          console.error('Failed to load revenue report (permission denied)');
        }
        try {
          await fetchOutstanding();
        } catch {
          console.error('Failed to load outstanding report (permission denied)');
        }
      }
    } catch (err) {
      console.error('Failed to load reports:', err);
    }
  };

  const handleApplyFilter = async (e) => {
    e.preventDefault();
    setFilterApplied(true);
    try {
      const params = { start_date: startDate, end_date: endDate };
      await Promise.all([
        fetchOccupancy(params),
        fetchReservations(params),
        canAccessFinancialReports(user?.role) && fetchRevenue(params),
        canAccessFinancialReports(user?.role) && fetchOutstanding(params),
      ].filter(Boolean));
    } catch (err) {
      console.error('Failed to apply filter:', err);
    }
  };

  const handleClearFilter = () => {
    setStartDate(getTodayForAPI());
    setEndDate(getTodayForAPI());
    setFilterApplied(false);
    loadAllReports();
  };

  if (error) {
    return (
      <div className="reports-container">
        <div className="error-banner">{error}</div>
      </div>
    );
  }

  return (
    <div className="reports-container">
      {/* Header */}
      <div className="reports-header">
        <div>
          <h1>Reports</h1>
          <p>View hotel operations and financial summaries</p>
        </div>
      </div>

      {/* Date Filter */}
      <div className="date-filter-section">
        <form onSubmit={handleApplyFilter} className="date-filter-form">
          <div className="form-group">
            <label>From</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="date-input"
            />
          </div>
          <div className="form-group">
            <label>To</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="date-input"
            />
          </div>
          <button type="submit" className="btn-primary">
            Apply
          </button>
          {filterApplied && (
            <button
              type="button"
              className="btn-secondary"
              onClick={handleClearFilter}
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Loading State */}
      {loading && <div className="loading-state">Loading reports...</div>}

      {/* Summary Cards */}
      {dashboard && (
        <div className="summary-cards">
          <div className="card">
            <div className="card-label">Total Rooms</div>
            <div className="card-value">{dashboard.total_rooms}</div>
          </div>
          <div className="card">
            <div className="card-label">Occupied</div>
            <div className="card-value accent-orange">{dashboard.occupied_rooms}</div>
          </div>
          <div className="card">
            <div className="card-label">Available</div>
            <div className="card-value accent-green">{dashboard.available_rooms}</div>
          </div>
          <div className="card">
            <div className="card-label">Today's Check-ins</div>
            <div className="card-value">{dashboard.today_check_ins}</div>
          </div>
          <div className="card">
            <div className="card-label">Today's Check-outs</div>
            <div className="card-value">{dashboard.today_check_outs}</div>
          </div>
          <div className="card">
            <div className="card-label">Current Guests</div>
            <div className="card-value">{dashboard.current_guests}</div>
          </div>

          {canAccessFinancialReports(user?.role) && (
            <>
              <div className="card financial">
                <div className="card-label">Today's Revenue</div>
                <div className="card-value">{formatCurrency(dashboard.today_revenue)}</div>
              </div>
              <div className="card financial">
                <div className="card-label">Outstanding Balance</div>
                <div className="card-value accent-red">{formatCurrency(dashboard.outstanding_balance)}</div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Reports Grid */}
      <div className="reports-grid">
        {/* Occupancy Report */}
        {occupancy && (
          <div className="report-card">
            <h3>Occupancy Report</h3>
            <div className="occupancy-gauge">
              <div
                className="occupancy-meter"
                style={{
                  width: `${occupancy.occupancy_rate}%`,
                  backgroundColor: getOccupancyColor(occupancy.occupancy_rate),
                }}
              />
            </div>
            <div className="occupancy-rate">{formatPercent(occupancy.occupancy_rate)}</div>
            <div className="report-details">
              <div className="detail-row">
                <span>Occupied:</span>
                <span>{occupancy.occupied}</span>
              </div>
              <div className="detail-row">
                <span>Available:</span>
                <span>{occupancy.available}</span>
              </div>
              <div className="detail-row">
                <span>Reserved:</span>
                <span>{occupancy.reserved}</span>
              </div>
              <div className="detail-row">
                <span>Maintenance:</span>
                <span>{occupancy.maintenance}</span>
              </div>
            </div>
          </div>
        )}

        {/* Reservations Report */}
        {reservations && (
          <div className="report-card">
            <h3>Reservations Report</h3>
            <div className="report-details">
              <div className="detail-row highlight">
                <span>Total:</span>
                <span>{reservations.total}</span>
              </div>
              <div className="detail-row">
                <span>Pending:</span>
                <span>{reservations.pending}</span>
              </div>
              <div className="detail-row">
                <span>Confirmed:</span>
                <span>{reservations.confirmed}</span>
              </div>
              <div className="detail-row">
                <span>Checked In:</span>
                <span>{reservations.checked_in}</span>
              </div>
              <div className="detail-row">
                <span>Checked Out:</span>
                <span>{reservations.checked_out}</span>
              </div>
              <div className="detail-row">
                <span>Cancelled:</span>
                <span>{reservations.cancelled}</span>
              </div>
            </div>
          </div>
        )}

        {/* Revenue Report */}
        {canAccessFinancialReports(user?.role) && revenue && (
          <div className="report-card financial-card">
            <h3>Revenue Report</h3>
            <div className="revenue-total">
              <div className="label">Total Revenue</div>
              <div className="amount">{formatCurrency(revenue.total_revenue)}</div>
            </div>
            <div className="report-details">
              <div className="detail-row">
                <span>Cash:</span>
                <span>{formatCurrency(revenue.cash)}</span>
              </div>
              <div className="detail-row">
                <span>POS:</span>
                <span>{formatCurrency(revenue.pos)}</span>
              </div>
              <div className="detail-row">
                <span>Bank Transfer:</span>
                <span>{formatCurrency(revenue.bank_transfer)}</span>
              </div>
              <div className="detail-row">
                <span>Other:</span>
                <span>{formatCurrency(revenue.other)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Outstanding Report */}
        {canAccessFinancialReports(user?.role) && outstanding && (
          <div className="report-card financial-card">
            <h3>Outstanding Balances</h3>
            <div className="outstanding-total">
              <div className="label">Total Outstanding</div>
              <div className="amount">{formatCurrency(outstanding.total_outstanding)}</div>
            </div>
            <div className="report-details">
              <div className="detail-row">
                <span>Unpaid Invoices:</span>
                <span>{outstanding.unpaid_invoices}</span>
              </div>
              <div className="detail-row">
                <span>Partially Paid:</span>
                <span>{outstanding.partially_paid_invoices}</span>
              </div>
            </div>
            <button className="btn-link" onClick={() => window.location.href = '/billing'}>
              View Billing →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
