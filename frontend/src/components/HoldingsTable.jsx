export default function HoldingsTable({ holdings }) {
  if (!holdings.length) {
    return <p className="empty-state">No holdings in this portfolio yet.</p>;
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Quantity</th>
        </tr>
      </thead>
      <tbody>
        {holdings.map((holding) => (
          <tr key={`${holding.ticker}-${holding.quantity}`}>
            <td>{holding.ticker}</td>
            <td>{holding.quantity}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}