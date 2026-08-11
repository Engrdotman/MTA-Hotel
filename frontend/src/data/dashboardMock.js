export const currentUser = {
  name: "Admin",
  role: "Hotel Administrator",
  initials: "AD",
};

export const statCards = [
  {
    id: "total-rooms",
    label: "Total Rooms",
    value: 24,
    support: "18 active today",
    tone: "primary",
  },
  {
    id: "occupied-rooms",
    label: "Occupied Rooms",
    value: 8,
    support: "33% occupancy",
    tone: "success",
  },
  {
    id: "check-ins",
    label: "Today's Check-ins",
    value: 6,
    support: "2 pending",
    tone: "info",
  },
  {
    id: "revenue",
    label: "Today's Revenue",
    value: 450000,
    support: "+12.5% from yesterday",
    tone: "warning",
    format: "currency",
  },
];

export const roomStatus = [
  { label: "Available", value: 10, tone: "success" },
  { label: "Occupied", value: 8, tone: "primary" },
  { label: "Reserved", value: 4, tone: "info" },
  { label: "Cleaning", value: 2, tone: "warning" },
];

export const recentReservations = [
  {
    id: "res-101",
    guest: "John Doe",
    room: "Room 101",
    checkIn: "11 Aug 2026",
    checkOut: "13 Aug 2026",
    status: "Confirmed",
  },
  {
    id: "res-204",
    guest: "Aisha Bello",
    room: "Room 204",
    checkIn: "11 Aug 2026",
    checkOut: "15 Aug 2026",
    status: "Checked In",
  },
  {
    id: "res-118",
    guest: "David Okafor",
    room: "Room 118",
    checkIn: "12 Aug 2026",
    checkOut: "14 Aug 2026",
    status: "Pending",
  },
  {
    id: "res-302",
    guest: "Mariam Yusuf",
    room: "Room 302",
    checkIn: "12 Aug 2026",
    checkOut: "16 Aug 2026",
    status: "Confirmed",
  },
];
