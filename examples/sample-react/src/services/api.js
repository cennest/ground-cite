// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://questify-server-gdegcmawbde8hxfn.centralindia-01.azurewebsites.net';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes for analysis requests
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        console.error('API Error:', error.response?.data || error.message);

        // Handle specific error cases
        if (error.response?.status === 404) {
            throw new Error('Resource not found');
        } else if (error.response?.status === 500) {
            throw new Error('Server error occurred');
        } else if (error.code === 'ECONNABORTED') {
            throw new Error('Request timeout - analysis took too long');
        }

        throw error;
    }
);

// API Methods
export const analysisAPI = {
    // Analyze query
    analyzeQuery: async (queryData) => {
        try {
            const response = await api.post('/api/analyze', queryData);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.detail || error.message || 'Analysis failed');
        }
    },

    // Health check
    healthCheck: async () => {
        try {
            const response = await api.get('/api/health');
            return response.data;
        } catch (error) {
            throw new Error('Backend service is not available');
        }
    }
};

export const configAPI = {
    // Get all configurations
    getConfigurations: async () => {
        try {
            const response = await api.get('/api/configs');
            return response.data.configurations || [];
        } catch (error) {
            console.error('Failed to load configurations:', error);
            return [];
        }
    },

    // Save configuration
    saveConfiguration: async (configData) => {
        try {
            const response = await api.post('/api/configs', configData);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.detail || 'Failed to save configuration');
        }
    },

    // Delete configuration
    deleteConfiguration: async (configId) => {
        try {
            const response = await api.delete(`/api/configs/${configId}`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.detail || 'Failed to delete configuration');
        }
    },

    // Get specific configuration
    getConfiguration: async (configId) => {
        try {
            const response = await api.get(`/api/configs/${configId}`);
            return response.data.configuration;
        } catch (error) {
            throw new Error(error.response?.data?.detail || 'Configuration not found');
        }
    }
};

// Export the axios instance for direct use if needed
export default api;