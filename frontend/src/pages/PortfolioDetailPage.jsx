import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { getPortfolio, getPortfolioTransactions, buySecurity, sellSecurity } from '../api/kiwiApi';
import HoldingsTable from '../components/HoldingsTable';
import TransactionTable from '../components/TransactionTable';
import MessageBanner from '../components/MessageBanner';

export default function PortfolioDetailPage() {
  const { id } = useParams();
  const { token } = useAuth();
  
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [message, setMessage] = useState('');
  const [messageKind, setMessageKind] = useState('info');
  const [loading, setLoading] = useState(true);
  const [tradeLoading, setTradeLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('buy');

  const [buyForm, setBuyForm] = useState({ ticker: '', quantity: '' });
  const [sellForm, setSellForm] = useState({ ticker: '', quantity: '' });

  const flash = (text, kind = 'info') => {
    setMessage(text);
    setMessageKind(kind);
  };

  const loadData = async () => {
    if (!token || !id) return;
    try {
      const [portData, txsData] = await Promise.all([
        getPortfolio(token, id),
        getPortfolioTransactions(token, id),
      ]);
      setPortfolio(portData);
      setTransactions(txsData);
    } catch (e) {
      flash(e.message || 'Failed to load portfolio details.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id, token]);

  const handleTrade = async (e, type) => {
    e.preventDefault();
    try {
      setTradeLoading(true);
      if (type === 'buy') {
        await buySecurity(token, id, buyForm.ticker, buyForm.quantity);
        setBuyForm({ ticker: '', quantity: '' });
        flash('Buy order placed successfully.', 'success');
      } else {
        await sellSecurity(token, id, sellForm.ticker, sellForm.quantity);
        setSellForm({ ticker: '', quantity: '' });
        flash('Sell order placed successfully.', 'success');
      }
      await loadData();
    } catch (e) {
      flash(e.message || `${type === 'buy' ? 'Buy' : 'Sell'} order failed.`, 'error');
    } finally {
      setTradeLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="empty-state loader-text">Loading portfolio details...</div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="page-container">
        <MessageBanner message={message} kind="error" onClear={() => setMessage('')} />
        <div className="empty-state">Portfolio not found.</div>
        <Link to="/" className="link-button">&larr; Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Link to="/" className="back-link">&larr; Back to Portfolios</Link>
      
      <div className="portfolio-header">
        <h1 className="page-title">{portfolio.name}</h1>
        <p className="portfolio-desc-large">{portfolio.description}</p>
      </div>

      <MessageBanner message={message} kind={messageKind} onClear={() => setMessage('')} />

      <div className="detail-grid">
        <div className="main-col stack-large">
          <section className="glass-panel">
            <h2 className="section-title">Current Holdings</h2>
            <HoldingsTable holdings={portfolio.investments || []} />
          </section>

          <section className="glass-panel">
            <h2 className="section-title">Transaction History</h2>
            <TransactionTable transactions={transactions} />
          </section>
        </div>

        <div className="side-col">
          <section className="glass-panel sticky-panel">
            <h2 className="section-title">Trade</h2>
            
            <div className="tabs">
              <button 
                className={`tab-btn ${activeTab === 'buy' ? 'active' : ''}`}
                onClick={() => setActiveTab('buy')}
              >
                Buy
              </button>
              <button 
                className={`tab-btn ${activeTab === 'sell' ? 'active' : ''}`}
                onClick={() => setActiveTab('sell')}
              >
                Sell
              </button>
            </div>

            {activeTab === 'buy' ? (
              <form className="trade-form" onSubmit={(e) => handleTrade(e, 'buy')}>
                <div className="input-group">
                  <label>Ticker Symbol</label>
                  <input
                    required
                    placeholder="e.g. AAPL"
                    value={buyForm.ticker}
                    onChange={(e) => setBuyForm({ ...buyForm, ticker: e.target.value })}
                  />
                </div>
                <div className="input-group">
                  <label>Quantity</label>
                  <input
                    required
                    min="1"
                    step="1"
                    type="number"
                    placeholder="Number of shares"
                    value={buyForm.quantity}
                    onChange={(e) => setBuyForm({ ...buyForm, quantity: e.target.value })}
                  />
                </div>
                <button type="submit" className="primary-button w-100" disabled={tradeLoading}>
                  {tradeLoading ? 'Processing...' : 'Place Buy Order'}
                </button>
              </form>
            ) : (
              <form className="trade-form" onSubmit={(e) => handleTrade(e, 'sell')}>
                <div className="input-group">
                  <label>Ticker Symbol</label>
                  <input
                    required
                    placeholder="e.g. AAPL"
                    value={sellForm.ticker}
                    onChange={(e) => setSellForm({ ...sellForm, ticker: e.target.value })}
                  />
                </div>
                <div className="input-group">
                  <label>Quantity</label>
                  <input
                    required
                    min="1"
                    step="1"
                    type="number"
                    placeholder="Number of shares"
                    value={sellForm.quantity}
                    onChange={(e) => setSellForm({ ...sellForm, quantity: e.target.value })}
                  />
                </div>
                <button type="submit" className="sell-button w-100" disabled={tradeLoading}>
                  {tradeLoading ? 'Processing...' : 'Place Sell Order'}
                </button>
              </form>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
