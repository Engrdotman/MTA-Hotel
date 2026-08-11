import { RouterProvider } from "react-router-dom";

import { router } from "./router.jsx";

export function App() {
  return <RouterProvider router={router} />;
}
