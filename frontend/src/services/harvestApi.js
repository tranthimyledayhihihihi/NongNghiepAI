import api from './api';

export const harvestApi = {
  // Predict harvest date
  predictHarvest: async (cropName, plantingDate, region) => {
    const response = await api.post('/api/harvest/predict', {
      crop_name: cropName,
      planting_date: plantingDate,
      region: region,
    });
    return response.data;
  },

  // Get harvest schedule
  getSchedule: async () => {
    const response = await api.get('/api/harvest/schedule');
    return response.data;
  },
};
