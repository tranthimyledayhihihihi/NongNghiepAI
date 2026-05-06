import { AlertCircle, Globe, ShoppingCart, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { marketApi } from '../services/marketApi';

const fallbackChannels = [
  { id: 'wholesale', name: 'Cho dau moi', commission: '5-10%' },
  { id: 'retail', name: 'Cho ban le', commission: '0%' },
  { id: 'supermarket', name: 'Sieu thi/cua hang sach', commission: '10-15%' },
];

const channelIcons = [ShoppingCart, TrendingUp, Globe];

const MarketPage = () => {
  const [channels, setChannels] = useState(fallbackChannels);
  const [formData, setFormData] = useState({
    cropName: 'ca chua',
    region: 'Ha Noi',
    quantity: 1000,
    qualityGrade: 'grade_1',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadChannels = async () => {
      try {
        const data = await marketApi.getChannels();
        if (data.channels?.length) {
          setChannels(data.channels);
        }
      } catch {
        setChannels(fallbackChannels);
      }
    };
    loadChannels();
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
      setError(getApiErrorMessage(err, 'Khong the goi y kenh ban hang'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Tu van kenh ban hang</h1>
        <p className="mt-2 text-gray-600">
          So sanh kenh ban va goi y kenh toi uu tu API backend.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {channels.map((channel, index) => {
          const Icon = channelIcons[index % channelIcons.length];
          return (
            <div
              key={channel.id || channel.name}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">{channel.name}</h3>
                  <p className="text-sm text-gray-600">{channel.id}</p>
                </div>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-700">Phi hoa hong:</span>
                <span className="ml-2 text-sm text-gray-900">{channel.commission}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Cong cu goi y kenh ban</h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nong san
            </label>
            <select
              value={formData.cropName}
              onChange={(event) => setFormData({ ...formData, cropName: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="ca chua">Ca chua</option>
              <option value="dua chuot">Dua chuot</option>
              <option value="rau muong">Rau muong</option>
              <option value="lua">Lua</option>
              <option value="ot">Ot</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Khu vuc
            </label>
            <select
              value={formData.region}
              onChange={(event) => setFormData({ ...formData, region: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="Ha Noi">Ha Noi</option>
              <option value="TP.HCM">TP.HCM</option>
              <option value="Da Nang">Da Nang</option>
              <option value="Can Tho">Can Tho</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              So luong (kg)
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
              Chat luong
            </label>
            <select
              value={formData.qualityGrade}
              onChange={(event) => setFormData({ ...formData, qualityGrade: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="grade_1">Loai 1</option>
              <option value="grade_2">Loai 2</option>
              <option value="grade_3">Loai 3</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300"
            >
              {loading ? 'Dang goi y...' : 'Goi y'}
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
              <p className="text-sm text-green-700">Kenh de xuat</p>
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
                        Tot nhat
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Gia uoc tinh: {channel.estimated_price.toLocaleString()} VND/kg
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
