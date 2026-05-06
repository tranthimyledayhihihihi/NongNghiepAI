import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from 'chart.js';
import { Minus, Search, TrendingDown, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { Line } from 'react-chartjs-2';
import { EmptyState, InlineLoading, PageError } from '../components/StatusState';
import { getApiErrorMessage } from '../services/api';
import { pricingApi } from '../services/pricingApi';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const crops = ['ca chua', 'dua chuot', 'rau muong', 'cai xanh', 'ot', 'lua'];
const regions = ['Ha Noi', 'TP.HCM', 'Da Nang', 'Can Tho', 'Hai Phong'];

const trendMeta = {
  increasing: {
    label: 'Tăng',
    icon: <TrendingUp className="h-5 w-5 text-green-600" />,
  },
  decreasing: {
    label: 'Giảm',
    icon: <TrendingDown className="h-5 w-5 text-red-600" />,
  },
  stable: {
    label: 'Ổn định',
    icon: <Minus className="h-5 w-5 text-gray-600" />,
  },
};

const formatCurrency = (value) => `${Number(value || 0).toLocaleString('vi-VN')} đ/kg`;

const PricingPage = () => {
  const [cropName, setCropName] = useState('ca chua');
  const [region, setRegion] = useState('Ha Noi');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [history, setHistory] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const [priceData, forecastData, historyData] = await Promise.all([
        pricingApi.getCurrentPrice(cropName, region),
        pricingApi.getPriceForecast(cropName, region, days),
        pricingApi.getPriceHistory(cropName, region, 30),
      ]);
      setCurrentPrice(priceData);
      setForecast(forecastData);
      setHistory(historyData);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tải dữ liệu giá'));
    } finally {
      setLoading(false);
    }
  };

  const chartData = forecast?.forecast_data?.length
    ? {
        labels: forecast.forecast_data.map((item) =>
          new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })
        ),
        datasets: [
          {
            label: 'Giá dự báo',
            data: forecast.forecast_data.map((item) => item.predicted_price),
            borderColor: 'rgb(22, 163, 74)',
            backgroundColor: 'rgba(22, 163, 74, 0.12)',
            fill: true,
            tension: 0.35,
          },
          {
            label: 'Cận trên',
            data: forecast.forecast_data.map((item) => item.confidence_upper),
            borderColor: 'rgba(22, 163, 74, 0.3)',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
          },
          {
            label: 'Cận dưới',
            data: forecast.forecast_data.map((item) => item.confidence_lower),
            borderColor: 'rgba(22, 163, 74, 0.3)',
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
          },
        ],
      }
    : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: `Dự báo giá ${days} ngày tới`,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => `${Number(value).toLocaleString('vi-VN')} đ`,
        },
      },
    },
  };

  const trend = trendMeta[currentPrice?.price_trend] || trendMeta.stable;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-green-700">API Pricing</p>
        <h1 className="mt-2 text-3xl font-bold text-gray-900">Định giá nông sản</h1>
        <p className="mt-2 text-gray-600">Tra cứu giá hiện tại, dự báo và lịch sử giá từ backend.</p>
      </div>

      <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-[1fr_1fr_180px_160px]">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Loại nông sản</label>
            <select
              value={cropName}
              onChange={(event) => setCropName(event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              {crops.map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Khu vực</label>
            <select
              value={region}
              onChange={(event) => setRegion(event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              {regions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Số ngày dự báo</label>
            <select
              value={days}
              onChange={(event) => setDays(Number(event.target.value))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              <option value={7}>7 ngày</option>
              <option value={14}>14 ngày</option>
              <option value={30}>30 ngày</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={handleSearch}
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-green-700 px-4 py-2.5 font-semibold text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Search className="h-5 w-5" />
              {loading ? 'Đang tải...' : 'Tra cứu'}
            </button>
          </div>
        </div>
      </section>

      {error && <PageError message={error} onRetry={handleSearch} />}
      {loading && <InlineLoading text="Đang tải dữ liệu giá..." />}

      {!loading && !currentPrice && !error && (
        <EmptyState
          title="Chưa có dữ liệu giá"
          description="Chọn nông sản, khu vực và bấm tra cứu để lấy dữ liệu từ backend."
        />
      )}

      {currentPrice && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-600">Giá hiện tại</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {formatCurrency(currentPrice.current_price)}
            </p>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-600">Xu hướng</p>
            <div className="mt-2 flex items-center gap-2">
              {trend.icon}
              <span className="text-2xl font-bold text-gray-900">{trend.label}</span>
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-gray-600">Phân loại</p>
            <p className="mt-2 text-2xl font-bold text-gray-900">{currentPrice.quality_grade}</p>
          </div>
        </div>
      )}

      {forecast && chartData && (
        <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <div className="h-80 min-h-80">
            <Line data={chartData} options={chartOptions} />
          </div>

          <div className="mt-5 rounded-lg border border-blue-100 bg-blue-50 p-4">
            <p className="text-sm font-semibold text-blue-900">Khuyến nghị</p>
            <p className="mt-1 text-sm leading-6 text-blue-800">{forecast.recommendation}</p>
          </div>
        </section>
      )}

      {history?.history?.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Lịch sử giá gần đây</h2>
          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {history.history.slice(-6).map((item) => (
              <div key={item.date} className="rounded-lg border border-gray-200 p-3">
                <p className="text-sm text-gray-500">{new Date(item.date).toLocaleDateString('vi-VN')}</p>
                <p className="mt-1 text-lg font-bold text-gray-900">{formatCurrency(item.avg_price)}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default PricingPage;
