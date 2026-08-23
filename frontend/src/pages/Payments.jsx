import { Download, Printer, ReceiptText, Search, WalletCards } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { InvoiceStatusBadge } from "../features/billing/components/InvoiceStatusBadge.jsx";
import useBilling from "../features/billing/hooks/useBilling.js";
import { formatCurrency, formatDateTime, getPaymentMethodDisplay } from "../features/billing/billingUtils.js";
import "../styles/payments.css";

const paymentMethods = [
  ["CASH", "Cash"],
  ["POS", "POS"],
  ["BANK_TRANSFER", "Bank Transfer"],
  ["OTHER", "Other"],
];

const payableStatuses = ["ISSUED", "PARTIALLY_PAID"];

function toNumber(value) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : 0;
}

export function Payments() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [selectedInvoiceId, setSelectedInvoiceId] = useState(null);
  const [receiptPayment, setReceiptPayment] = useState(null);
  const [paymentForm, setPaymentForm] = useState({ amount: "", method: "CASH", notes: "" });
  const [notice, setNotice] = useState("");
  const {
    error,
    fetchInvoice,
    fetchInvoices,
    invoice,
    invoices,
    loading,
    recordPayment,
  } = useBilling();

  const selectedInvoice = selectedInvoiceId === invoice?.id ? invoice : null;
  const invoiceRows = Array.isArray(invoices) ? invoices : [];
  const balance = toNumber(selectedInvoice?.balance);
  const canRecordPayment = selectedInvoice && payableStatuses.includes(selectedInvoice.status) && balance > 0;
  const payments = selectedInvoice?.payments ?? [];
  const latestPayment = payments[0] ?? null;
  const activeReceiptPayment = receiptPayment ?? latestPayment;

  const loadInvoices = useCallback(async () => {
    const params = {};
    if (searchQuery.trim()) {
      params.search = searchQuery.trim();
    }
    if (filterStatus) {
      params.status = filterStatus;
    }
    await fetchInvoices(params);
  }, [fetchInvoices, filterStatus, searchQuery]);

  useEffect(() => {
    loadInvoices().catch(() => undefined);
  }, [loadInvoices]);

  useEffect(() => {
    if (!selectedInvoiceId) {
      return;
    }
    fetchInvoice(selectedInvoiceId).catch(() => undefined);
  }, [fetchInvoice, selectedInvoiceId]);

  useEffect(() => {
    if (!selectedInvoice || paymentForm.amount) {
      return;
    }
    setPaymentForm((current) => ({ ...current, amount: String(balance || "") }));
  }, [balance, paymentForm.amount, selectedInvoice]);

  const receiptRows = useMemo(() => {
    if (!selectedInvoice || !activeReceiptPayment) {
      return [];
    }

    return [
      ["Receipt No.", activeReceiptPayment.payment_reference],
      ["Invoice No.", selectedInvoice.invoice_number],
      ["Guest", selectedInvoice.guest_name],
      ["Room", selectedInvoice.room_number],
      ["Payment Method", activeReceiptPayment.method_display || getPaymentMethodDisplay(activeReceiptPayment.method)],
      ["Payment Date", formatDateTime(activeReceiptPayment.payment_date || activeReceiptPayment.created_at)],
      ["Received By", activeReceiptPayment.received_by_email || "-"],
    ];
  }, [activeReceiptPayment, selectedInvoice]);

  async function handleSelectInvoice(invoiceId) {
    setSelectedInvoiceId(invoiceId);
    setReceiptPayment(null);
    setNotice("");
    const detail = await fetchInvoice(invoiceId);
    setPaymentForm({ amount: String(toNumber(detail.balance) || ""), method: "CASH", notes: "" });
  }

  async function handleRecordPayment(event) {
    event.preventDefault();
    if (!selectedInvoice) {
      return;
    }
    const shouldPrint = event.nativeEvent.submitter?.value === "print";

    const response = await recordPayment(selectedInvoice.id, {
      amount: Number(paymentForm.amount),
      method: paymentForm.method,
      notes: paymentForm.notes.trim(),
    });

    setReceiptPayment(response.payment);
    setPaymentForm({ amount: "", method: "CASH", notes: "" });
    setNotice(`Receipt ${response.payment.payment_reference} is ready for ${response.invoice.guest_name}.`);
    await loadInvoices();
    if (shouldPrint) {
      window.setTimeout(() => window.print(), 100);
    }
  }

  function handlePrintReceipt() {
    window.print();
  }

  return (
    <main className="dashboard-page payments-page">
      <section className="rooms-header">
        <div>
          <p className="dashboard-kicker">Finance</p>
          <h2>Payments</h2>
          <p>Record guest payments and issue front desk receipts.</p>
        </div>
      </section>

      {notice ? <div className="dashboard-notice" role="status">{notice}</div> : null}
      {error ? <div className="dashboard-error" role="alert">{error}</div> : null}

      <section className="payments-workspace">
        <div className="payments-list dashboard-card">
          <div className="payments-toolbar">
            <label className="payment-search">
              <Search aria-hidden="true" size={18} />
              <input
                aria-label="Search invoices"
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search invoice, guest, or reservation"
                value={searchQuery}
              />
            </label>
            <select aria-label="Filter invoice status" onChange={(event) => setFilterStatus(event.target.value)} value={filterStatus}>
              <option value="">All invoices</option>
              <option value="ISSUED">Issued</option>
              <option value="PARTIALLY_PAID">Partially Paid</option>
              <option value="PAID">Paid</option>
            </select>
          </div>

          <div className="payment-table-wrap">
            <table className="payment-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Guest</th>
                  <th>Total</th>
                  <th>Paid</th>
                  <th>Balance</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {invoiceRows.map((item) => (
                  <tr className={selectedInvoiceId === item.id ? "is-selected" : ""} key={item.id}>
                    <td>{item.invoice_number}</td>
                    <td>{item.guest_name}</td>
                    <td>{formatCurrency(item.total)}</td>
                    <td>{formatCurrency(item.amount_paid)}</td>
                    <td>{formatCurrency(item.balance)}</td>
                    <td><InvoiceStatusBadge status={item.status} /></td>
                    <td>
                      <button className="payment-link-button" onClick={() => handleSelectInvoice(item.id)} type="button">
                        Select
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!loading && invoiceRows.length === 0 ? <div className="room-empty">No invoices found.</div> : null}
            {loading ? <div className="room-load-state">Loading invoices...</div> : null}
          </div>
        </div>

        <aside className="payment-side">
          <section className="payment-panel dashboard-card">
            <div className="payment-panel-heading">
              <WalletCards aria-hidden="true" size={22} />
              <div>
                <h3>Record Payment</h3>
                <p>{selectedInvoice ? selectedInvoice.invoice_number : "Select an invoice to begin."}</p>
              </div>
            </div>

            {selectedInvoice ? (
              <>
                <div className="payment-summary">
                  <span>Guest</span>
                  <strong>{selectedInvoice.guest_name}</strong>
                  <span>Balance Due</span>
                  <strong>{formatCurrency(selectedInvoice.balance)}</strong>
                </div>

                <form className="payment-form" onSubmit={handleRecordPayment}>
                  <label className="room-field">
                    Amount
                    <input
                      disabled={!canRecordPayment}
                      max={balance || undefined}
                      min="1"
                      onChange={(event) => setPaymentForm((current) => ({ ...current, amount: event.target.value }))}
                      required
                      step="0.01"
                      type="number"
                      value={paymentForm.amount}
                    />
                  </label>
                  <label className="room-field">
                    Method
                    <select
                      disabled={!canRecordPayment}
                      onChange={(event) => setPaymentForm((current) => ({ ...current, method: event.target.value }))}
                      value={paymentForm.method}
                    >
                      {paymentMethods.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                    </select>
                  </label>
                  <label className="room-field room-field-wide">
                    Notes
                    <textarea
                      disabled={!canRecordPayment}
                      onChange={(event) => setPaymentForm((current) => ({ ...current, notes: event.target.value }))}
                      rows={3}
                      value={paymentForm.notes}
                    />
                  </label>
                  <button className="rooms-secondary-button" disabled={!canRecordPayment || loading} type="submit" value="save">
                    <ReceiptText aria-hidden="true" size={18} />
                    Save & Issue Receipt
                  </button>
                  <button className="rooms-primary-button" disabled={!canRecordPayment || loading} type="submit" value="print">
                    <Printer aria-hidden="true" size={18} />
                    Save & Print Receipt
                  </button>
                </form>
              </>
            ) : (
              <div className="payment-empty">Choose an issued invoice from the table.</div>
            )}
          </section>

          <section className="receipt-preview dashboard-card">
            <div className="payment-panel-heading">
              <ReceiptText aria-hidden="true" size={22} />
              <div>
                <h3>Receipt</h3>
                <p>{activeReceiptPayment ? activeReceiptPayment.payment_reference : "No receipt selected."}</p>
              </div>
            </div>

            {selectedInvoice && activeReceiptPayment ? (
              <>
                <div className="receipt-paper">
                  <div className="receipt-brand">
                    <strong>M.T.A HOTEL</strong>
                    <span>Luxury living in Every Moment</span>
                  </div>
                  <div className="receipt-amount">
                    <span>Amount Received</span>
                    <strong>{formatCurrency(activeReceiptPayment.amount)}</strong>
                  </div>
                  <dl>
                    {receiptRows.map(([label, value]) => (
                      <div key={label}>
                        <dt>{label}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                  <div className="receipt-balance">
                    <span>Invoice Balance</span>
                    <strong>{formatCurrency(selectedInvoice.balance)}</strong>
                  </div>
                </div>
                <button className="rooms-secondary-button" onClick={handlePrintReceipt} type="button">
                  <Printer aria-hidden="true" size={18} />
                  Print Receipt
                </button>
              </>
            ) : (
              <div className="payment-empty">
                <Download aria-hidden="true" size={28} />
                Receipts appear here after selecting a paid invoice or recording payment.
              </div>
            )}
          </section>
        </aside>
      </section>
    </main>
  );
}

export default Payments;
