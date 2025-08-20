import axios from 'axios';

const api = axios.create({
    baseURL: 'https://web-tradingproject.jm.ordago.local/api',
});

api.interceptors.request.use(
    config => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = 'Bearer ' + token;
        }
        return config;
    },
    error => {
        Promise.reject(error)
    }
);

// Optionnel: Intercepteur pour gérer l'expiration du token (refresh token)
api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');
            try {
                const rs = await axios.post('https://web-tradingproject.jm.ordago.local/api/login/refresh/', {
                    refresh: refreshToken
                });
                const { access } = rs.data;
                localStorage.setItem('access_token', access);
                api.defaults.headers.common['Authorization'] = 'Bearer ' + access;
                return api(originalRequest);
            } catch (_error) {
                // Gérer l'échec du refresh (e.g., rediriger vers login)
                return Promise.reject(_error);
            }
        }
        return Promise.reject(error);
    }
);

export default api;
