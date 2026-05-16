import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { exchangeCodeForToken } from '../auth/oidc';

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const { completeLogin, logoutLocal } = useAuth();
  const [message, setMessage] = useState('Completing login...');

  useEffect(() => {
    const complete = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const error = params.get('error');

        if (error) {
          throw new Error(params.get('error_description') || error);
        }

        if (!code) {
          throw new Error('Missing authorization code.');
        }

        const idToken = await exchangeCodeForToken(code);
        completeLogin(idToken);
        navigate('/', { replace: true });
      } catch (e) {
        logoutLocal();
        setMessage(e.message || 'Authentication failed.');
      }
    };

    complete();
  }, [completeLogin, logoutLocal, navigate]);

  return <div className="screen-center">{message}</div>;
}