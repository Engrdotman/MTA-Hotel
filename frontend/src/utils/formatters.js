export function formatCurrency(value, currency = "NGN", locale = "en-NG") {
  return new Intl.NumberFormat(locale, {
    currency,
    maximumFractionDigits: 0,
    style: "currency",
  }).format(value);
}
