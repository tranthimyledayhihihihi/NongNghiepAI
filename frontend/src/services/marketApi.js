import api, { getApiErrorMessage } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';
import { normalizePriceInput } from '../utils/priceInputs';
import { pricingApi } from './pricingApi';

const unwrap = (response) => normalizeApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

const normalizeMarketQuery = (crop, region, qualityGrade = 'grade_1', quantity = undefined) => ({
  crop_name: normalizePriceInput(crop),
  region: normalizePriceInput(region),
  quality_grade: qualityGrade,
  quantity: quantity === undefined ? undefined : Number(quantity),
});

export const marketApi = {
  getChannels: async () => {
    return request(() => api.get('/api/market/channels'), 'Không tải được danh sách kênh bán');
  },

  getNews: async ({ limit = 10, crop, region } = {}) => {
    return request(() => api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || undefined,
        region: region || undefined,
      },
    }), 'Không tải được tin thị trường');
  },

  getPrices: async ({ crop = 'lua', region = 'Ha Noi', qualityGrade = 'grade_1' } = {}) => {
    const response = await pricingApi.getCurrentPrice({
      cropName: crop,
      region,
      qualityGrade,
    });
    return response;
  },

  analyzeMarket: async ({ cropName, region, quantity, qualityGrade = 'grade_2' }) => {
    return request(() => api.post('/api/market/analyze', normalizeMarketQuery(cropName, region, qualityGrade, quantity)), 'Không phân tích được thị trường');
  },

  analyzeNews: async ({ title, summary, crop, region }) => {
    return request(() => api.post('/api/market/analyze-news', {
      title,
      summary,
      crop,
      region,
    }), 'Không phân tích được tin thị trường');
  },

  getTrends: async ({ crop = 'lua', region = 'Ha Noi' } = {}) => {
    return request(() => api.get('/api/market/trends', {
      params: { crop, region },
    }), 'Không tải được xu hướng thị trường');
  },

  suggestMarket: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    return request(() => api.post('/api/market/suggest', {
      crop_name: normalizePriceInput(cropName),
      region: normalizePriceInput(region),
      quantity: Number(quantity),
      quality_grade: qualityGrade,
    }), 'Không gợi ý được kênh bán hàng');
  },

  getHistory: async (userId = 1, limit = 50) => {
    return request(() => api.get(`/api/market/history/${encodeURIComponent(userId)}`, {
      params: { limit },
    }), 'Không tải được lịch sử kênh bán');
  },

  getDemand: async (cropName) => {
    return request(() => api.get(`/api/market/demand/${encodeURIComponent(cropName)}`), 'Không tải được nhu cầu thị trường');
  },
};

marketApi.getMarketNews = marketApi.getNews;
marketApi.getMarketPrices = marketApi.getPrices;
marketApi.getMarketTrends = (crop, region) => marketApi.getTrends({ crop, region });
marketApi.analyzeMarketNews = marketApi.analyzeNews;
marketApi.getMarketAnalysis = marketApi.analyzeMarket;

marketApi.getLegacyChannels = marketApi.getChannels;
marketApi.suggestMarketLegacy = marketApi.suggestMarket;
marketApi.getMarketHistoryLegacy = marketApi.getHistory;
marketApi.getMarketDemandLegacy = marketApi.getDemand;
