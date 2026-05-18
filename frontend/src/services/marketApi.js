import api, { getApiErrorMessage } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

export const marketApi = {
  getChannels: async () => {
    return request(() => api.get('/api/market/channels'), 'Khong tai duoc legacy market channels');
  },

  getNews: async ({ limit = 10, crop, region } = {}) => {
    return request(() => api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || undefined,
        region: region || undefined,
      },
    }), 'Khong tai duoc market news');
  },

  getPrices: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    return request(() => api.get('/api/market/prices', {
      params: { crop, region },
    }), 'Khong tai duoc market prices');
  },

  analyzeNews: async ({ title, summary, crop, region }) => {
    return request(() => api.post('/api/market/analyze-news', {
      title,
      summary,
      crop,
      region,
    }), 'Khong phan tich duoc tin thi truong');
  },

  getTrends: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    return request(() => api.get('/api/market/trends', {
      params: { crop, region },
    }), 'Khong tai duoc market trends');
  },

  getOpportunities: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    return request(() => api.get('/api/market/opportunities', {
      params: { crop, region },
    }), 'Khong tai duoc market opportunities');
  },

  getRisks: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    return request(() => api.get('/api/market/risks', {
      params: { crop, region },
    }), 'Khong tai duoc market risks');
  },

  suggestMarket: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    return request(() => api.post('/api/market/suggest', {
      crop_name: cropName,
      region,
      quantity: Number(quantity),
      quality_grade: qualityGrade,
    }), 'Khong goi y duoc kenh ban hang');
  },

  getHistory: async (userId = 1, limit = 50) => {
    return request(() => api.get(`/api/market/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    }), 'Khong tai duoc market history legacy');
  },

  getDemand: async (cropName) => {
    return request(() => api.get(`/api/market/demand/${encodeURIComponent(cropName)}`), 'Khong tai duoc demand legacy');
  },
};

marketApi.getMarketNews = marketApi.getNews;
marketApi.getMarketPrices = marketApi.getPrices;
marketApi.getMarketTrends = (crop, region) => marketApi.getTrends({ crop, region });
marketApi.getMarketOpportunities = marketApi.getOpportunities;
marketApi.getMarketRisks = marketApi.getRisks;
marketApi.analyzeMarketNews = marketApi.analyzeNews;

marketApi.getLegacyChannels = marketApi.getChannels;
marketApi.suggestMarketLegacy = marketApi.suggestMarket;
marketApi.getMarketHistoryLegacy = marketApi.getHistory;
marketApi.getMarketDemandLegacy = marketApi.getDemand;
