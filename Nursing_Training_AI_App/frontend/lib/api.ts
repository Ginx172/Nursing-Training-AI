/**
 * API client cu interceptor pentru JWT auth headers.
 * Gestioneaza automat token refresh la 401.
 */
import axios from 'axios';

// When accessed via ngrok/external URL, use relative paths (Next.js rewrites proxy to backend).
// When running locally, use direct backend URL for faster response.
const isServer = typeof window === 'undefined';
const isExternalAccess = !isServer && !window.location.hostname.match(/^(localhost|127\.0\.0\.1)$/);
const API_URL = isExternalAccess ? '' : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Interceptor: adauga Authorization header pe fiecare request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Interceptor: la 401, incearca refresh token o singura data
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = typeof window !== 'undefined'
        ? localStorage.getItem('refresh_token')
        : null;

      if (refreshToken) {
        try {
          const res = await axios.post(`${API_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefresh } = res.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefresh);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch {
          // Refresh a esuat - clear tokens si redirect la login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
