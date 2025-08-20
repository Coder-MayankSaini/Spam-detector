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
  private baseUrl = 'http://localhost:5000';
  private tokenKey = 'spam_detector_token';

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    const result = await response.json();
    this.setToken(result.access_token);
    return result;
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const result = await response.json();
    this.setToken(result.access_token);
    return result;
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
        this.removeToken();
        return { valid: false };
      }

      const result = await response.json();
      return { valid: true, user: result.user };
    } catch (error) {
      this.removeToken();
      return { valid: false };
    }
  }

  logout() {
    this.removeToken();
  }

  setToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  removeToken() {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}

export const authService = new AuthService();
export type { User, AuthResponse, LoginRequest, RegisterRequest };
