/**
 * APTI API Client Service
 * Kết nối tương tác trực tiếp với FastAPI Backend và Neon PostgreSQL
 * Hỗ trợ Dual-Mode: Tự động phát hiện Backend Online / Offline để trải nghiệm không bị gián đoạn.
 */

export class ApiClient {
  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
    this.tokenKey = 'apti_access_token';
    this.refreshTokenKey = 'apti_refresh_token';
    this.userKey = 'apti_user_profile';
    this.isOnline = false;
    this.listeners = [];

    this.checkHealth();
  }

  // Lắng nghe sự kiện thay đổi trạng thái đăng nhập
  onAuthStateChange(callback) {
    this.listeners.push(callback);
    callback(this.getCurrentUser());
  }

  notifyAuthChange() {
    const user = this.getCurrentUser();
    this.listeners.forEach(cb => {
      try { cb(user); } catch (e) { console.error(e); }
    });
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  getCurrentUser() {
    try {
      const u = localStorage.getItem(this.userKey);
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  }

  setSession(tokenResponse) {
    if (tokenResponse.access_token) {
      localStorage.setItem(this.tokenKey, tokenResponse.access_token);
    }
    if (tokenResponse.refresh_token) {
      localStorage.setItem(this.refreshTokenKey, tokenResponse.refresh_token);
    }
    if (tokenResponse.user) {
      localStorage.setItem(this.userKey, JSON.stringify(tokenResponse.user));
    }
    this.notifyAuthChange();
  }

  clearSession() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
    this.notifyAuthChange();
  }

  async checkHealth() {
    try {
      const res = await fetch(`${this.baseUrl}/health`, { method: 'GET', signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        this.isOnline = true;
        return true;
      }
    } catch {
      this.isOnline = false;
    }
    return this.isOnline;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: AbortSignal.timeout( options.timeout || 8000 )
      });

      // Nếu 401 Unauthorized và có Refresh Token -> Tự động xoay vòng Token
      if (response.status === 401 && this.getRefreshToken() && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh')) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          headers['Authorization'] = `Bearer ${this.getToken()}`;
          return fetch(url, { ...options, headers });
        }
      }

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || data.message || `Lỗi yêu cầu (${response.status})`);
      }

      this.isOnline = true;
      return data;
    } catch (err) {
      // Nếu lỗi kết nối, cập nhật isOnline = false
      if (err.name === 'TimeoutError' || err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        this.isOnline = false;
      }
      throw err;
    }
  }

  // 1. Xác thực & Tài khoản
  async register(email, fullName, password, phone = '') {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: email.trim(),
        full_name: fullName.trim(),
        password,
        phone: phone.trim() || undefined
      })
    });
    return res;
  }

  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.trim(), password })
    });
    this.setSession(res);
    return res;
  }

  async refreshToken() {
    try {
      const rawRefresh = this.getRefreshToken();
      if (!rawRefresh) return false;

      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: rawRefresh })
      });

      if (!res.ok) {
        this.clearSession();
        return false;
      }

      const data = await res.json();
      this.setSession(data);
      return true;
    } catch {
      this.clearSession();
      return false;
    }
  }

  async logout() {
    try {
      if (this.getToken()) {
        await this.request('/auth/logout', { method: 'POST' });
      }
    } catch {
      // Ignore network errors on logout
    } finally {
      this.clearSession();
    }
  }

  async getMe() {
    if (!this.getToken()) return null;
    try {
      const res = await this.request('/auth/me', { method: 'GET' });
      if (res && res.data) {
        localStorage.setItem(this.userKey, JSON.stringify(res.data));
        this.notifyAuthChange();
        return res.data;
      }
    } catch {
      return this.getCurrentUser();
    }
    return null;
  }

  // 2. Đề thi & Chấm điểm
  async getCategories() {
    return this.request('/quiz/categories', { method: 'GET' });
  }

  async getQuestions(categoryId = null, mode = 'PRACTICE', limit = 10) {
    let q = `?mode=${mode}&limit=${limit}`;
    if (categoryId && categoryId !== 'all') {
      q += `&category_id=${encodeURIComponent(categoryId)}`;
    }
    return this.request(`/quiz/questions${q}`, { method: 'GET' });
  }

  async submitQuiz(answers, timeSpentSeconds, categoryId = null, mode = 'PRACTICE') {
    return this.request('/quiz/submit', {
      method: 'POST',
      body: JSON.stringify({
        category_id: categoryId && categoryId !== 'all' ? categoryId : null,
        mode,
        time_spent_seconds: timeSpentSeconds,
        answers
      })
    });
  }

  async getQuizHistory(limit = 10) {
    return this.request(`/quiz/history?limit=${limit}`, { method: 'GET' });
  }

  async getLeaderboard(limit = 10) {
    return this.request(`/quiz/leaderboard?limit=${limit}`, { method: 'GET' });
  }

  // 3. Gói học & Đơn hàng VietQR
  async getPlans() {
    return this.request('/plans', { method: 'GET' });
  }

  async getMySubscription() {
    return this.request('/plans/my-subscription', { method: 'GET' });
  }

  async createOrder(planId, paymentMethod = 'VIETQR') {
    return this.request('/orders/checkout', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, payment_method: paymentMethod })
    });
  }

  async simulatePaymentSuccess(orderId) {
    const res = await this.request(`/orders/${orderId}/simulate-success`, { method: 'POST' });
    // Tải lại hồ sơ để cập nhật ngay subscription tier
    await this.getMe();
    return res;
  }

  // 4. Tài liệu Ebook
  async getDocuments() {
    return this.request('/documents', { method: 'GET' });
  }

  async getDocumentDownloadUrl(docId) {
    return this.request(`/documents/${docId}/download-link`, { method: 'GET' });
  }
}

// Singleton API instance
export const api = new ApiClient();
