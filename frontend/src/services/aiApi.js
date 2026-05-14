import axios from 'axios';
import api from './api';

const aiAxios = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 90000,
  headers: { 'Content-Type': 'application/json' },
});

export const aiApi = {
  chat: async ({ question }) => {
    const response = await aiAxios.post('/api/chat/price-qa', { question });
    return response.data;
  },

  getHistory: async (limit = 20) => {
    const response = await api.get(`/api/chat/history?limit=${limit}`);
    return response.data;
  },
};
