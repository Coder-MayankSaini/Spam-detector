import { EmailAnalysis, HistoryItem, Stats, TrainingItem } from './types';
import { authService } from './authService';

const API_BASE = 'http://localhost:5000';

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
}

export const apiService = new ApiService();
