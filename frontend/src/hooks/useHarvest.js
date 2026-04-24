import { useState } from 'react';
import api from '../services/api';

export const useHarvest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const predictHarvest = async (cropName, plantingDate, region) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/harvest/predict', {
        crop_name: cropName,
        planting_date: plantingDate,
        region: region,
      });
      setData(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Lỗi khi dự báo thu hoạch');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    data,
    predictHarvest,
  };
};
