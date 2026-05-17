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
import DataSourceBadge from '../components/DataSourceBadge';
import { EmptyState, InlineLoading, PageError } from '../components/StatusState';
import { getApiErrorMessage } from '../services/api';
import { pricingApi } from '../services/pricingApi';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const crops = ['ca chua', 'dua chuot', 'rau muong', 'cai xanh', 'ot', 'lua'];
const cropLabels = {
  'ca chua': 'Cà chua',
  'dua chuot': 'Dưa chuột',
  'rau muong': 'Rau muống',
  'cai xanh': 'Cải xanh',
  ot: 'Ớt',
  lua: 'Lúa',
};
const regions = [
  { value: 'Ha Noi', label: 'Hà Nội' },
  { value: 'TP.HCM', label: 'TP.HCM' },
  { value: 'Da Nang', label: 'Đà Nẵng' },
  { value: 'Can Tho', label: 'Cần Thơ' },
  { value: 'Hai Phong', label: 'Hải Phòng' },
];

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
const QUALITY_LABELS = {
  grade_1: 'Loại 1',
  grade_2: 'Loại 2',
  grade_3: 'Loại 3',
  'Loai 1': 'Loại 1',
  'Loai 2': 'Loại 2',
  'Loai 3': 'Loại 3',
};

const PricingPage = () => {
  const [cropName, setCropName] = useState('ca chua');
  const [region, setRegion] = useState('Ha Noi');
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [history, setHistory] = useState(null);
  const [engine, setEngine] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const [priceData, forecastData, historyData, engineData] = await Promise.all([
        pricingApi.getCurrentPrice(cropName, region),
        pricingApi.getPriceForecast(cropName, region, days),
        pricingApi.getPriceHistory(cropName, region, 30),
        pricingApi.getPricingEngine(cropName, region, 100, 'grade_1', days),
      ]);
      setCurrentPrice(priceData);
      setForecast(forecastData);
      setHistory(historyData);
      setEngine(engineData);
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
                  {cropLabels[crop] || crop}
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
                <option key={item.value} value={item.value}>
                  {item.label}
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
        <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-700 shadow-sm">
          <DataSourceBadge data={currentPrice} />
          <span>Nguồn: {currentPrice.source_name || 'không rõ'}</span>
          {currentPrice.last_updated && (
            <span>Cập nhật: {new Date(currentPrice.last_updated).toLocaleString('vi-VN')}</span>
          )}
          {currentPrice.is_mock && (
            <span className="font-medium text-amber-700">Đang hiển thị dữ liệu demo.</span>
          )}
        </div>
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
            <p className="mt-2 text-2xl font-bold text-gray-900">
              {QUALITY_LABELS[currentPrice.quality_grade] || currentPrice.quality_grade}
            </p>
          </div>
        </div>
      )}

      {engine && (
        <section className="rounded-lg border border-violet-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI Pricing Engine</h2>
              <p className="text-sm text-gray-500">Market price + forecast + quality + weather reasoning</p>
            </div>
            <DataSourceBadge data={engine} />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-violet-50 p-4">
              <p className="text-sm text-violet-700">AI suggested price</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">{formatCurrency(engine.suggested_price)}</p>
            </div>
            <div className="rounded-lg bg-emerald-50 p-4">
              <p className="text-sm text-emerald-700">7-day forecast</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">{formatCurrency(engine.forecast_price_7d)}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-sm text-slate-700">Confidence</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">{((engine.confidence || 0) * 100).toFixed(0)}%</p>
            </div>
          </div>
          {engine.reasons?.length > 0 && (
            <div className="mt-4 grid gap-2 md:grid-cols-2">
              {engine.reasons.map((reason) => (
                <div key={reason} className="rounded-lg border border-violet-100 bg-violet-50/60 p-3 text-sm text-violet-900">
                  {reason}
                </div>
              ))}
            </div>
          )}
          {engine.recommendation && (
            <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
              {engine.recommendation}
            </div>
          )}
        </section>
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
          {history.history.some((item) => item.is_mock) && (
            <div className="mb-3 flex flex-wrap items-center gap-3 text-sm text-amber-700">
              <DataSourceBadge data={{ is_mock: true }} />
              <span>Biểu đồ lịch sử đang dùng dữ liệu demo dự phòng.</span>
            </div>
          )}
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
