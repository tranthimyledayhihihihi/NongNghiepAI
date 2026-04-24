import { useEffect, useState } from 'react';
import { pricingApi } from '../services/pricingApi';

export const usePriceData = (cropName, region, autoFetch = false) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [history, setHistory] = useState(null);

  const fetchCurrentPrice = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await pricingApi.getCurrentPrice(cropName, region);
      setCurrentPrice(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async (days = 7) => {
    setLoading(true);
    setError(null);

    try {
      const data = await pricingApi.getPriceForecast(cropName, region, days);
      setForecast(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (days = 30) => {
    setLoading(true);
    setError(null);

    try {
      const data = await pricingApi.getPriceHistory(cropName, region, days);
      setHistory(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch && cropName && region) {
      fetchCurrentPrice();
    }
  }, [cropName, region, autoFetch]);

  return {
    loading,
    error,
    currentPrice,
    forecast,
    history,
    fetchCurrentPrice,
    fetchForecast,
    fetchHistory,
  };
};
