import api from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

export const pricingApi = {
  getCurrentPrice: async (cropName, region, qualityGrade = 'grade_1') => {
    const response = await api.get('/api/pricing/current', {
      params: {
        crop_name: cropName,
        region,
        quality_grade: qualityGrade,
      },
    });
    return normalizeApiResponse(response);
  },

  getPriceForecast: async (cropName, region, days = 7) => {
    const response = await api.post('/api/pricing/forecast', {
      crop_name: cropName,
      region,
      days,
    });
    return normalizeApiResponse(response);
  },

  getPriceHistory: async (cropName, region, days = 30) => {
    const response = await api.get(
      `/api/pricing/history/${encodeURIComponent(cropName)}/${encodeURIComponent(region)}`,
      { params: { days } }
    );
    return normalizeApiResponse(response);
  },

  compareRegions: async (cropName, region) => {
    const response = await api.get(`/api/pricing/compare-regions/${encodeURIComponent(cropName)}`, {
      params: region ? { region } : undefined,
    });
    return normalizeApiResponse(response);
  },

  suggestPrice: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    const response = await api.post('/api/pricing/suggest', {
      crop_name: cropName,
      region,
      quantity,
      quality_grade: qualityGrade,
    });
    return normalizeApiResponse(response);
  },

  getPricingEngine: async (cropName, region, quantity = 1, qualityGrade = 'grade_1', days = 7) => {
    const response = await api.post('/api/pricing/engine', {
      crop_name: cropName,
      region,
      quantity,
      quality_grade: qualityGrade,
      days,
    });
    return normalizeApiResponse(response);
  },

  predictPrice: async (cropName, region, forecastDays = 7) => {
    const response = await api.post('/api/price-forecast/predict', {
      crop_name: cropName,
      region,
      forecast_days: forecastDays,
    });
    return normalizeApiResponse(response);
  },
};
