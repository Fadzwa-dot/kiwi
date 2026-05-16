import { config } from '../config';

const TOKEN_STORAGE_KEY = 'kiwi_id_token';
const CODE_VERIFIER_KEY = 'kiwi_pkce_verifier';

function base64UrlEncode(input) {
  const bytes = typeof input === 'string' ? new TextEncoder().encode(input) : input;
  let str = '';
  bytes.forEach((b) => {
    str += String.fromCharCode(b);
  });
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function randomString(length = 64) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const buffer = new Uint8Array(length);
  crypto.getRandomValues(buffer);
  return Array.from(buffer, (v) => chars[v % chars.length]).join('');
}

async function sha256(input) {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return new Uint8Array(hash);
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function storeToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function decodeJwtPayload(token) {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const json = atob(normalized);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function isTokenExpired(token) {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== 'number') {
    return true;
  }
  const now = Math.floor(Date.now() / 1000);
  return payload.exp <= now;
}

function assertCognitoConfig() {
  if (!config.cognitoDomain || !config.cognitoClientId) {
    throw new Error('Missing Cognito configuration. Set VITE_COGNITO_DOMAIN and VITE_COGNITO_CLIENT_ID.');
  }
}

export async function buildLoginUrl() {
  assertCognitoConfig();
  const verifier = randomString(96);
  const challenge = base64UrlEncode(await sha256(verifier));
  sessionStorage.setItem(CODE_VERIFIER_KEY, verifier);

  const params = new URLSearchParams({
    client_id: config.cognitoClientId,
    response_type: 'code',
    scope: config.cognitoScope,
    redirect_uri: config.cognitoRedirectUri,
    code_challenge_method: 'S256',
    code_challenge: challenge,
  });

  return `${config.cognitoDomain}/login?${params.toString()}`;
}

export async function exchangeCodeForToken(code) {
  assertCognitoConfig();
  const verifier = sessionStorage.getItem(CODE_VERIFIER_KEY);
  if (!verifier) {
    throw new Error('Missing PKCE verifier. Start login again.');
  }

  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: config.cognitoClientId,
    code,
    redirect_uri: config.cognitoRedirectUri,
    code_verifier: verifier,
  });

  const response = await fetch(`${config.cognitoDomain}/oauth2/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  });

  if (!response.ok) {
    let detail = 'Token exchange failed.';
    try {
      const data = await response.json();
      detail = data.error_description || data.error || detail;
    } catch {
      // noop
    }
    throw new Error(detail);
  }

  const tokenData = await response.json();
  if (!tokenData.id_token) {
    throw new Error('No id_token returned from Cognito.');
  }

  sessionStorage.removeItem(CODE_VERIFIER_KEY);
  return tokenData.id_token;
}

export function buildLogoutUrl() {
  assertCognitoConfig();
  const params = new URLSearchParams({
    client_id: config.cognitoClientId,
    logout_uri: config.cognitoLogoutRedirectUri,
  });
  return `${config.cognitoDomain}/logout?${params.toString()}`;
}