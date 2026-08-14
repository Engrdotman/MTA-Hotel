import { getStatusColor, getStatusDisplay } from '../billingUtils';

export const InvoiceStatusBadge = ({ status }) => {
  const colors = {
    gray: 'bg-gray-100 text-gray-800',
    blue: 'bg-blue-100 text-blue-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    green: 'bg-green-100 text-green-800',
    red: 'bg-red-100 text-red-800',
  };

  const color = getStatusColor(status);
  const colorClass = colors[color];

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${colorClass}`}>
      {getStatusDisplay(status)}
    </span>
  );
};
