import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const API_TIMEOUTS = {
  default: Number(import.meta.env.VITE_API_TIMEOUT_MS || 18000),
  ai: Number(import.meta.env.VITE_AI_TIMEOUT_MS || 60000),
  upload: Number(import.meta.env.VITE_UPLOAD_TIMEOUT_MS || 60000),
};

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUTS.default,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const isApiTimeoutError = (error) => (
  error?.code === 'ECONNABORTED' ||
  error?.name === 'AbortError' ||
  String(error?.message || '').toLowerCase().includes('timeout')
);

export const withApiTimeout = (kind = 'default', config = {}) => ({
  ...config,
  timeout: config.timeout ?? API_TIMEOUTS[kind] ?? API_TIMEOUTS.default,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (isApiTimeoutError(error)) {
      error.isTimeout = true;
      error.friendlyMessage = 'Du lieu realtime dang cham. He thong se dung cache/du lieu du phong neu co.';
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

export const getApiErrorMessage = (error, fallback = 'Khong the ket noi API') => {
  if (error?.friendlyMessage) return error.friendlyMessage;
  if (isApiTimeoutError(error)) {
    return 'Du lieu realtime dang cham. Vui long thu lai, cac khoi co cache se tiep tuc hien thi du lieu du phong.';
  }
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(', ');
  }
  return detail || error?.response?.data?.message || error?.response?.data?.meta?.error || error?.message || fallback;
};

export const settledValue = (result, fallback = null) => (
  result?.status === 'fulfilled' ? result.value : fallback
);

export const settledErrorMessage = (result, fallback) => (
  result?.status === 'rejected' ? getApiErrorMessage(result.reason, fallback) : null
);

export const fetchWithTimeout = async (url, options = {}, timeoutMs = API_TIMEOUTS.default) => {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      ...options,
      signal: options.signal || controller.signal,
    });
  } finally {
    window.clearTimeout(timer);
  }
};
