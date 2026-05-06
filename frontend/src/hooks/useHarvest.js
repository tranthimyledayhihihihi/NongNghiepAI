import { useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { harvestApi } from '../services/harvestApi';

export const useHarvest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const predictHarvest = async (cropName, plantingDate, region) => {
    setLoading(true);
    setError(null);

    try {
      const result = await harvestApi.forecastHarvest(cropName, plantingDate, region);
      setData(result);
      return result;
    } catch (err) {
      setError(getApiErrorMessage(err, 'Loi khi du bao thu hoach'));
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
