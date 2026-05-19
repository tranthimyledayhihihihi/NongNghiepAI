import api, { getApiErrorMessage } from './api';
import { normalizeApiError, normalizeApiResponse } from '../utils/apiResponse';
import { normalizePriceInput } from '../utils/priceInputs';
import { pricingApi } from './pricingApi';

const unwrap = (response) => normalizeApiResponse(response);
const normalizeNewsPayload = (payload) => (
  Array.isArray(payload)
    ? {
        news: payload,
        metadata: payload.meta || {},
        source: payload.meta?.source_type || payload.source,
        source_name: payload.meta?.source_name || payload.source_name,
        cache_status: payload.meta?.cache_status,
      }
    : payload
);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
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

  getNews: async ({ limit = 10, crop, cropName, region } = {}) => {
    const payload = await request(() => api.get('/api/market/news', {
      params: {
        limit,
        crop: crop || cropName || undefined,
        region: region || undefined,
      },
    }), 'Không tải được tin thị trường');
    return normalizeNewsPayload(payload);
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

  getStorePrices: async ({ cropName, region = 'TP.HCM' }) => {
    return request(() => api.get('/api/market/store-prices', {
      params: { crop_name: normalizePriceInput(cropName), region: normalizePriceInput(region) },
    }), 'Không tải được giá chuỗi cửa hàng');
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
marketApi.getMarketTrends = (input, region) => (
  typeof input === 'object'
    ? marketApi.getTrends({ crop: input.cropName || input.crop, region: input.region })
    : marketApi.getTrends({ crop: input, region })
);
marketApi.analyzeMarketNews = marketApi.analyzeNews;
marketApi.getMarketAnalysis = marketApi.analyzeMarket;

marketApi.getLegacyChannels = marketApi.getChannels;
marketApi.suggestMarketLegacy = marketApi.suggestMarket;
marketApi.getMarketHistoryLegacy = marketApi.getHistory;
marketApi.getMarketDemandLegacy = marketApi.getDemand;
