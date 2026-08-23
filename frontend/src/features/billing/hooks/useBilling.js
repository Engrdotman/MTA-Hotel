import { useState, useCallback } from 'react';
import billingService from '../services/billingService';

export const useBilling = () => {
  const [invoices, setInvoices] = useState([]);
  const [invoice, setInvoice] = useState(null);
  const [charges, setCharges] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all invoices
  const fetchInvoices = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.getInvoices(params);
      const invoiceData = Array.isArray(response.data) ? response.data : response.data.results || [];
      setInvoices(invoiceData);
      return invoiceData;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch invoices';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch single invoice
  const fetchInvoice = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.getInvoice(id);
      setInvoice(response.data);
      setPayments(response.data.payments || []);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch invoice';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Create invoice
  const createInvoice = useCallback(async (data) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.createInvoice(data);
      setInvoice(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to create invoice';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Issue invoice
  const issueInvoice = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.issueInvoice(id);
      setInvoice(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to issue invoice';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Void invoice
  const voidInvoice = useCallback(async (id) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.voidInvoice(id);
      setInvoice(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to void invoice';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Record payment
  const recordPayment = useCallback(async (invoiceId, data) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.recordPayment(invoiceId, data);
      setInvoice(response.data.invoice);
      setPayments(response.data.invoice.payments || []);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to record payment';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCharges = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.getCharges(params);
      const chargeData = Array.isArray(response.data) ? response.data : response.data.results || [];
      setCharges(chargeData);
      return chargeData;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch charges';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createCharge = useCallback(async (data) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.createCharge(data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.detail || err.message || 'Failed to add charge';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Search invoices
  const searchInvoices = useCallback(async (query) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.searchInvoices(query);
      setInvoices(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Search failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Filter invoices
  const filterInvoices = useCallback(async (filters) => {
    try {
      setLoading(true);
      setError(null);
      const response = await billingService.filterInvoices(filters);
      setInvoices(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Filter failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    // State
    invoices,
    invoice,
    charges,
    payments,
    loading,
    error,

    // Actions
    fetchInvoices,
    fetchInvoice,
    createInvoice,
    issueInvoice,
    voidInvoice,
    recordPayment,
    fetchCharges,
    createCharge,
    searchInvoices,
    filterInvoices,
  };
};

export default useBilling;
