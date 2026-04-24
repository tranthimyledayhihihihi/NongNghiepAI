import React, { useState } from 'react';
import { pricingApi } from '../services/pricingApi';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PricingPage = () => {
  const [cropName, setCropName] = useState('Cà chua');
  const [region, setRegion] = useState('Hà Nội');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [history, setHistory] = useState(null);

  const crops = ['Cà chua', 'Dưa chuột', 'Rau muống', 'Cải xanh', 'Ớt'];
  const regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng'];

  const handleSearch = async () => {
    setLoading(true);
    try {
      // Get current price
      const priceData = await pricingApi.getCurrentPrice(cropName, region);
      setCurrentPrice(priceData);

      // Get forecast
      const forecastData = await pricingApi.getPriceForecast(cropName, region, days);
      setForecast(forecastData);

      // Get history
      const historyData = await pricingApi.getPriceHistory(cropName, region, 30);
      setHistory(historyData);
    } catch (error) {
      console.error('Error fetching price data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case 'decreasing':
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      default:
        return <Minus className="h-5 w-5 text-gray-600" />;
    }
  };

  const getTrendText = (trend) => {
    switch (trend) {
      case 'increasing':
        return 'Tăng';
      case 'decreasing':
        return 'Giảm';
      default:
        return 'Ổn định';
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600 bg-green-50';
      case 'decreasing':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const chartData = forecast
    ? {
        labels: forecast.forecast_data.map((d) => {
          const date = new Date(d.date);
          return `${date.getDate()}/${date.getMonth() + 1}`;
        }),
        datasets: [
          {
            label: 'Giá dự báo',
            data: forecast.forecast_data.map((d) => d.predicted_price),
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            fill: true,
            tension: 0.4,
          },
          {
            label: 'Khoảng tin cậy trên',
            data: forecast.forecast_data.map((d) => d.confidence_upper),
            borderColor: 'rgba(34, 197, 94, 0.3)',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
          },
          {
            label: 'Khoảng tin cậy dưới',
            data: forecast.forecast_data.map((d) => d.confidence_lower),
            borderColor: 'rgba(34, 197, 94, 0.3)',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
          },
        ],
      }
    : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Dự báo giá ${days} ngày tới`,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => `${value.toLocaleString()} đ`,
        },
      },
    },
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Định giá nông sản</h1>
        <p className="mt-2 text-gray-600">
          Tra cứu giá hiện tại và dự báo xu hướng giá
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Loại nông sản
            </label>
            <select
              value={cropName}
              onChange={(e) => setCropName(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {crops.map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Khu vực
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {regions.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số ngày dự báo
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={7}>7 ngày</option>
              <option value={14}>14 ngày</option>
              <option value={30}>30 ngày</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300"
            >
              {loading ? 'Đang tải...' : 'Tra cứu'}
            </button>
          </div>
        </div>
      </div>

      {/* Current Price */}
      {currentPrice && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Giá hiện tại</p>
            <p className="text-3xl font-bold text-gray-900">
              {currentPrice.current_price.toLocaleString()} đ/kg
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Xu hướng</p>
            <div className="flex items-center space-x-2">
              {getTrendIcon(currentPrice.price_trend)}
              <span
                className={`text-2xl font-bold ${getTrendColor(currentPrice.price_trend)}`}
              >
                {getTrendText(currentPrice.price_trend)}
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Phân loại</p>
            <p className="text-2xl font-bold text-gray-900">
              {currentPrice.quality_grade === 'grade_1'
                ? 'Loại 1'
                : currentPrice.quality_grade === 'grade_2'
                ? 'Loại 2'
                : 'Loại 3'}
            </p>
          </div>
        </div>
      )}

      {/* Forecast Chart */}
      {forecast && chartData && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <Line data={chartData} options={chartOptions} />

          {/* Recommendation */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm font-medium text-blue-900 mb-2">
              Khuyến nghị:
            </p>
            <p className="text-blue-800">{forecast.recommendation}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingPage;
