import { Calendar, TrendingUp } from 'lucide-react';
import { useState } from 'react';

const HarvestPage = () => {
  const [formData, setFormData] = useState({
    crop: 'Cà chua',
    region: 'Hà Nội',
    plantingDate: '',
  });

  const [result, setResult] = useState(null);

  const crops = ['Cà chua', 'Dưa chuột', 'Rau muống', 'Cải xanh', 'Ớt'];
  const regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng'];

  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock result - API integration in Phase 2
    const plantDate = new Date(formData.plantingDate);
    const harvestDate = new Date(plantDate);
    harvestDate.setDate(harvestDate.getDate() + 75); // Mock 75 days

    setResult({
      crop: formData.crop,
      region: formData.region,
      plantingDate: formData.plantingDate,
      predictedHarvestDate: harvestDate.toISOString().split('T')[0],
      growthDays: 75,
      confidence: 0.85,
    });
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Dự báo thu hoạch
        </h1>
        <p className="mt-2 text-gray-600">
          Dự đoán thời điểm thu hoạch tối ưu dựa trên AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Thông tin cây trồng</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Loại cây trồng
              </label>
              <select
                value={formData.crop}
                onChange={(e) =>
                  setFormData({ ...formData, crop: e.target.value })
                }
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
                value={formData.region}
                onChange={(e) =>
                  setFormData({ ...formData, region: e.target.value })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {regions.map((region) => (
                  <option key={region} value={region}>
                    {region}
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
                onChange={(e) =>
                  setFormData({ ...formData, plantingDate: e.target.value })
                }
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700"
            >
              Dự báo thu hoạch
            </button>
          </form>
        </div>

        {/* Result */}
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
                  {new Date(result.predictedHarvestDate).toLocaleDateString(
                    'vi-VN'
                  )}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  Sau {result.growthDays} ngày kể từ ngày xuống giống
                </p>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                  <span className="text-sm font-medium text-gray-700">
                    Độ tin cậy
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {(result.confidence * 100).toFixed(0)}%
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">
                  Khuyến nghị:
                </p>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Chuẩn bị nhân lực trước 1 tuần</li>
                  <li>• Theo dõi thời tiết để điều chỉnh kế hoạch</li>
                  <li>• Chuẩn bị phương tiện vận chuyển</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p>Nhập thông tin để dự báo thu hoạch</p>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Lưu ý:</strong> Dự báo hiện tại dựa trên thời gian sinh trưởng trung bình.
          Tích hợp Prophet model và dữ liệu thời tiết sẽ có trong Phase 2 để dự báo chính xác hơn.
        </p>
      </div>
    </div>
  );
};

export default HarvestPage;
