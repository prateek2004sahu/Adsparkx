# API Authentication Guide

## Overview
Our platform uses OAuth 2.0 and API key-based authentication for all API endpoints.

## API Key Authentication

### Generating an API Key
1. Log in to your dashboard at app.adsparkx.com
2. Navigate to Settings > Developer > API Keys
3. Click "Generate New Key"
4. Copy and store your key securely — it will not be shown again

### Using API Keys in Requests
Include your API key in the `Authorization` header:
```
Authorization: Bearer YOUR_API_KEY
```

### Common Authentication Errors

**401 Unauthorized**
- Cause: Invalid or expired API key
- Fix: Regenerate the key from the dashboard

**403 Forbidden**
- Cause: API key lacks required permissions
- Fix: Update key permissions under Settings > Developer > Permissions

**429 Too Many Requests**
- Cause: Rate limit exceeded (default: 100 requests/minute)
- Fix: Implement exponential backoff; upgrade plan for higher limits

## OAuth 2.0 Authentication

### Authorization Flow
1. Redirect user to: `https://auth.adsparkx.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=read write`
2. Exchange authorization code for access token:
```
POST https://auth.adsparkx.com/oauth/token
{
  "grant_type": "authorization_code",
  "code": "AUTH_CODE",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
```
3. Access token expires in 3600 seconds; use refresh token to renew

### Token Refresh
```
POST https://auth.adsparkx.com/oauth/token
{
  "grant_type": "refresh_token",
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

## Security Best Practices
- Never commit API keys to version control
- Rotate keys every 90 days
- Use environment variables to store credentials
- Enable IP whitelisting for production keys
- Monitor API usage in the dashboard for anomalies

## Rate Limits by Plan
| Plan       | Requests/Minute | Daily Limit  |
|------------|-----------------|--------------|
| Free       | 10              | 500          |
| Starter    | 50              | 5,000        |
| Pro        | 200             | 50,000       |
| Enterprise | Custom          | Unlimited    |
