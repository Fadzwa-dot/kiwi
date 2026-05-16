import { apiRequest } from './client';

export async function ensureBackendUser(token, username) {
  try {
    await apiRequest(`/users/${encodeURIComponent(username)}`, { token });
  } catch (error) {
    if (error.status !== 404) {
      throw error;
    }
    await apiRequest('/users/', {
      token,
      method: 'POST',
      body: {
        username,
        password: 'oidc-user',
        firstname: username,
        lastname: 'Cognito',
        balance: 10000,
      },
    });
  }
}

export function getUserPortfolios(token, username) {
  return apiRequest(`/portfolios/user/${encodeURIComponent(username)}`, { token });
}

export function createPortfolio(token, username, name, description) {
  return apiRequest('/portfolios/', {
    token,
    method: 'POST',
    body: { username, name, description },
  });
}

export function deletePortfolio(token, portfolioId) {
  return apiRequest(`/portfolios/${portfolioId}`, {
    token,
    method: 'DELETE',
  });
}

export function getPortfolio(token, portfolioId) {
  return apiRequest(`/portfolios/${portfolioId}`, { token });
}

export function buySecurity(token, portfolioId, ticker, quantity) {
  return apiRequest('/trades/buy', {
    token,
    method: 'POST',
    body: {
      portfolio_id: Number(portfolioId),
      ticker: ticker.toUpperCase(),
      quantity: Number(quantity),
    },
  });
}

export async function sellSecurity(token, portfolioId, ticker, quantity) {
  const security = await apiRequest(`/securities/${encodeURIComponent(ticker.toUpperCase())}`, { token });
  return apiRequest('/trades/sell', {
    token,
    method: 'POST',
    body: {
      portfolio_id: Number(portfolioId),
      ticker: ticker.toUpperCase(),
      quantity: Number(quantity),
      sale_price: Number(security.price),
    },
  });
}

export function getPortfolioTransactions(token, portfolioId) {
  return apiRequest(`/portfolios/${portfolioId}/transactions`, { token });
}