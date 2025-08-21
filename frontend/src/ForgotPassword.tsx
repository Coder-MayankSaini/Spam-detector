import React, { useState } from 'react';
import { apiService } from './apiService';
import './Auth.css';

interface ForgotPasswordProps {
  onBackToAuth: () => void;
}

export const ForgotPassword: React.FC<ForgotPasswordProps> = ({ onBackToAuth }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setMessage('');

    if (!email.trim()) {
      setError('Email is required');
      setIsSubmitting(false);
      return;
    }

    try {
      const result = await apiService.forgotPassword(email);
      setMessage(result.message);
      setEmail('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset email');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>🔐 Forgot Password</h2>
          <p>Enter your email address and we'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          {message && <div className="success-message">{message}</div>}
          
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              required
              disabled={isSubmitting}
            />
          </div>

          <button 
            type="submit" 
            className="auth-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div className="auth-links">
          <p>
            <button type="button" onClick={onBackToAuth} className="link-button">
              Back to Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
