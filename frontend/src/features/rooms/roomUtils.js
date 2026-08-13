export const roomStatuses = [
  "AVAILABLE",
  "OCCUPIED",
  "RESERVED",
  "DIRTY",
  "MAINTENANCE",
  "OUT_OF_SERVICE",
];

export function formatStatus(status) {
  return status
    ? status
        .toLowerCase()
        .split("_")
        .map((part) => part[0].toUpperCase() + part.slice(1))
        .join(" ")
    : "-";
}

export function formatCurrency(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  return new Intl.NumberFormat("en-NG", {
    currency: "NGN",
    maximumFractionDigits: 0,
    style: "currency",
  }).format(Number(value));
}

export function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

export function getApiErrorMessage(error) {
  if (!error.response) {
    return "Network error. Please check your connection and try again.";
  }

  if (error.response.status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (error.response.status === 403) {
    return "You do not have permission to perform this action.";
  }

  if (error.response.status === 404) {
    return "Record was not found.";
  }

  if (error.response.status === 409) {
    return error.response.data?.detail || "This record cannot be deleted.";
  }

  if (error.response.status >= 500) {
    return "Server error. Please try again shortly.";
  }

  return "Unable to complete the request. Please review the details and try again.";
}

export function mapValidationErrors(error) {
  if (!error.response || ![400, 422].includes(error.response.status)) {
    return {};
  }

  return error.response.data || {};
}
