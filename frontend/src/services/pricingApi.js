import api from './api';

export const pricingApi = {
  // Get current price
  getCurrentPrice: async (cropName, region, qualityGrade = 'grade_1') => {
    const response = await api.post('/api/pricing/current', {
      crop_name: cropName,
      region: region,
      quality_grade: qualityGrade,
    });
    return response.data;
  },

  // Get price forecast
  getPriceForecast: async (cropName, region, days = 7) => {
    const response = await api.post('/api/pricing/forecast', {
      crop_name: cropName,
      region: region,
      days: days,
    });
    return response.data;
  },

  // Get price history
  getPriceHistory: async (cropName, region, days = 30) => {
    const response = await api.get(`/api/pricing/history/${cropName}/${region}`, {
      params: { days },
    });
    return response.data;
  },

  // Compare regions
  compareRegions: async (cropName) => {
    const response = await api.get(`/api/pricing/compare-regions/${cropName}`);
    return response.data;
  },
};
