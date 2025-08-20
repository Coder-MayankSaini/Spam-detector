import React from 'react';

interface LoadingSpinnerProps {
  progress?: number;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  progress, 
  className = '' 
}) => {
  return (
    <div className={`loading-container ${className}`}>
      <div className="loading-spinner">
        <div className="spinner-circle"></div>
      </div>
      {progress !== undefined && (
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          ></div>
        </div>
      )}
    </div>
  );
};
