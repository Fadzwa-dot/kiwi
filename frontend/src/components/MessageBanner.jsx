export default function MessageBanner({ message, kind = 'info', onClear }) {
  if (!message) return null;

  return (
    <div className={`banner banner-${kind}`} role="alert">
      <span>{message}</span>
      {onClear ? (
        <button type="button" className="link-button" onClick={onClear}>
          Dismiss
        </button>
      ) : null}
    </div>
  );
}