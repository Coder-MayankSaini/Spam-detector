import React, { useState } from 'react';
import { EmailAnalysis } from './types';
import { useTheme } from './ThemeContext';

interface ResultDisplayProps {
  result: EmailAnalysis | null;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ result }) => {
  const [showFullText, setShowFullText] = useState(false);
  const [showOriginalText, setShowOriginalText] = useState(false);
  const { theme } = useTheme();

  if (!result) return null;

  const confidence = (result.confidence * 100).toFixed(1);
  const threshold = (result.threshold * 100).toFixed(1);
  const isOcrResult = result.source === 'ocr';

  return (
    <div className={`result-card ${result.is_spam ? 'spam-result' : 'ham-result'}`}>
      <div className="result-header">
        <div className="result-classification">
          <span className={`badge large ${result.is_spam ? 'spam' : 'ham'}`}>
            {result.is_spam ? '⚠️ Spam' : '✅ Not Spam'}
          </span>
          {isOcrResult && (
            <span className="source-badge">
              📷 OCR Analysis
            </span>
          )}
        </div>
        <div className="confidence-info">
          <div className={`confidence ${theme}`}>
            Confidence: {confidence}%
          </div>
          <div className="threshold">
            (Threshold: {threshold}%)
          </div>
        </div>
      </div>

      {result.processing_notes && (
        <div className="processing-info">
          <small>{result.processing_notes}</small>
        </div>
      )}

      {result.keywords && result.keywords.length > 0 && (
        <div className="keywords-section">
          <h4>Key Indicators:</h4>
          <div className="keywords">
            {result.keywords.map((keyword, index) => (
              <span key={index} className="keyword-tag">
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="text-section">
        <button
          onClick={() => setShowFullText(!showFullText)}
          className="toggle-text-btn"
        >
          {showFullText ? 'Hide' : 'Show'} analyzed text
        </button>
        {showFullText && (
          <div className="analyzed-text">
            <h5>Processed Text:</h5>
            <pre>{result.text}</pre>
          </div>
        )}
        
        {isOcrResult && result.extracted_text && result.extracted_text !== result.text && (
          <>
            <button
              onClick={() => setShowOriginalText(!showOriginalText)}
              className="toggle-text-btn"
              style={{ marginTop: '0.5rem' }}
            >
              {showOriginalText ? 'Hide' : 'Show'} raw OCR text
            </button>
            {showOriginalText && (
              <div className="analyzed-text">
                <h5>Raw OCR Output:</h5>
                <pre>{result.extracted_text}</pre>
                <small style={{ color: 'var(--text-secondary)' }}>
                  This is the raw text extracted from the image before processing
                </small>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
