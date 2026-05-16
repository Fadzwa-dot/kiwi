import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Navbar() {
  const { username, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🥝</span>
          <span className="logo-text">Kiwi<span className="logo-accent">Portfolio</span></span>
        </Link>
      </div>
      
      <div className="navbar-menu">
        <Link to="/" className="nav-link">Dashboard</Link>
      </div>

      <div className="navbar-user">
        <div className="user-profile">
          <div className="user-avatar">{username ? username.charAt(0).toUpperCase() : 'U'}</div>
          <span className="user-name">{username}</span>
        </div>
        <button type="button" className="nav-logout-btn" onClick={logout}>
          Logout
        </button>
      </div>
    </nav>
  );
}
