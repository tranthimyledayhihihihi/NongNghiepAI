import api from './api';

export const pricingApi = {
  // Get current price
  getCurrentPrice: async (cropName, region, qualityGrade = 'grade_1') => {
    const response = await api.get('/api/pricing/current', {
      params: {
        crop_name: cropName,
        region: region,
        quality_grade: qualityGrade,
      },
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
    const response = await api.get(
      `/api/pricing/history/${encodeURIComponent(cropName)}/${encodeURIComponent(region)}`,
      {
      params: { days },
      }
    );
    return response.data;
  },

  // Compare regions
  compareRegions: async (cropName, region) => {
    const response = await api.get(`/api/pricing/compare-regions/${encodeURIComponent(cropName)}`, {
      params: region ? { region } : undefined,
    });
    return response.data;
  },

  suggestPrice: async (cropName, region, quantity, qualityGrade = 'grade_1') => {
    const response = await api.post('/api/pricing/suggest', {
      crop_name: cropName,
      region,
      quantity,
      quality_grade: qualityGrade,
    });
    return response.data;
  },

  predictPrice: async (cropName, region, forecastDays = 7) => {
    const response = await api.post('/api/price-forecast/predict', {
      crop_name: cropName,
      region,
      forecast_days: forecastDays,
    });
    return response.data;
  },
};
