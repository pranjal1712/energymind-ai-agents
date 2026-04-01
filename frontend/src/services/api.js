import Cookies from 'js-cookie';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = {
  getToken: () => Cookies.get('access_token') || localStorage.getItem('access_token'),
  setToken: (token) => {
    localStorage.setItem('access_token', token);
    const consent = localStorage.getItem('cookie_consent');
    if (consent === 'accepted') {
      Cookies.set('access_token', token, { expires: 7, secure: true, sameSite: 'strict' });
    }
  },
  clearToken: () => {
    localStorage.removeItem('access_token');
    Cookies.remove('access_token');
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.clearToken();
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }

      const errorData = await response.json().catch(() => ({ detail: 'Network response was not ok' }));
      let message = 'An error occurred';
      
      if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        message = errorData.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
      } else if (errorData.detail) {
        message = JSON.stringify(errorData.detail);
      }
      
      throw new Error(message);
    }

    return response.json();
  },

  async login(username, password) {
    // OAuth2PasswordRequestForm expects form-data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${BASE_URL}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  },

  async signup(username, email, password) {
    return this.request('/signup', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  },

  async googleAuth(token) {
    const data = await this.request('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
    this.setToken(data.access_token);
    return data;
  },

  async getMe() {
    const token = this.getToken();
    if (!token || token === 'undefined' || token === 'null') {
      return { name: 'Guest User', email: '' };
    }
    return this.request('/me');
  },

  async getHistory() {
    const token = this.getToken();
    if (!token || token === 'undefined' || token === 'null') {
      return [];
    }
    return this.request('/history');
  },

  async deleteHistoryItem(id) {
    return this.request(`/history/${id}`, {
      method: 'DELETE',
    });
  },

  async runResearch(query, threadId = null) {
    const body = { query };
    if (threadId) body.thread_id = threadId;
    
    return this.request('/research', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }
};

export default api;
