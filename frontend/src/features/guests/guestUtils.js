export const idTypeOptions = [
  "NATIONAL_ID",
  "PASSPORT",
  "DRIVER_LICENSE",
  "VOTER_CARD",
  "OTHER",
];

export function getGuestName(guest) {
  return `${guest.first_name || ""} ${guest.last_name || ""}`.trim();
}

export function getGuestInitials(guest) {
  const first = guest.first_name?.[0] || "";
  const last = guest.last_name?.[0] || "";
  return `${first}${last}`.toUpperCase() || "G";
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

function monthName(month) {
  return [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ][month - 1];
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
    return "Guest record was not found.";
  }

  if (error.response.status === 409) {
    return error.response.data?.detail || "This guest cannot be removed.";
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
