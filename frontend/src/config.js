export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  cognitoDomain: import.meta.env.VITE_COGNITO_DOMAIN || '',
  cognitoClientId: import.meta.env.VITE_COGNITO_CLIENT_ID || '',
  cognitoRedirectUri: import.meta.env.VITE_COGNITO_REDIRECT_URI || `${window.location.origin}/auth/callback`,
  cognitoLogoutRedirectUri: import.meta.env.VITE_COGNITO_LOGOUT_REDIRECT_URI || window.location.origin,
  cognitoScope: import.meta.env.VITE_COGNITO_SCOPE || 'openid profile email',
};