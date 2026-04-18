import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:18090';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('kkrpa_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

// Handle 401 responses
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && typeof window !== 'undefined') {
            localStorage.removeItem('kkrpa_token');
            localStorage.removeItem('kkrpa_user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (data: { username: string; email: string; password: string }) =>
        api.post('/api/auth/register', data),
    login: (data: { username: string; password: string }) =>
        api.post('/api/auth/login', data),
    getMe: () => api.get('/api/auth/me'),
    getEdition: () => api.get('/api/auth/edition'),
};

// Workflow API
export const workflowAPI = {
    list: () => api.get('/api/workflows'),
    get: (id: number) => api.get(`/api/workflows/${id}`),
    create: (data: { name: string; description?: string; graph_data?: object }) =>
        api.post('/api/workflows', data),
    update: (id: number, data: object) => api.put(`/api/workflows/${id}`, data),
    delete: (id: number) => api.delete(`/api/workflows/${id}`),
    execute: (id: number) => api.post(`/api/workflows/${id}/execute`),
};

// Task API
export const taskAPI = {
    list: (params?: { workflow_id?: number; status?: string; limit?: number }) =>
        api.get('/api/tasks', { params }),
    get: (id: number) => api.get(`/api/tasks/${id}`),
    cancel: (id: number) => api.post(`/api/tasks/${id}/cancel`),
};

// Schedule API (Enterprise)
export const scheduleAPI = {
    list: () => api.get('/api/schedules'),
    create: (data: { workflow_id: number; cron_expression: string; timezone?: string }) =>
        api.post('/api/schedules', data),
    update: (id: number, data: object) => api.put(`/api/schedules/${id}`, data),
    delete: (id: number) => api.delete(`/api/schedules/${id}`),
};

export default api;
