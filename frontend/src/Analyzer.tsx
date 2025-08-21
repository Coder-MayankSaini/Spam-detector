import React, { useState, useCallback } from 'react';
import { EmailAnalysis } from './types';
import { apiService } from './apiService';
import { LoadingSpinner } from './LoadingSpinner';
import { useTheme } from './ThemeContext';

interface AnalyzerProps {
  onAnalysisComplete: (result: EmailAnalysis) => void;
}

export const Analyzer: React.FC<AnalyzerProps> = ({ onAnalysisComplete }) => {
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();

  const handleAnalyze = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!emailText.trim()) return;

    setLoading(true);
    setError(null);
    setProgress(0);

    // Simulate streaming progress
    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + Math.random() * 20, 90));
    }, 100);

    try {
      const result = await apiService.analyzeEmail(emailText);
      setProgress(100);
      setTimeout(() => {
        onAnalysisComplete(result);
        setLoading(false);
        clearInterval(progressInterval);
      }, 200);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setLoading(false);
      clearInterval(progressInterval);
    }
  }, [emailText, onAnalysisComplete]);

  const handleClear = () => {
    setEmailText('');
    setError(null);
  };

  return (
    <div className="analyzer-card">
      <h2>Analyze Email</h2>
      <form onSubmit={handleAnalyze}>
        <div className="form-group">
          <label htmlFor="emailText">Email Content</label>
          <textarea
            id="emailText"
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
            placeholder="Paste email content here..."
            rows={8}
            disabled={loading}
            className={theme}
          />
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        {loading && (
          <LoadingSpinner progress={progress} className="analysis-loading" />
        )}
        
        <div className="form-actions">
          <button 
            type="submit" 
            disabled={loading || !emailText.trim()}
            className="btn-primary"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
          <button 
            type="button" 
            onClick={handleClear}
            disabled={loading}
            className="btn-secondary"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};
