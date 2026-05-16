import { createContext, useContext, useEffect, useMemo, useState } from 'react';

import {
  buildLoginUrl,
  buildLogoutUrl,
  clearToken,
  decodeJwtPayload,
  getStoredToken,
  isTokenExpired,
  storeToken,
} from './oidc';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [claims, setClaims] = useState(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    const current = getStoredToken();
    if (current && !isTokenExpired(current)) {
      setToken(current);
      setClaims(decodeJwtPayload(current));
    } else {
      clearToken();
    }
    setAuthReady(true);
  }, []);

  useEffect(() => {
    if (!token) return;

    const timer = window.setInterval(() => {
      if (isTokenExpired(token)) {
        clearToken();
        setToken(null);
        setClaims(null);
        window.location.assign('/login');
      }
    }, 30000);

    return () => window.clearInterval(timer);
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      claims,
      authReady,
      isAuthenticated: Boolean(token),
      username: claims?.sub || '',
      async login() {
        const url = await buildLoginUrl();
        window.location.assign(url);
      },
      completeLogin(idToken) {
        storeToken(idToken);
        setToken(idToken);
        setClaims(decodeJwtPayload(idToken));
      },
      logout() {
        clearToken();
        setToken(null);
        setClaims(null);
        window.location.assign(buildLogoutUrl());
      },
      logoutLocal() {
        clearToken();
        setToken(null);
        setClaims(null);
      },
    }),
    [token, claims, authReady],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}