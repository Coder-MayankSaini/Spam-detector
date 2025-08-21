import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { ForgotPassword } from './ForgotPassword';
import { ResetPassword } from './ResetPassword';
import './Auth.css';

type AuthView = 'login' | 'register' | 'forgot-password' | 'reset-password';

export const AuthComponent: React.FC = () => {
  const { login, register } = useAuth();
  const [currentView, setCurrentView] = useState<AuthView>('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [resetToken, setResetToken] = useState<string>('');

  // Check for reset token in URL on component mount
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      setResetToken(token);
      setCurrentView('reset-password');
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (currentView === 'login') {
        await login(formData.email, formData.password);
      } else if (currentView === 'register') {
        await register(formData.email, formData.password);
      }
      // The AuthContext will automatically trigger a re-render when authentication state changes
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToAuth = () => {
    setCurrentView('login');
    setError('');
    setFormData({ email: '', password: '' });
    // Clear URL parameters
    window.history.replaceState({}, document.title, window.location.pathname);
  };

  // Show forgot password component
  if (currentView === 'forgot-password') {
    return <ForgotPassword onBackToAuth={handleBackToAuth} />;
  }

  // Show reset password component
  if (currentView === 'reset-password') {
    return <ResetPassword token={resetToken} onBackToAuth={handleBackToAuth} />;
  }

  const isLogin = currentView === 'login';

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>🛡️ SpamWall</h2>
          <p>Sign in to access your personalized spam detection dashboard</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('login');
              setError('');
              setFormData({ email: '', password: '' });
            }}
          >
            Login
          </button>
          <button
            className={`auth-tab ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setCurrentView('register');
              setError('');
              setFormData({ email: '', password: '' });
            }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-error">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              disabled={loading}
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              disabled={loading}
              placeholder={isLogin ? "Enter your password" : "Create a password (min 6 chars)"}
              minLength={6}
            />
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={loading || !formData.email || !formData.password}
          >
            {loading ? (
              <span>
                <span className="spinner"></span>
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </span>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>

          {isLogin && (
            <div className="forgot-password-link">
              <button
                type="button"
                className="link-button"
                onClick={() => setCurrentView('forgot-password')}
              >
                Forgot your password?
              </button>
            </div>
          )}
        </form>

        <div className="auth-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              className="auth-switch"
              onClick={() => {
                setCurrentView(isLogin ? 'register' : 'login');
                setError('');
                setFormData({ email: '', password: '' });
              }}
            >
              {isLogin ? 'Create one' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
