# Deployment Guide for Render

This guide will help you deploy the Bilmo LLM API to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your HuggingFace API token (`HF_TOKEN`)
3. Git repository (GitHub, GitLab, or Bitbucket) with your code

## Step-by-Step Deployment Instructions

### Option 1: Deploy using render.yaml (Recommended)

1. **Push your code to a Git repository**
   - Make sure all files are committed and pushed to your repository
   - The repository should include:
     - `app.py`
     - `llm_client.py`
     - `extractor.py`
     - `prompts.py`
     - `schemas.py`
     - `requirements.txt`
     - `render.yaml`

2. **Connect your repository to Render**
   - Log in to Render dashboard: https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml` and configure the service

3. **Set Environment Variables**
   - In the Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add the following environment variable:
     - `HF_TOKEN`: Your HuggingFace API token (mark as "Secret")
   - Optionally add:
     - `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: "*")

4. **Deploy**
   - Render will automatically start building and deploying
   - Wait for the deployment to complete (usually 2-5 minutes)
   - Your API will be available at: `https://your-service-name.onrender.com`

### Option 2: Manual Deployment

1. **Create a new Web Service**
   - Log in to Render dashboard
   - Click "New +" → "Web Service"
   - Connect your Git repository

2. **Configure the Service**
   - **Name**: `bilmo-llm-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - `HF_TOKEN`: Your HuggingFace API token
   - `ALLOWED_ORIGINS`: (Optional) Comma-separated CORS origins

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application

## Post-Deployment

### Verify Deployment

1. **Health Check**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```
   Should return: `{"status": "healthy"}`

2. **Test API Endpoint**
   ```bash
   curl https://your-service-name.onrender.com/
   ```
   Should return: `{"status": "ok", "message": "Bilmo LLM API is running"}`

### API Endpoints

- `GET /` - Root endpoint (health check)
- `GET /health` - Health check endpoint
- `POST /chat` - Chat endpoint
- `POST /finalize` - Finalize endpoint

### Example API Call

```bash
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to buy a travel bag"}
    ],
    "mode": "default"
  }'
```

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `HF_TOKEN` | Yes | HuggingFace API token | - |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins | `*` |
| `PORT` | No | Port number (set by Render) | - |

## Troubleshooting

### Build Failures
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility (3.12.0)

### Runtime Errors
- Check Render logs: Dashboard → Your Service → Logs
- Verify `HF_TOKEN` is set correctly
- Ensure all required files are in the repository

### CORS Issues
- Set `ALLOWED_ORIGINS` environment variable with your frontend URL
- Format: `https://your-frontend.com,https://another-domain.com`

## Notes

- Render free tier services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid plan for always-on service
- Monitor usage and costs in Render dashboard

