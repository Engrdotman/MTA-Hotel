/**
 * Format currency to Nigerian Naira
 */
export const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return '₦0.00';
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    minimumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format percentage
 */
export const formatPercent = (value) => {
  if (value === null || value === undefined) return '0%';
  return `${value}%`;
};

/**
 * Format date for display
 */
export const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Parse date string to Date object
 */
export const parseDate = (dateString) => {
  if (!dateString) return null;
  return new Date(dateString);
};

/**
 * Format date for API query (YYYY-MM-DD)
 */
export const formatDateForAPI = (date) => {
  if (!date) return null;
  if (typeof date === 'string') return date;
  return date.toISOString().split('T')[0];
};

/**
 * Get today's date formatted for API
 */
export const getTodayForAPI = () => {
  const today = new Date();
  return formatDateForAPI(today);
};

/**
 * Get occupancy color
 */
export const getOccupancyColor = (rate) => {
  const percentage = parseFloat(rate);
  if (percentage >= 75) return '#4caf50'; // Green
  if (percentage >= 50) return '#ff9800'; // Orange
  return '#f44336'; // Red
};

/**
 * Get room status color
 */
export const getRoomStatusColor = (status) => {
  const colors = {
    AVAILABLE: '#4caf50',
    OCCUPIED: '#ff9800',
    RESERVED: '#2196f3',
    DIRTY: '#f44336',
    MAINTENANCE: '#9c27b0',
    OUT_OF_SERVICE: '#757575',
  };
  return colors[status] || '#999';
};

/**
 * Check if user can access financial reports
 */
export const normalizeRole = (role) => {
  if (!role) return null;
  return typeof role === 'string' ? role : role.name;
};

export const canAccessFinancialReports = (userRole) => {
  const financialRoles = ['ADMIN', 'MANAGER', 'ACCOUNTANT'];
  return financialRoles.includes(normalizeRole(userRole));
};

/**
 * Check if user can access operational reports
 */
export const canAccessOperationalReports = (userRole) => {
  const operationalRoles = ['ADMIN', 'MANAGER', 'RECEPTIONIST'];
  return operationalRoles.includes(normalizeRole(userRole));
};

/**
 * Get default date range (today)
 */
export const getDefaultDateRange = () => {
  const today = new Date();
  return {
    startDate: today,
    endDate: today,
  };
};

/**
 * Get date range for last 30 days
 */
export const getLast30DaysRange = () => {
  const endDate = new Date();
  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - 30);
  return { startDate, endDate };
};

/**
 * Get month-to-date range
 */
export const getMonthToDateRange = () => {
  const today = new Date();
  const startDate = new Date(today.getFullYear(), today.getMonth(), 1);
  return { startDate, endDate: today };
};
