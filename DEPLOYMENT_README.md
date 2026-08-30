# PatientTriage.ai - Deployment Ready

## 1. Push to GitHub
Upload this entire project folder to a GitHub repository. The `.venv` folder has been removed.

## 2. Deploy Backend on Northflank
- Create a service from your GitHub repository.
- Build context: repository root.
- Dockerfile path: `backend/Dockerfile`.
- Expose port: `8000` using HTTP.
- Deploy.
- Test:
  - `/`
  - `/docs`
  - `/api/queue`

## 3. Connect the Frontend
After Northflank gives you the public backend URL, open:

`frontend/config.js`

Replace:

`YOUR_NORTHFLANK_BACKEND_URL`

with your actual URL, for example:

`https://your-service--your-project.code.run`

Commit and push the change.

## 4. Deploy Frontend on Vercel
- Import the same GitHub repository.
- Set Root Directory to: `frontend`
- Framework preset: Other / Static.
- Deploy.

## Architecture
Browser -> Vercel Frontend -> HTTPS API calls -> Northflank FastAPI -> ML model
