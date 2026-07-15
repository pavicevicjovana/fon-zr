import axios from 'axios';

export const api = axios.create({ baseURL: 'http://localhost:8000/api' });


let csrfToken = null;

async function fetchCsrfToken() {
  try {
    const res = await axios.get('http://localhost:8000/api/csrf-token');
    csrfToken = res.data.csrf_token;
  } catch {
    console.warn('CSRF token fetch failed');
  }
}


fetchCsrfToken();

api.interceptors.request.use(async config => {
 
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;

  const method = config.method?.toLowerCase();
  if (['post', 'put', 'delete', 'patch'].includes(method)) {
    if (!csrfToken) await fetchCsrfToken();
    if (csrfToken) config.headers['X-CSRF-Token'] = csrfToken;
  }

  return config;
});

api.interceptors.response.use(
  response => response,
  async error => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail ?? '';

    
    if (status === 403 && detail.toLowerCase().includes('csrf')) {
      await fetchCsrfToken();
      return Promise.reject(error);
    }

    
    if (status === 401) {
      const isLoginRequest = error.config?.url?.includes('/users/login');

      if (!isLoginRequest) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
