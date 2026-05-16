import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { createPortfolio, deletePortfolio, ensureBackendUser, getUserPortfolios } from '../api/kiwiApi';
import MessageBanner from '../components/MessageBanner';
import CreatePortfolioModal from '../components/CreatePortfolioModal';

export default function DashboardPage() {
  const { token, username } = useAuth();
  const navigate = useNavigate();
  
  const [portfolios, setPortfolios] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [message, setMessage] = useState('');
  const [messageKind, setMessageKind] = useState('info');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const flash = (text, kind = 'info') => {
    setMessage(text);
    setMessageKind(kind);
  };

  const loadPortfolios = async () => {
    if (!token || !username) return;
    const list = await getUserPortfolios(token, username);
    setPortfolios(list);
  };

  useEffect(() => {
    const bootstrap = async () => {
      if (!token || !username) return;
      try {
        setLoading(true);
        await ensureBackendUser(token, username);
        await loadPortfolios();
      } catch (e) {
        flash(e.message || 'Failed to load portfolios.', 'error');
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, [token, username]);

  const handleCreatePortfolio = async ({ name, description }) => {
    try {
      setActionLoading(true);
      await createPortfolio(token, username, name, description);
      setShowCreateModal(false);
      await loadPortfolios();
      flash('Portfolio created successfully.', 'success');
    } catch (e) {
      flash(e.message || 'Failed to create portfolio.', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeletePortfolio = async (e, portfolioId, portfolioName) => {
    e.stopPropagation();
    if (!window.confirm(`Delete portfolio "${portfolioName}"?`)) {
      return;
    }
    try {
      setActionLoading(true);
      await deletePortfolio(token, portfolioId);
      await loadPortfolios();
      flash('Portfolio deleted successfully.', 'success');
    } catch (e) {
      flash(e.message || 'Unable to delete portfolio. It may still contain holdings.', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="page-container">
      <MessageBanner message={message} kind={messageKind} onClear={() => setMessage('')} />

      <div className="page-header">
        <h1 className="page-title">My Portfolios</h1>
        <button className="primary-button add-btn" onClick={() => setShowCreateModal(true)}>
          <span className="icon">+</span> New Portfolio
        </button>
      </div>

      {loading ? (
        <div className="empty-state loader-text">Loading portfolios...</div>
      ) : portfolios.length === 0 ? (
        <div className="card empty-card">
          <div className="empty-state-icon">📁</div>
          <p>You don't have any portfolios yet.</p>
          <button className="secondary-button mt-4" onClick={() => setShowCreateModal(true)}>Create Your First Portfolio</button>
        </div>
      ) : (
        <div className="portfolio-grid">
          {portfolios.map(p => (
            <div
              key={p.id}
              className="glass-card clickable-card"
              onClick={() => navigate(`/portfolio/${p.id}`)}
            >
              <div className="card-header">
                <div>
                  <h3 className="card-title">{p.name}</h3>
                  <span className="card-id">#{p.id}</span>
                </div>
                {p.owner === username && (
                  <button
                    className="danger-icon-button"
                    onClick={(e) => handleDeletePortfolio(e, p.id, p.name)}
                    title="Delete Portfolio"
                    disabled={actionLoading}
                  >
                    &times;
                  </button>
                )}
              </div>
              <p className="card-desc">{p.description}</p>
              <div className="card-footer">
                <span className="action-text">View Details &rarr;</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreatePortfolioModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreatePortfolio}
          loading={actionLoading}
        />
      )}
    </div>
  );
}