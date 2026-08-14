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

import { ROLES } from "../../features/auth/authorization.js";

const ALL_ROLES = [ROLES.ADMIN, ROLES.MANAGER, ROLES.RECEPTIONIST, ROLES.ACCOUNTANT, ROLES.STAFF];
const OPERATIONS_ROLES = [ROLES.ADMIN, ROLES.MANAGER, ROLES.RECEPTIONIST];

export const navigationSections = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", path: "/dashboard", icon: Home, roles: ALL_ROLES }],
  },
  {
    label: "Operations",
    items: [
      { label: "Guests", path: "/guests", icon: Users, roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.RECEPTIONIST, ROLES.ACCOUNTANT, ROLES.STAFF] },
      { label: "Rooms", path: "/rooms", icon: BedDouble, roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.RECEPTIONIST, ROLES.STAFF] },
      { label: "Reservations", path: "/reservations", icon: CalendarDays, roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.RECEPTIONIST, ROLES.ACCOUNTANT] },
      { label: "Check-in / Check-out", path: "/check-in", icon: DoorOpen, roles: OPERATIONS_ROLES },
    ],
  },
  {
    label: "Finance",
    items: [
      { label: "Billing", path: "/billing", icon: ReceiptText, roles: [ROLES.ADMIN, ROLES.ACCOUNTANT] },
      { label: "Payments", path: "/payments", icon: CreditCard, roles: [ROLES.ADMIN, ROLES.ACCOUNTANT] },
    ],
  },
  {
    label: "Management",
    items: [
      { label: "Reports", path: "/reports", icon: FileBarChart, roles: [ROLES.ADMIN, ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.RECEPTIONIST] },
      { label: "Users", path: "/users", icon: ShieldCheck, roles: [ROLES.ADMIN] },
    ],
  },
  {
    label: "System",
    items: [{ label: "Settings", path: "/settings", icon: Settings, roles: [ROLES.ADMIN] }],
  },
];
