// UPDATED authService.ts with debugging and timeout handling
// Copy this into your frontend/src/authService.ts

interface User {
  id: number;
  email: string;
}

interface AuthResponse {
  message: string;
  access_token: string;
  user: User;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
}

class AuthService {
  // Try local backend first, then Railway (you can switch this)
  private baseUrl = 'http://localhost:5001'; // For local testing
  // private baseUrl = 'https://web-production-02077.up.railway.app'; // For Railway
  
  private tokenKey = 'spamwall_token';

  private async makeAuthRequest(endpoint: string, data: any): Promise<any> {
    console.log(`🔄 Making request to: ${this.baseUrl}${endpoint}`);
    console.log('📨 Request data:', { email: data.email, password: '***' });
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.log('⏰ Request timed out, aborting...');
        controller.abort();
      }, 30000); // 30 second timeout
      
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      
      console.log(`📊 Response status: ${response.status}`);
      console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const error = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
        console.error('❌ Request failed:', error);
        throw new Error(error.error || `Request failed with status ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Request successful:', { ...result, access_token: result.access_token ? 'present' : 'missing' });
      return result;

    } catch (error) {
      console.error('🚨 Request exception:', error);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. The server may be slow or unreachable.');
      }
      
      if (error.message?.includes('Failed to fetch')) {
        throw new Error('Cannot connect to server. Check if backend is running and CORS is configured.');
      }
      
      throw error;
    }
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    console.log('📝 Starting registration...');
    
    // Validate input on frontend
    if (!data.email || !data.password) {
      throw new Error('Email and password are required');
    }
    
    if (data.email.trim().length < 3) {
      throw new Error('Email must be at least 3 characters');
    }
    
    if (data.password.length < 6) {
      throw new Error('Password must be at least 6 characters');
    }
    
    try {
      const result = await this.makeAuthRequest('/register', data);
      this.setToken(result.access_token);
      console.log('🎉 Registration successful!');
      return result;
    } catch (error) {
      console.error('❌ Registration failed:', error);
      throw error;
    }
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    console.log('🔑 Starting login...');
    
    // Validate input on frontend
    if (!data.email || !data.password) {
      throw new Error('Email and password are required');
    }
    
    if (data.email.trim().length < 3) {
      throw new Error('Email must be at least 3 characters');
    }
    
    if (data.password.length < 1) {
      throw new Error('Password is required');
    }
    
    try {
      const result = await this.makeAuthRequest('/login', data);
      this.setToken(result.access_token);
      console.log('🎉 Login successful!');
      return result;
    } catch (error) {
      console.error('❌ Login failed:', error);
      throw error;
    }
  }

  async forgotPassword(email: string): Promise<{ message: string }> {
    console.log('🔄 Password reset request...');
    
    const response = await fetch(`${this.baseUrl}/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send reset email');
    }

    return response.json();
  }

  async resetPassword(token: string, password: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to reset password');
    }

    return response.json();
  }

  async verifyToken(): Promise<{ valid: boolean; user?: User }> {
    const token = this.getToken();
    if (!token) {
      return { valid: false };
    }

    try {
      const response = await fetch(`${this.baseUrl}/verify-token`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.log('🔄 Token invalid, removing...');
        this.removeToken();
        return { valid: false };
      }

      const result = await response.json();
      return { valid: true, user: result.user };
    } catch (error) {
      console.error('❌ Token verification failed:', error);
      this.removeToken();
      return { valid: false };
    }
  }

  logout() {
    console.log('👋 Logging out...');
    this.removeToken();
  }

  setToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
    console.log('💾 Token saved to localStorage');
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  removeToken() {
    localStorage.removeItem(this.tokenKey);
    console.log('🗑️ Token removed from localStorage');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // Debug method to test connectivity
  async testConnection(): Promise<boolean> {
    console.log('🔍 Testing backend connection...');
    
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });
      
      console.log(`📊 Health check status: ${response.status}`);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Backend is reachable:', result);
        return true;
      } else {
        console.log('⚠️ Backend responded but with error');
        return false;
      }
      
    } catch (error) {
      console.error('❌ Backend unreachable:', error);
      return false;
    }
  }
}

export const authService = new AuthService();
export type { User, AuthResponse, LoginRequest, RegisterRequest };
