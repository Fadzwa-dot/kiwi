export default function PortfolioList({ portfolios, selectedId, onSelect, onDelete }) {
  if (!portfolios.length) {
    return <p className="empty-state">No portfolios yet. Create one to get started.</p>;
  }

  return (
    <ul className="list-reset">
      {portfolios.map((portfolio) => (
        <li key={portfolio.id} className={`card ${selectedId === portfolio.id ? 'card-active' : ''}`}>
          <button
            type="button"
            className="card-button"
            onClick={() => onSelect(portfolio.id)}
          >
            <div className="card-title">{portfolio.name}</div>
            <div className="card-subtitle">{portfolio.description}</div>
          </button>
          <button
            type="button"
            className="danger-button"
            onClick={() => onDelete(portfolio.id, portfolio.name)}
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}