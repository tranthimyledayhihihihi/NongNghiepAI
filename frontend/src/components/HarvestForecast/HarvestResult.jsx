import { Calendar, TrendingUp } from 'lucide-react';

const HarvestResult = ({ result }) => {
  if (!result) {
    return (
      <div className="text-center text-gray-500 py-12">
        <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p>Nhập thông tin để dự báo thu hoạch</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="border rounded-lg p-4">
        <div className="flex items-center mb-2">
          <Calendar className="h-5 w-5 text-primary-600 mr-2" />
          <span className="text-sm font-medium text-gray-700">
            Ngày thu hoạch dự kiến
          </span>
        </div>
        <p className="text-2xl font-bold text-gray-900">
          {new Date(result.predictedHarvestDate).toLocaleDateString('vi-VN')}
        </p>
        <p className="text-sm text-gray-600 mt-1">
          Sau {result.growthDays} ngày kể từ ngày xuống giống
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

      <div className="bg-blue-50 rounded-lg p-4">
        <p className="text-sm font-medium text-blue-900 mb-2">Khuyến nghị:</p>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Chuẩn bị nhân lực trước 1 tuần</li>
          <li>• Theo dõi thời tiết để điều chỉnh kế hoạch</li>
          <li>• Chuẩn bị phương tiện vận chuyển</li>
        </ul>
      </div>
    </div>
  );
};

export default HarvestResult;
