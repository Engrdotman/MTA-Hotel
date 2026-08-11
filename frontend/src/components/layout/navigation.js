import {
  BarChart3,
  BedDouble,
  CreditCard,
  DoorOpen,
  FileBarChart,
  Home,
  ReceiptText,
  Settings,
  ShieldCheck,
  Users,
  CalendarDays,
} from "lucide-react";

export const navigationSections = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", path: "/dashboard", icon: Home }],
  },
  {
    label: "Operations",
    items: [
      { label: "Guests", path: "/guests", icon: Users },
      { label: "Rooms", path: "/rooms", icon: BedDouble },
      { label: "Reservations", path: "/reservations", icon: CalendarDays },
      { label: "Check-in / Check-out", path: "/check-in", icon: DoorOpen },
    ],
  },
  {
    label: "Finance",
    items: [
      { label: "Billing", path: "/billing", icon: ReceiptText },
      { label: "Payments", path: "/payments", icon: CreditCard },
    ],
  },
  {
    label: "Management",
    items: [
      { label: "Reports", path: "/reports", icon: FileBarChart },
      { label: "Staff", path: "/staff", icon: ShieldCheck },
    ],
  },
  {
    label: "System",
    items: [{ label: "Settings", path: "/settings", icon: Settings }],
  },
];
