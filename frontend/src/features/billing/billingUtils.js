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
 * Get status badge color
 */
export const getStatusColor = (status) => {
  const colors = {
    DRAFT: 'gray',
    ISSUED: 'blue',
    PARTIALLY_PAID: 'yellow',
    PAID: 'green',
    VOID: 'red',
  };
  return colors[status] || 'gray';
};

/**
 * Get payment method display name
 */
export const getPaymentMethodDisplay = (method) => {
  const methods = {
    CASH: 'Cash',
    POS: 'POS',
    BANK_TRANSFER: 'Bank Transfer',
    OTHER: 'Other',
  };
  return methods[method] || method;
};

/**
 * Calculate invoice summary
 */
export const calculateInvoiceSummary = (invoice) => {
  if (!invoice) return null;

  return {
    invoiceNumber: invoice.invoice_number,
    guestName: invoice.guest_name,
    roomNumber: invoice.room_number,
    status: invoice.status,
    subtotal: invoice.subtotal,
    discount: invoice.discount,
    tax: invoice.tax,
    total: invoice.total,
    amountPaid: invoice.amount_paid,
    balance: invoice.balance,
    issuedAt: invoice.issued_at ? new Date(invoice.issued_at) : null,
    dueAt: invoice.due_at ? new Date(invoice.due_at) : null,
  };
};

/**
 * Check if invoice can be issued
 */
export const canIssueInvoice = (invoice) => {
  return invoice && invoice.status === 'DRAFT';
};

/**
 * Check if invoice can record payment
 */
export const canRecordPayment = (invoice) => {
  return invoice && !['DRAFT', 'VOID'].includes(invoice.status) && invoice.balance > 0;
};

/**
 * Check if invoice can be voided
 */
export const canVoidInvoice = (invoice) => {
  return invoice && !['PAID', 'VOID'].includes(invoice.status);
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
 * Format datetime for display
 */
export const formatDateTime = (dateTime) => {
  if (!dateTime) return '';
  return new Date(dateTime).toLocaleDateString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Get invoice status display
 */
export const getStatusDisplay = (status) => {
  const statuses = {
    DRAFT: 'Draft',
    ISSUED: 'Issued',
    PARTIALLY_PAID: 'Partially Paid',
    PAID: 'Paid',
    VOID: 'Voided',
  };
  return statuses[status] || status;
};

/**
 * Calculate payment percentage
 */
export const getPaymentPercentage = (invoice) => {
  if (!invoice || invoice.total === 0) return 0;
  return Math.round((invoice.amount_paid / invoice.total) * 100);
};

/**
 * Generate invoice summary for printing
 */
export const generateInvoiceSummary = (invoice) => {
  return {
    invoiceNumber: invoice.invoice_number,
    guest: `${invoice.guest_name} (${invoice.guest_code})`,
    room: invoice.room_number,
    roomType: invoice.room_type,
    issuedDate: formatDate(invoice.issued_at),
    items: invoice.items.map((item) => ({
      description: item.description,
      quantity: item.quantity,
      unitPrice: formatCurrency(item.unit_price),
      amount: formatCurrency(item.amount),
    })),
    subtotal: formatCurrency(invoice.subtotal),
    discount: invoice.discount > 0 ? formatCurrency(invoice.discount) : '-',
    tax: invoice.tax > 0 ? formatCurrency(invoice.tax) : '-',
    total: formatCurrency(invoice.total),
    amountPaid: formatCurrency(invoice.amount_paid),
    balance: formatCurrency(invoice.balance),
    status: getStatusDisplay(invoice.status),
  };
};
