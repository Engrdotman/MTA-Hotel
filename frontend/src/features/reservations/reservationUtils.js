export const reservationStatusOptions = [
  "PENDING",
  "CONFIRMED",
  "CHECKED_IN",
  "CHECKED_OUT",
  "CANCELLED",
  "NO_SHOW",
];

export const reservationSourceOptions = ["WALK_IN", "PHONE", "EMAIL", "WEBSITE", "AGENT", "OTHER"];

export function formatReservationLabel(value) {
  return value
    .toLowerCase()
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function formatDate(value) {
  if (!value) {
    return "-";
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return `${day} ${monthName(Number(month))} ${year}`;
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
    return "Reservation was not found.";
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

function monthName(month) {
  return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month - 1];
}
