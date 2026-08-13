# Frontend Deployment on Vercel

## Configuration Files Created
- `vercel.json` - Build configuration for Vercel
- `.vercelignore` - Excludes backend files from deployment

## Environment Variables

Set these in Vercel project settings → Environment Variables:

### For Development (Preview Deployments)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### For Production
```
VITE_API_BASE_URL=https://your-backend-url.com/api
```

Replace `https://your-backend-url.com` with your actual backend domain.

## Deployment Steps

1. **Connect Repository**
   - Push code to GitHub
   - Import project in Vercel
   - Select `main` or feature branch

2. **Configure Environment**
   - Go to Project Settings → Environment Variables
   - Add `VITE_API_BASE_URL` for your environment

3. **Deploy**
   - Vercel automatically builds from `frontend/dist`
   - Frontend deployed to `your-vercel-url.vercel.app`

## How It Works

```
vercel.json Configuration:
├── buildCommand: cd frontend && npm run build
├── outputDirectory: frontend/dist
├── env: VITE_API_BASE_URL
└── envPrefix: VITE_
```

Vercel will:
1. Run `npm run build` inside the `frontend` folder
2. Use `frontend/dist` as the output
3. Inject environment variables starting with `VITE_`

## Frontend API Configuration

Your frontend uses this in API calls:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
```

This automatically uses:
- Development: `http://localhost:8000/api` (local)
- Production: Your configured `VITE_API_BASE_URL` (Vercel)

## CORS Configuration

Make sure your backend's `.env` includes:
```env
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-url.vercel.app
```

## Troubleshooting

### Error: "Failed to read Django application settings"
✅ **Fixed** - `vercel.json` and `.vercelignore` now properly configure frontend-only deployment

### API calls failing in production
→ Check that `VITE_API_BASE_URL` environment variable is set in Vercel

### CORS errors
→ Add your Vercel URL to `DJANGO_CORS_ALLOWED_ORIGINS` in backend `.env`

## Backend Deployment

Backend should be deployed separately:
- Option 1: Railway, Render, or Heroku (free/cheap options)
- Option 2: AWS, GCP, or Azure
- Option 3: Your own server

Set `VITE_API_BASE_URL` to wherever your backend is deployed.
