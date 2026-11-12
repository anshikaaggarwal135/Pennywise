import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api' });
api.interceptors.request.use(config => { const token = localStorage.getItem('pennywise_token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
api.interceptors.response.use(r => r, error => { if (error.response?.status === 401) { localStorage.removeItem('pennywise_token'); localStorage.removeItem('pennywise_user'); if (!location.pathname.startsWith('/login') && !location.pathname.startsWith('/register')) location.href = '/login'; } return Promise.reject(error); });
export default api;
