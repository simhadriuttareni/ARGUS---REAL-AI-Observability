/**
 * ARGUS API Client
 * Axios-based service for backend communication
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('argus_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // Server responded with error
            console.error('API Error:', error.response.data);
        } else if (error.request) {
            // No response received
            console.error('Network Error:', error.request);
        } else {
            console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
    }
);

// === Monitoring APIs ===
export const monitoringAPI = {
    getStatus: () => api.get('/monitoring/status'),
    getChecks: (limit = 50) => api.get(`/monitoring/checks?limit=${limit}`),
    runCheck: () => api.post('/monitoring/run'),
};

// === Alert APIs ===
export const alertAPI = {
    getAlerts: (activeOnly = true) => api.get(`/alerts?active_only=${activeOnly}`),
    getRules: () => api.get('/alerts/rules'),
    createRule: (rule) => api.post('/alerts/rules', rule),
    acknowledgeAlert: (alertId) => api.post(`/alerts/${alertId}/acknowledge`),
    resolveAlert: (alertId) => api.post(`/alerts/${alertId}/resolve`),
};

// === Cost APIs ===
export const costAPI = {
    getMetrics: (startTime, endTime, model, provider) => {
        let url = `/metrics/cost?start_time=${startTime.toISOString()}&end_time=${endTime.toISOString()}`;
        if (model) url += `&model=${model}`;
        if (provider) url += `&provider=${provider}`;
        return api.get(url);
    },
    getByModel: (startTime, endTime) => 
        api.get(`/metrics/cost/by-model?start_time=${startTime.toISOString()}&end_time=${endTime.toISOString()}`),
    getByProvider: (startTime, endTime) => 
        api.get(`/metrics/cost/by-provider?start_time=${startTime.toISOString()}&end_time=${endTime.toISOString()}`),
};

// === Cache APIs ===
export const cacheAPI = {
    getStats: () => api.get('/cache/stats'),
    clear: () => api.post('/cache/clear'),
};

// === Traces APIs ===
export const tracesAPI = {
    getTraces: (limit = 50, offset = 0) => 
        api.get(`/traces?limit=${limit}&offset=${offset}`),
    getTrace: (traceId) => api.get(`/traces/${traceId}`),
    getTracesByModel: (model, limit = 50) => 
        api.get(`/traces/by-model/${model}?limit=${limit}`),
};

// === Router APIs ===
export const routerAPI = {
    route: (prompt, taskType, maxCost, maxLatency) => 
        api.post('/router/route', {
            prompt,
            task_type: taskType,
            max_cost: maxCost,
            max_latency: maxLatency,
        }),
};

// === Dashboard APIs ===
export const dashboardAPI = {
    getMetrics: () => api.get('/dashboard/metrics'),
    getSummary: () => api.get('/dashboard/summary'),
};

// === Ingest APIs ===
export const ingestAPI = {
    ingestTrace: (trace) => api.post('/ingest', trace),
    ingestBatch: (traces) => api.post('/ingest/batch', { traces }),
};

export default api;