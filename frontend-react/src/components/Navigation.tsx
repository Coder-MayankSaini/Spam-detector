import React from 'react';
import './Navigation.css';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  user: { email: string } | null;
  onLogout: () => void;
  onToggleTheme: () => void;
  theme: string;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentPage,
  onPageChange,
  user,
  onLogout,
  onToggleTheme,
  theme
}) => {
  const navItems = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'about', label: 'About', icon: 'ℹ️' },
    { id: 'contact', label: 'Contact', icon: '📧' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' }
  ];

  return (
    <header className="main-header">
      <div className="header-content">
        <div className="brand">
          <h1>🛡️ Spam Detector</h1>
          <p className="tagline">AI-powered email classification</p>
        </div>
        
        <nav className="main-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
              onClick={() => onPageChange(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="header-actions">
          <span className="user-info">
            <span className="user-email">{user?.email}</span>
          </span>
          <button 
            onClick={onToggleTheme}
            className="theme-toggle"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button 
            onClick={onLogout}
            className="logout-btn"
            aria-label="Logout"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </header>
  );
};
