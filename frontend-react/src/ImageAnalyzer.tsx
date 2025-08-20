import React, { useState, useRef } from 'react';
import { EmailAnalysis } from './types';
import { LoadingSpinner } from './LoadingSpinner';
import { apiService } from './apiService';

interface ImageAnalyzerProps {
  onAnalysisComplete: (result: EmailAnalysis) => void;
}

export const ImageAnalyzer: React.FC<ImageAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setError('Image file size must be less than 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setPreviewImage(result);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const analyzeImage = async () => {
    if (!previewImage) {
      setError('Please select an image first');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiService.analyzeImage(previewImage);

      // Add timestamp for consistency with text analysis
      const analysisResult: EmailAnalysis = {
        ...result,
        timestamp: new Date().toISOString()
      };

      onAnalysisComplete(analysisResult);
      
      // Clear the image after successful analysis
      setPreviewImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const clearImage = () => {
    setPreviewImage(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="analyzer-card">
      <h2>📷 Analyze Email Screenshot</h2>
      
      {!previewImage ? (
        <div
          className={`image-drop-zone ${dragOver ? 'drag-over' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">📁</div>
            <p>Drag & drop an email screenshot here</p>
            <p className="drop-zone-subtext">or click to browse files</p>
            <div className="supported-formats">
              Supports: JPG, PNG, GIF, WebP (max 10MB)
            </div>
          </div>
        </div>
      ) : (
        <div className="image-preview-container">
          <div className="image-preview">
            <img src={previewImage} alt="Email screenshot preview" />
            <button 
              className="clear-image-btn"
              onClick={clearImage}
              aria-label="Remove image"
            >
              ✕
            </button>
          </div>
          
          <div className="form-actions">
            <button
              className="btn-primary"
              onClick={analyzeImage}
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing Image...' : '🔍 Analyze Screenshot'}
            </button>
            <button
              className="btn-secondary"
              onClick={clearImage}
              disabled={isLoading}
            >
              Choose Different Image
            </button>
          </div>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      {isLoading && (
        <div className="loading-container">
          <LoadingSpinner />
          <p>Extracting text from image...</p>
          <div className="progress-steps">
            <div className="step">📷 Processing image</div>
            <div className="step">🔍 Extracting text (OCR)</div>
            <div className="step">🤖 Analyzing for spam</div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
          {error.includes('No text could be extracted') && (
            <div className="error-suggestions">
              <h4>Suggestions:</h4>
              <ul>
                <li>Ensure the image is clear and high resolution</li>
                <li>Make sure text is clearly visible and not too small</li>
                <li>Try adjusting image contrast or brightness</li>
                <li>Avoid images with complex backgrounds</li>
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="feature-info">
        <h4>📋 How it works:</h4>
        <ul>
          <li><strong>OCR Technology:</strong> Extracts text from your email screenshots</li>
          <li><strong>AI Analysis:</strong> Uses the same spam detection model as text input</li>
          <li><strong>Privacy:</strong> Images are processed locally and not stored</li>
          <li><strong>Accuracy:</strong> Works best with clear, high-contrast text</li>
        </ul>
      </div>
    </div>
  );
};
