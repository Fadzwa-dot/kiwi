# Kiwi Frontend

React + Vite frontend for Assignment 5. It connects to the Flask backend API and uses AWS Cognito Hosted UI with OIDC Authorization Code Flow (PKCE).

## Features

- Cognito login/logout with code flow
- Protected dashboard route
- Bearer token attached to API requests
- Portfolio list, create, delete
- Holdings display per selected portfolio
- Buy and sell order forms
- Portfolio transaction history
- Graceful API error messages in UI

## Prerequisites

- Node.js 18+
- Backend API running (default: http://127.0.0.1:5000)
- Cognito User Pool + Hosted UI configured

## Setup

1. Copy environment template:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` values:

   - `VITE_API_BASE_URL` should usually remain `/api` for local proxy mode.
   - `VITE_COGNITO_DOMAIN` example: `https://my-domain.auth.us-east-1.amazoncognito.com`
   - `VITE_COGNITO_CLIENT_ID` must match your Cognito app client.
   - `VITE_COGNITO_REDIRECT_URI` must be allowed in Cognito callback URLs.
   - `VITE_COGNITO_LOGOUT_REDIRECT_URI` must be allowed in Cognito sign-out URLs.

3. Install and run:

   ```bash
   npm install
   npm run dev
   ```

4. Open http://localhost:5173

## Notes

- The frontend stores only the Cognito `id_token` in local storage.
- The token is never placed in URL query parameters and is never printed to console.
- The Vite dev server proxies `/api/*` to `http://127.0.0.1:5000/*` to avoid CORS issues during local development.
