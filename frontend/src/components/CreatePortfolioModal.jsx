import { useState } from 'react';

export default function CreatePortfolioModal({ onClose, onSubmit, loading }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) return;
    onSubmit({ name, description });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Portfolio</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body stack">
          <div className="input-group">
            <label htmlFor="portfolio-name">Portfolio Name</label>
            <input
              id="portfolio-name"
              required
              placeholder="e.g. Tech Growth"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label htmlFor="portfolio-desc">Description</label>
            <textarea
              id="portfolio-desc"
              required
              placeholder="What is the strategy for this portfolio?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="modal-actions">
            <button type="button" className="ghost-button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="primary-button" disabled={loading || !name.trim() || !description.trim()}>
              {loading ? 'Creating...' : 'Create Portfolio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
