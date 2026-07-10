import axios from 'axios';

export const api = axios.create({ baseURL: 'http://localhost:8000/api' });

// CSRF token stored in module memory (not localStorage — keeps it out of XSS reach)
let csrfToken = null;

async function fetchCsrfToken() {
  try {
    const res = await axios.get('http://localhost:8000/api/csrf-token');
    csrfToken = res.data.csrf_token;
  } catch {
    console.warn('CSRF token fetch failed');
  }
}

// Fetch once on module load
fetchCsrfToken();

api.interceptors.request.use(async config => {
  // Attach JWT if available
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;

  // Attach CSRF token for state-changing requests
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

    // Refresh the CSRF token if it expired, then let the caller retry
    if (status === 403 && detail.toLowerCase().includes('csrf')) {
      await fetchCsrfToken();
      return Promise.reject(error);
    }

    // Expired / invalid JWT → clear session and redirect to login
    if (status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);
