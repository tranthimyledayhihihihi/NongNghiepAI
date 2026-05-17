import { AlertCircle, Calendar, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { harvestApi } from '../services/harvestApi';

const cropOptions = [
  { value: 'ca chua', label: 'Cà chua' },
  { value: 'dua chuot', label: 'Dưa chuột' },
  { value: 'rau muong', label: 'Rau muống' },
  { value: 'cai xanh', label: 'Cải xanh' },
  { value: 'ot', label: 'Ớt' },
  { value: 'lua', label: 'Lúa' },
];

const regionOptions = [
  { value: 'Ha Noi', label: 'Hà Nội' },
  { value: 'TP.HCM', label: 'TP.HCM' },
  { value: 'Da Nang', label: 'Đà Nẵng' },
  { value: 'Can Tho', label: 'Cần Thơ' },
  { value: 'Hai Phong', label: 'Hải Phòng' },
];

const dateDiffDays = (start, end) => {
  if (!start || !end) return 0;
  return Math.round((new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24));
};

const HarvestPage = () => {
  const [formData, setFormData] = useState({
    crop: 'ca chua',
    region: 'Ha Noi',
    plantingDate: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await harvestApi.forecastHarvest(
        formData.crop,
        formData.plantingDate,
        formData.region
      );
      setResult(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể dự báo thu hoạch'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dự báo thu hoạch</h1>
        <p className="mt-2 text-gray-600">
          Dự đoán thời điểm thu hoạch tối ưu qua API backend.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Thông tin cây trồng</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Loại cây trồng
              </label>
              <select
                value={formData.crop}
                onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {cropOptions.map((crop) => (
                  <option key={crop.value} value={crop.value}>
                    {crop.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Khu vực
              </label>
              <select
                value={formData.region}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {regionOptions.map((region) => (
                  <option key={region.value} value={region.value}>
                    {region.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ngày xuống giống
              </label>
              <input
                type="date"
                value={formData.plantingDate}
                onChange={(e) => setFormData({ ...formData, plantingDate: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
                <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300"
            >
              {loading ? 'Đang dự báo...' : 'Dự báo thu hoạch'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Kết quả dự báo</h2>

          {result ? (
            <div className="space-y-4">
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Calendar className="h-5 w-5 text-primary-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">
                    Ngày thu hoạch dự kiến
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {new Date(result.expected_harvest_date).toLocaleDateString('vi-VN')}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Sau {dateDiffDays(result.planting_date, result.expected_harvest_date)} ngày kể từ ngày xuống giống
                </p>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">Độ tin cậy</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {(result.confidence * 100).toFixed(0)}%
                </p>
              </div>

              {(result.warning || result.recommendation) && (
                <div className="bg-blue-50 rounded-lg p-4">
                  {result.warning && (
                    <p className="text-sm text-blue-900 mb-2">{result.warning}</p>
                  )}
                  <p className="text-sm text-blue-800">{result.recommendation}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>Nhập thông tin để gọi API dự báo thu hoạch</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HarvestPage;
