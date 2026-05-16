export default function TransactionTable({ transactions }) {
  if (!transactions.length) {
    return <p className="empty-state">No transactions yet.</p>;
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Type</th>
          <th>Quantity</th>
          <th>Price</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {transactions.map((tx) => (
          <tr key={tx.transaction_id}>
            <td>{tx.ticker}</td>
            <td>{tx.transaction_type}</td>
            <td>{tx.quantity}</td>
            <td>{Number(tx.price).toFixed(2)}</td>
            <td>{new Date(tx.date_time).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}