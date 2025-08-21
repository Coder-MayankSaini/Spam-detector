import React, { useState } from 'react';
import { Analyzer } from '../Analyzer';
import { ImageAnalyzer } from '../ImageAnalyzer';
import { ResultDisplay } from '../ResultDisplay';
import { History } from '../History';
import { EmailAnalysis } from '../types';
import './HomePage.css';

type AnalysisTab = 'text' | 'image';

export const HomePage: React.FC = () => {
  const [result, setResult] = useState<EmailAnalysis | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<AnalysisTab>('text');

  const handleAnalysisComplete = (analysisResult: EmailAnalysis) => {
    setResult(analysisResult);
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="home-page">
      <div className="welcome-section">
        <div className="welcome-content">
          <h2>🛡️ Welcome to AI-Powered Spam Detection</h2>
          <p>Protect your inbox with advanced machine learning technology. Analyze emails instantly with both text and image analysis capabilities.</p>
          <div className="feature-highlights">
            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <span>AI-Powered Analysis</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📝</span>
              <span>Text Detection</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📷</span>
              <span>Image OCR</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <span>Real-time Results</span>
            </div>
          </div>
        </div>
      </div>

      <main className="home-main">
        <div className="main-grid">
          <div className="analyzer-section">
            <div className="analyzer-tabs">
              <button
                className={`tab-button ${activeTab === 'text' ? 'active' : ''}`}
                onClick={() => setActiveTab('text')}
              >
                📝 Text Analysis
              </button>
              <button
                className={`tab-button ${activeTab === 'image' ? 'active' : ''}`}
                onClick={() => setActiveTab('image')}
              >
                📷 Image Analysis
              </button>
            </div>
            
            <div className="tab-content">
              {activeTab === 'text' ? (
                <Analyzer onAnalysisComplete={handleAnalysisComplete} />
              ) : (
                <ImageAnalyzer onAnalysisComplete={handleAnalysisComplete} />
              )}
            </div>
            
            {result && <ResultDisplay result={result} />}
          </div>
          
          <div className="history-section">
            <History refreshTrigger={refreshTrigger} />
          </div>
        </div>
      </main>
      
      <footer className="home-footer">
        <p>Demo model with OCR support - not production ready. Improve dataset for real-world use.</p>
      </footer>
    </div>
  );
};
