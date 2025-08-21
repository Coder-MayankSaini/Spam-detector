import { EmailAnalysis, HistoryItem, Stats, TrainingItem } from './types';
import { authService } from './authService';

// Use environment variable for API base URL, fallback to Railway production
const API_BASE = process.env.REACT_APP_API_URL || 'https://web-production-02077.up.railway.app';

// Debug logging
console.log('API Service initialized with:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  API_BASE,
  NODE_ENV: process.env.NODE_ENV
});

class ApiService {
  async analyzeEmail(emailText: string): Promise<EmailAnalysis> {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify({ text: emailText })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
      const error = await response.json();
      throw new Error(error.error || 'Analysis failed');
    }
    
    return response.json();
  }

  async analyzeImage(imageData: string): Promise<EmailAnalysis> {
    const response = await fetch(`${API_BASE}/analyze-image`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify({ image: imageData })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
      const error = await response.json();
      throw new Error(error.error || 'Image analysis failed');
    }
    
    return response.json();
  }

  async getHistory(): Promise<HistoryItem[]> {
    const response = await fetch(`${API_BASE}/history`, {
      headers: authService.getAuthHeaders()
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
      throw new Error('Failed to fetch history');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  }

  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE}/stats`, {
      headers: authService.getAuthHeaders()
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
      throw new Error('Failed to fetch stats');
    }
    
    return response.json();
  }

  async retrain(trainingData: TrainingItem[]): Promise<any> {
    const response = await fetch(`${API_BASE}/retrain`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify({ training_data: trainingData })
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        authService.logout();
        window.location.reload();
        return Promise.reject(new Error('Session expired. Please login again.'));
      }
      const error = await response.json();
      throw new Error(error.error || 'Retraining failed');
    }
    
    return response.json();
  }

  async submitContactForm(formData: { name: string; email: string; subject: string; message: string }): Promise<any> {
    const response = await fetch(`${API_BASE}/contact`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: formData.name,
        email: formData.email,
        message: `Subject: ${formData.subject}\n\n${formData.message}`
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send message');
    }
    
    return response.json();
  }

  async forgotPassword(email: string): Promise<any> {
    const response = await fetch(`${API_BASE}/forgot-password`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send reset email');
    }
    
    return response.json();
  }

  async resetPassword(token: string, password: string): Promise<any> {
    const response = await fetch(`${API_BASE}/reset-password`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to reset password');
    }
    
    return response.json();
  }
}

export const apiService = new ApiService();
