import { useState } from 'react';
import { Navigate } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import MessageBanner from '../components/MessageBanner';

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      await login();
    } catch (e) {
      setError(e.message || 'Unable to begin login flow.');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-glow-1"></div>
      <div className="login-glow-2"></div>
      
      <div className="glass-card login-card">
        <div className="login-header">
          <span className="logo-icon-large">🥝</span>
          <h1>Kiwi<span className="logo-accent">Portfolio</span></h1>
          <p className="login-subtitle">Your wealth, visualized.</p>
        </div>
        
        <div className="login-body">
          <p className="login-desc">Sign in with AWS Cognito to access your dashboard, track holdings, and execute trades seamlessly.</p>
          <MessageBanner message={error} kind="error" onClear={() => setError('')} />
          
          <button type="button" className="primary-button login-button w-100" onClick={handleLogin} disabled={loading}>
            {loading ? 'Redirecting...' : 'Sign In / Register'}
          </button>
        </div>
      </div>
    </div>
  );
}