import { useState, useEffect } from 'react';
import useBilling from '../features/billing/hooks/useBilling';
import { InvoiceStatusBadge } from '../features/billing/components/InvoiceStatusBadge';
import { formatCurrency, formatDate } from '../features/billing/billingUtils';
import '../styles/billing.css';

export const Billing = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showChargeForm, setShowChargeForm] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [notice, setNotice] = useState('');
  const {
    invoices,
    invoice,
    loading,
    error,
    fetchInvoices,
    fetchInvoice,
    createInvoice,
    createCharge,
    issueInvoice,
    voidInvoice,
    recordPayment,
  } = useBilling();

  // Load invoices on mount
  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (filterStatus) params.status = filterStatus;
      await fetchInvoices(params);
    } catch (err) {
      console.error('Failed to load invoices:', err);
    }
  };

  useEffect(() => {
    const timer = setTimeout(loadInvoices, 500);
    return () => clearTimeout(timer);
  }, [searchQuery, filterStatus]);

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    const stayId = e.target.stay_id.value;
    const discount = e.target.discount.value || 0;

    try {
      await createInvoice({ stay_id: parseInt(stayId), discount: parseFloat(discount) });
      setShowCreateForm(false);
      setNotice('Invoice generated with room charges and any pending stay charges.');
      loadInvoices();
    } catch (err) {
      console.error('Failed to create invoice:', err);
    }
  };

  const handleAddCharge = async (e) => {
    e.preventDefault();
    const form = e.currentTarget;

    try {
      await createCharge({
        stay: parseInt(form.stay_id.value),
        charge_type: form.charge_type.value,
        description: form.description.value.trim(),
        quantity: parseFloat(form.quantity.value),
        unit_price: parseFloat(form.unit_price.value),
        service_date: form.service_date.value,
      });
      form.reset();
      setShowChargeForm(false);
      setNotice('Charge added. It will be included when you generate the invoice for this stay.');
    } catch (err) {
      console.error('Failed to add charge:', err);
    }
  };

  const handleRecordPayment = async (amount, method) => {
    if (!selectedInvoice) return;

    try {
      await recordPayment(selectedInvoice.id, {
        amount: parseFloat(amount),
        method,
      });
      fetchInvoice(selectedInvoice.id);
    } catch (err) {
      console.error('Failed to record payment:', err);
    }
  };

  const handlePrint = () => {
    if (!selectedInvoice) return;
    window.print();
  };

  return (
    <div className="billing-container">
      <div className="billing-header">
        <div>
          <h1>Billing & Invoices</h1>
          <p>Manage invoices and guest payments</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create Invoice'}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {notice && <div className="success-banner">{notice}</div>}

      <div className="billing-flow-actions">
        <button
          className="btn-outline"
          onClick={() => setShowChargeForm(!showChargeForm)}
          type="button"
        >
          {showChargeForm ? 'Cancel Charge' : 'Add Stay Charge'}
        </button>
      </div>

      {showChargeForm && (
        <div className="create-invoice-form">
          <h3>Add Stay Charge</h3>
          <form onSubmit={handleAddCharge}>
            <div className="form-grid">
              <div className="form-group">
                <label>Stay ID</label>
                <input type="number" name="stay_id" required />
              </div>
              <div className="form-group">
                <label>Charge Type</label>
                <select name="charge_type" defaultValue="SERVICE">
                  <option value="SERVICE">Service</option>
                  <option value="FOOD">Food</option>
                  <option value="LAUNDRY">Laundry</option>
                  <option value="DAMAGE">Damage</option>
                  <option value="LATE_CHECKOUT">Late checkout</option>
                  <option value="OTHER">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input type="number" name="quantity" min="0.01" step="0.01" defaultValue="1" required />
              </div>
              <div className="form-group">
                <label>Unit Price</label>
                <input type="number" name="unit_price" min="0" step="0.01" required />
              </div>
              <div className="form-group">
                <label>Service Date</label>
                <input type="date" name="service_date" defaultValue={new Date().toISOString().split('T')[0]} required />
              </div>
              <div className="form-group form-group-wide">
                <label>Description</label>
                <input type="text" name="description" placeholder="Laundry, restaurant order, damages, late checkout..." required />
              </div>
            </div>
            <button type="submit" className="btn-primary">
              Save Charge
            </button>
          </form>
        </div>
      )}

      {showCreateForm && (
        <div className="create-invoice-form">
          <h3>Create New Invoice</h3>
          <form onSubmit={handleCreateInvoice}>
            <div className="form-group">
              <label>Stay ID</label>
              <input type="number" name="stay_id" required />
              <small>Use the checked-in stay ID. Pending charges for this stay will be included automatically.</small>
            </div>
            <div className="form-group">
              <label>Discount (Optional)</label>
              <input type="number" name="discount" min="0" placeholder="0.00" step="0.01" />
              <small>Apply an invoice-level discount in NGN before issuing the invoice.</small>
            </div>
            <button type="submit" className="btn-primary">
              Create Invoice
            </button>
          </form>
        </div>
      )}

      <div className="billing-layout">
        <div className="invoices-section">
          <div className="search-filter">
            <input
              type="text"
              placeholder="Search invoices..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="filter-select"
            >
              <option value="">All Status</option>
              <option value="DRAFT">Draft</option>
              <option value="ISSUED">Issued</option>
              <option value="PARTIALLY_PAID">Partially Paid</option>
              <option value="PAID">Paid</option>
              <option value="VOID">Voided</option>
            </select>
          </div>

          {loading ? (
            <div className="loading">Loading invoices...</div>
          ) : (
            <div className="invoices-table">
              <table>
                <thead>
                  <tr>
                    <th>Invoice</th>
                    <th>Guest</th>
                    <th>Issued Date</th>
                    <th>Total</th>
                    <th>Discount</th>
                    <th>Paid</th>
                    <th>Balance</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.isArray(invoices) && invoices.map((inv) => (
                    <tr key={inv.id} className={selectedInvoice?.id === inv.id ? 'selected' : ''}>
                      <td className="invoice-number">{inv.invoice_number}</td>
                      <td>{inv.guest_name}</td>
                      <td>{formatDate(inv.issued_at)}</td>
                      <td>{formatCurrency(inv.total)}</td>
                      <td>{formatCurrency(inv.discount)}</td>
                      <td>{formatCurrency(inv.amount_paid)}</td>
                      <td>{formatCurrency(inv.balance)}</td>
                      <td>
                        <InvoiceStatusBadge status={inv.status} />
                      </td>
                      <td>
                        <button
                          className="btn-link"
                          onClick={() => {
                            setSelectedInvoice(inv);
                            fetchInvoice(inv.id);
                          }}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {(!invoices || invoices.length === 0) && (
                <div className="empty-state">No invoices found</div>
              )}
            </div>
          )}
        </div>

        {selectedInvoice && invoice && (
          <div className="invoice-detail-panel">
            <div className="detail-header">
              <h3>{invoice.invoice_number}</h3>
              <button
                className="btn-close"
                onClick={() => setSelectedInvoice(null)}
              >
                ✕
              </button>
            </div>

            <div className="detail-content">
              {/* Guest Information */}
              <section className="detail-section">
                <h4>Guest Information</h4>
                <div className="info-grid">
                  <div>
                    <label>Name</label>
                    <p>{invoice.guest_name}</p>
                  </div>
                  <div>
                    <label>Guest Code</label>
                    <p>{invoice.guest_code}</p>
                  </div>
                  <div>
                    <label>Phone</label>
                    <p>{invoice.guest_phone}</p>
                  </div>
                  <div>
                    <label>Email</label>
                    <p>{invoice.guest_email}</p>
                  </div>
                </div>
              </section>

              {/* Room & Reservation */}
              <section className="detail-section">
                <h4>Room & Reservation</h4>
                <div className="info-grid">
                  <div>
                    <label>Room Number</label>
                    <p>{invoice.room_number}</p>
                  </div>
                  <div>
                    <label>Room Type</label>
                    <p>{invoice.room_type}</p>
                  </div>
                  <div>
                    <label>Reservation</label>
                    <p>{invoice.reservation_number}</p>
                  </div>
                  <div>
                    <label>Stay Charges</label>
                    <p>{invoice.stay_charges?.length || 0} included</p>
                  </div>
                </div>
              </section>

              {/* Invoice Items */}
              <section className="detail-section">
                <h4>Items</h4>
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>Description</th>
                      <th>Qty</th>
                      <th>Unit Price</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoice.items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.description}</td>
                        <td>{item.quantity}</td>
                        <td>{formatCurrency(item.unit_price)}</td>
                        <td>{formatCurrency(item.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>

              {/* Totals */}
              <section className="detail-section">
                <div className="totals">
                  <div className="total-row">
                    <span>Subtotal:</span>
                    <span>{formatCurrency(invoice.subtotal)}</span>
                  </div>
                  <div className="total-row discount">
                    <span>Discount:</span>
                    <span>-{formatCurrency(invoice.discount)}</span>
                  </div>
                  {invoice.tax > 0 && (
                    <div className="total-row tax">
                      <span>Tax:</span>
                      <span>{formatCurrency(invoice.tax)}</span>
                    </div>
                  )}
                  <div className="total-row total">
                    <span>Total:</span>
                    <span>{formatCurrency(invoice.total)}</span>
                  </div>
                  <div className="total-row paid">
                    <span>Paid:</span>
                    <span>{formatCurrency(invoice.amount_paid)}</span>
                  </div>
                  <div className="total-row balance">
                    <span>Balance:</span>
                    <span>{formatCurrency(invoice.balance)}</span>
                  </div>
                </div>
              </section>

              {/* Actions */}
              <div className="actions">
                {invoice.status === 'DRAFT' && (
                  <button
                    className="btn-secondary"
                    onClick={() => issueInvoice(invoice.id).then(() => fetchInvoice(invoice.id))}
                  >
                    Issue Invoice
                  </button>
                )}
                {['ISSUED', 'PARTIALLY_PAID'].includes(invoice.status) && invoice.balance > 0 && (
                  <button
                    className="btn-success"
                    onClick={() => {
                      const amount = prompt('Enter payment amount:');
                      const method = 'CASH';
                      if (amount) handleRecordPayment(amount, method);
                    }}
                  >
                    Record Payment
                  </button>
                )}
                {!['PAID', 'VOID'].includes(invoice.status) && (
                  <button
                    className="btn-danger"
                    onClick={() => voidInvoice(invoice.id).then(() => fetchInvoice(invoice.id))}
                  >
                    Void Invoice
                  </button>
                )}
                <button className="btn-outline" onClick={handlePrint}>
                  Print Invoice
                </button>
              </div>

              {/* Payment History */}
              {invoice.payments.length > 0 && (
                <section className="detail-section">
                  <h4>Payment History</h4>
                  <table className="payments-table">
                    <thead>
                      <tr>
                        <th>Reference</th>
                        <th>Amount</th>
                        <th>Method</th>
                        <th>Date</th>
                        <th>Received By</th>
                      </tr>
                    </thead>
                    <tbody>
                      {invoice.payments.map((payment) => (
                        <tr key={payment.id}>
                          <td>{payment.payment_reference}</td>
                          <td>{formatCurrency(payment.amount)}</td>
                          <td>{payment.method_display}</td>
                          <td>{formatDate(payment.payment_date)}</td>
                          <td>{payment.received_by_email}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </section>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Billing;
