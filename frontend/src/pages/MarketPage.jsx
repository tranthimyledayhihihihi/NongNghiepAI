import { AlertCircle, Globe, ShoppingCart, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import DataSourceBadge from '../components/DataSourceBadge';
import { getApiErrorMessage } from '../services/api';
import { marketApi } from '../services/marketApi';
import { marketNewsApi } from '../services/marketNewsApi';

const fallbackChannels = [
  { id: 'wholesale', name: 'Chợ đầu mối', commission: '5-10%' },
  { id: 'retail', name: 'Chợ bán lẻ', commission: '0%' },
  { id: 'supermarket', name: 'Siêu thị/cửa hàng sạch', commission: '10-15%' },
];

const channelIcons = [ShoppingCart, TrendingUp, Globe];

const MarketPage = () => {
  const [channels, setChannels] = useState(fallbackChannels);
  const [channelSource, setChannelSource] = useState({ is_mock: true, source: 'fallback' });
  const [formData, setFormData] = useState({
    cropName: 'ca chua',
    region: 'Ha Noi',
    quantity: 1000,
    qualityGrade: 'grade_1',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [news, setNews] = useState([]);

  useEffect(() => {
    const loadChannels = async () => {
      try {
        const data = await marketApi.getChannels();
        if (data.channels?.length) {
          setChannels(data.channels);
          setChannelSource(data);
        }
      } catch {
        setChannels(fallbackChannels);
        setChannelSource({ is_mock: true, source: 'fallback' });
      }
    };
    loadChannels();
  }, []);

  useEffect(() => {
    marketNewsApi.getLatest(4)
      .then((data) => setNews(data.news || []))
      .catch(() => setNews([]));
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await marketApi.suggestMarket(
        formData.cropName,
        formData.region,
        formData.quantity,
        formData.qualityGrade
      );
      setResult(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể gợi ý kênh bán hàng'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-gray-900">Tư vấn kênh bán hàng</h1>
          <DataSourceBadge data={channelSource} />
        </div>
        <p className="mt-2 text-gray-600">
          So sánh kênh bán và gợi ý kênh tối ưu từ API backend.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {channels.map((channel, index) => {
          const Icon = channelIcons[index % channelIcons.length];
          const channelId = channel.id || channel.channel_code;
          const channelName = channel.name || channel.channel_name;
          const commission =
            channel.commission ||
            (Number.isFinite(channel.commission_rate) ? `${Math.round(channel.commission_rate * 100)}%` : 'N/A');
          return (
            <div
              key={channelId || channelName}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">{channelName}</h3>
                  <p className="text-sm text-gray-600">{channelId}</p>
                </div>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-700">Phí hoa hồng:</span>
                <span className="ml-2 text-sm text-gray-900">{commission}</span>
              </div>
            </div>
          );
        })}
      </div>

      {news.length > 0 && (
        <section className="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Tin tức thị trường realtime</h2>
            <DataSourceBadge data={{ source_name: 'RSS', is_realtime: true }} />
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {news.map((item) => (
              <a
                key={item.source_url}
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-gray-200 p-4 hover:border-green-300 hover:bg-green-50"
              >
                <p className="text-sm font-semibold text-gray-900">{item.title}</p>
                <p className="mt-2 line-clamp-2 text-sm text-gray-600">{item.summary}</p>
                <p className="mt-3 text-xs text-gray-500">{item.source_name}</p>
              </a>
            ))}
          </div>
        </section>
      )}

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Công cụ gợi ý kênh bán</h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nông sản
            </label>
            <select
              value={formData.cropName}
              onChange={(event) => setFormData({ ...formData, cropName: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="ca chua">Cà chua</option>
              <option value="dua chuot">Dưa chuột</option>
              <option value="rau muong">Rau muống</option>
              <option value="lua">Lúa</option>
              <option value="ot">Ớt</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Khu vực
            </label>
            <select
              value={formData.region}
              onChange={(event) => setFormData({ ...formData, region: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="Ha Noi">Hà Nội</option>
              <option value="TP.HCM">TP.HCM</option>
              <option value="Da Nang">Đà Nẵng</option>
              <option value="Can Tho">Cần Thơ</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số lượng (kg)
            </label>
            <input
              type="number"
              min="1"
              value={formData.quantity}
              onChange={(event) => setFormData({ ...formData, quantity: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chất lượng
            </label>
            <select
              value={formData.qualityGrade}
              onChange={(event) => setFormData({ ...formData, qualityGrade: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="grade_1">Loại 1</option>
              <option value="grade_2">Loại 2</option>
              <option value="grade_3">Loại 3</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300"
            >
              {loading ? 'Đang gợi ý...' : 'Gợi ý'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-6 space-y-4">
            <div className="rounded-lg bg-green-50 border border-green-200 p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <p className="text-sm text-green-700">Kênh đề xuất</p>
                <DataSourceBadge data={result} />
              </div>
              <p className="text-2xl font-bold text-green-900">{result.recommended_channel}</p>
              <p className="mt-2 text-sm text-green-800">{result.reason}</p>
              {result.warning && <p className="mt-2 text-sm text-yellow-700">{result.warning}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.profit_comparison?.map((channel, index) => (
                <div
                  key={channel.channel}
                  className={`p-4 rounded-lg border-2 ${
                    index === 0 ? 'border-green-500 bg-green-50' : 'border-gray-200'
                  }`}
                >
                  <p className="font-medium text-gray-900">
                    {channel.channel_name}
                    {index === 0 && (
                      <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">
                        Tốt nhất
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Giá ước tính: {channel.estimated_price.toLocaleString()} VND/kg
                  </p>
                  <p className="text-lg font-bold text-gray-900 mt-1">
                    {channel.estimated_total_revenue.toLocaleString()} VND
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketPage;
