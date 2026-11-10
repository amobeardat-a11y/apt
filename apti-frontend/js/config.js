/**
 * APTI Frontend Environment Configuration
 * Quản lý cấu hình kết nối API cho Vercel (Production) & Local (Development)
 */

// URL Backend FastAPI triển khai trên Render
// Thay thế bằng domain Render thực tế của bạn (ví dụ: https://apti-backend.onrender.com/api/v1)
export const DEFAULT_PRODUCTION_API_URL = 'https://apti-backend.onrender.com/api/v1';

export function getApiBaseUrl() {
  // 1. Kiểm tra URL override từ localStorage (hữu ích cho việc test nhanh các staging/dev url)
  const storedUrl = localStorage.getItem('apti_api_base_url');
  if (storedUrl) return storedUrl;

  // 2. Kiểm tra biến môi trường được inject từ HTML/Vercel script (nếu có)
  if (window.__APTI_API_URL__) return window.__APTI_API_URL__;

  // 3. Nếu đang chạy Localhost (Development)
  const host = window.location.hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '') {
    return 'http://127.0.0.1:8000/api/v1';
  }

  // 4. Mặc định trên Production (Vercel)
  return DEFAULT_PRODUCTION_API_URL;
}

