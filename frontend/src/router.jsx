import { createBrowserRouter, Navigate } from "react-router-dom";

import { DashboardLayout } from "./layouts/DashboardLayout.jsx";
import { Dashboard } from "./pages/Dashboard.jsx";
import { Guests } from "./pages/Guests.jsx";
import { Login } from "./pages/Login.jsx";
import { PlaceholderPage } from "./pages/PlaceholderPage.jsx";
import { Reservations } from "./pages/Reservations.jsx";
import { Rooms } from "./pages/Rooms.jsx";
import { Unauthorized } from "./pages/Unauthorized.jsx";
import { Users } from "./pages/Users.jsx";
import { Billing } from "./pages/Billing.jsx";
import { Reports } from "./pages/Reports.jsx";
import { ROLES } from "./features/auth/authorization.js";
import { ProtectedRoute, PublicRoute } from "./features/auth/ProtectedRoute.jsx";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    path: "/login",
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    ),
  },
  {
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: "/dashboard",
        element: <Dashboard />,
      },
      {
        path: "/guests",
        element: <Guests />,
      },
      {
        path: "/rooms",
        element: <Rooms />,
      },
      {
        path: "/reservations",
        element: <Reservations />,
      },
      {
        path: "/users",
        element: (
          <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
            <Users />
          </ProtectedRoute>
        ),
      },
      {
        path: "/billing",
        element: (
          <ProtectedRoute allowedRoles={[ROLES.ADMIN, ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.RECEPTIONIST]}>
            <Billing />
          </ProtectedRoute>
        ),
      },
      {
        path: "/unauthorized",
        element: <Unauthorized />,
      },
      {
        path: "/check-in",
        element: <PlaceholderPage title="Check-in / Check-out" />,
      },
      {
        path: "/payments",
        element: <PlaceholderPage title="Payments" />,
      },
      {
        path: "/reports",
        element: (
          <ProtectedRoute allowedRoles={[ROLES.ADMIN, ROLES.MANAGER, ROLES.ACCOUNTANT, ROLES.RECEPTIONIST]}>
            <Reports />
          </ProtectedRoute>
        ),
      },
      {
        path: "/staff",
        element: <PlaceholderPage title="Staff" />,
      },
      {
        path: "/settings",
        element: <PlaceholderPage title="Settings" />,
      },
    ],
  },
]);
