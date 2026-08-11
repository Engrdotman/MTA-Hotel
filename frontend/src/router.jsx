import { createBrowserRouter, Navigate } from "react-router-dom";

import { DashboardLayout } from "./layouts/DashboardLayout.jsx";
import { Dashboard } from "./pages/Dashboard.jsx";
import { Login } from "./pages/Login.jsx";
import { PlaceholderPage } from "./pages/PlaceholderPage.jsx";
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
        element: <PlaceholderPage title="Guests" />,
      },
      {
        path: "/rooms",
        element: <PlaceholderPage title="Rooms" />,
      },
      {
        path: "/reservations",
        element: <PlaceholderPage title="Reservations" />,
      },
      {
        path: "/check-in",
        element: <PlaceholderPage title="Check-in / Check-out" />,
      },
      {
        path: "/billing",
        element: <PlaceholderPage title="Billing" />,
      },
      {
        path: "/payments",
        element: <PlaceholderPage title="Payments" />,
      },
      {
        path: "/reports",
        element: <PlaceholderPage title="Reports" />,
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
