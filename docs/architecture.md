# Architecture

The backend is a modular Django monolith. Each business area lives in its own Django app under `backend/apps/` and owns its models, serializers, API views, permissions, services, URLs, and tests.

This gives the MVP a simple deployment model while keeping future modules easy to add without moving existing code. New domains such as restaurant, housekeeping, maintenance, inventory, online booking, notifications, and customer portal should be added as new apps under `backend/apps/` when they are needed.

The frontend uses a feature-based structure under `frontend/src/features/`. Each future product area can grow its own pages, API clients, hooks, components, and tests without turning the app into a flat shared folder.

