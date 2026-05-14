import {
  AlertCircle,
  CheckCircle,
  DollarSign,
  Download,
  Droplet,
  FileText,
  Leaf,
  Package,
  Shield,
  Sun,
  Thermometer,
  TrendingUp,
  Truck,
  Users,
  Wind
} from 'lucide-react';
import { useState } from 'react';

const HarvestForecastPage = () => {
  const [cropType, setCropType] = useState('rice');
  const [plantingDate, setPlantingDate] = useState('2024-10-15');
  const [fieldType, setFieldType] = useState('auto');
  const [confidenceScore, setConfidenceScore] = useState(84);

  // Harvest Timeline Data
  const harvestTimeline = [
    {
      phase: 'Giai đoạn Sinh trưởng',
      status: 'completed',
      date: 'Th01 24',
      icon: <Leaf className="w-5 h-5" />,
      color: 'bg-green-600'
    },
    {
      phase: 'Thời điểm Chín',
      status: 'current',
      date: 'Th01 24',
      icon: <Sun className="w-5 h-5" />,
      color: 'bg-yellow-500',
      highlight: '+ ĐỊNH KIỂM TỐI ƯU'
    },
    {
      phase: 'Dự kiến Thu hoạch',
      status: 'upcoming',
      date: '04 Th02 - 18 Th02',
      icon: <Package className="w-5 h-5" />,
      color: 'bg-green-500'
    }
  ];

  // Yield Estimate
  const yieldEstimate = {
    amount: '4.2',
    unit: 'Tấn/Hecta',
    change: '+12%',
    comparison: 'so với vụ trước'
  };

  // Revenue Estimate
  const revenueEstimate = {
    amount: '$18,460',
    currency: 'USD',
    note: 'Dựa trên giá thị trường hiện tại'
  };

  // Environmental Factors
  const environmentalFactors = [
    {
      icon: <Droplet className="w-6 h-6 text-blue-600" />,
      label: 'Lượng Bình thường',
      value: '28°C',
      status: 'good',
      percentage: 85
    },
    {
      icon: <Thermometer className="w-6 h-6 text-orange-600" />,
      label: 'Nhiệt độ',
      value: '28°C',
      status: 'good',
      percentage: 75
    },
    {
      icon: <Wind className="w-6 h-6 text-gray-600" />,
      label: 'Cường độ UV',
      value: 'Cao',
      status: 'warning',
      percentage: 90
    },
    {
      icon: <Sun className="w-6 h-6 text-yellow-600" />,
      label: 'Độ ẩm',
      value: '62%',
      status: 'good',
      percentage: 62
    }
  ];

  // Strategic Recommendations
  const recommendations = [
    {
      icon: <Users className="w-6 h-6 text-green-700" />,
      title: 'Chuẩn bị Nhân lực',
      description: 'Đặt trước đội ngũ thu hoạch từ 12-15 người trước ngày 05/01 để đảm bảo nhân lực trong giai đoạn cao điểm.',
      action: 'Quản lý Nhân lực →'
    },
    {
      icon: <Truck className="w-6 h-6 text-green-700" />,
      title: 'Logistics & Lưu kho',
      description: 'Đảm bảo 400 mét khối không gian lưu kho khô ráo. Lên lịch vận chuyển vào ngày 05/02 và 12/02.',
      action: 'Kiểm tra Kho bãi →'
    },
    {
      icon: <Shield className="w-6 h-6 text-green-700" />,
      title: 'Cảnh báo Sâu bệnh',
      description: 'AI phát hiện sự gia tăng 15% hoạt động của rầy nâu (Nilaparvata lugens) trong vùng. Kiểm tra các khu trung tâm hàng tuần.',
      action: 'Chạy Chẩn đoán →'
    }
  ];

  const handleUpdateForecast = () => {
    // API call to update forecast
    console.log('Updating forecast...');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="inline-block bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-medium mb-3">
            PHÂN TÍCH DỰ ĐOÁN
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dự báo Thu hoạch
          </h1>
          <p className="text-gray-600">
            Trực quan hóa và lập kế hoạch sản lượng cây trồng với mô hình AI chính xác.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-6 py-3 border-2 border-gray-300 rounded-xl hover:border-green-700 hover:text-green-700 transition font-medium">
            <Download className="w-5 h-5" />
            <span>Xuất Báo cáo</span>
          </button>
          <button className="flex items-center space-x-2 px-6 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium">
            <FileText className="w-5 h-5" />
            <span>Lên Lịch Công việc</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Forecast Form & Timeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Forecast Input Form */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Leaf className="w-6 h-6 text-green-700" />
              <h2 className="text-xl font-bold text-gray-900">
                Cấu hình Dự báo
              </h2>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Crop Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loại Cây trồng
                </label>
                <select
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="rice">Lúa (Oryza sativa)</option>
                  <option value="corn">Ngô</option>
                  <option value="coffee">Cà phê</option>
                  <option value="pepper">Hồ tiêu</option>
                </select>
              </div>

              {/* Planting Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ngày Gieo trồng
                </label>
                <input
                  type="date"
                  value={plantingDate}
                  onChange={(e) => setPlantingDate(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              {/* Field Area */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chỉ số Dinh dưỡng Đất
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value="84%"
                    readOnly
                    className="w-full px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-700 font-bold"
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  </div>
                </div>
              </div>

              {/* Field Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loại Hình Tưới tiêu
                </label>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setFieldType('auto')}
                    className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${fieldType === 'auto'
                        ? 'bg-green-700 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                  >
                    Tự động
                  </button>
                  <button
                    onClick={() => setFieldType('manual')}
                    className={`flex-1 px-4 py-3 rounded-lg font-medium transition ${fieldType === 'manual'
                        ? 'bg-green-700 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                  >
                    Thủ công
                  </button>
                </div>
              </div>
            </div>

            <button
              onClick={handleUpdateForecast}
              className="w-full mt-6 bg-green-700 text-white py-4 rounded-xl font-bold hover:bg-green-800 transition"
            >
              Cập nhật Dự đoán
            </button>
          </div>

          {/* Harvest Timeline */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Lịch trình Thu hoạch
              </h2>
              <div className="flex items-center space-x-2">
                <button className="px-4 py-2 bg-green-700 text-white rounded-lg text-sm font-medium">
                  Hàng tuần
                </button>
                <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">
                  Hàng tháng
                </button>
              </div>
            </div>

            {/* Timeline */}
            <div className="relative">
              {harvestTimeline.map((phase, index) => (
                <div key={index} className="flex items-start space-x-4 mb-8 last:mb-0">
                  {/* Icon */}
                  <div className={`${phase.color} w-12 h-12 rounded-xl flex items-center justify-center text-white flex-shrink-0`}>
                    {phase.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-gray-900">{phase.phase}</h3>
                      <span className="text-sm text-gray-500">{phase.date}</span>
                    </div>
                    {phase.highlight && (
                      <div className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-bold">
                        {phase.highlight}
                      </div>
                    )}
                    {phase.status === 'current' && (
                      <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                      </div>
                    )}
                  </div>

                  {/* Status Badge */}
                  {phase.status === 'completed' && (
                    <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                  )}
                  {phase.status === 'current' && (
                    <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse flex-shrink-0 mt-2"></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Yield & Revenue Cards */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Yield Estimate */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Package className="w-6 h-6 text-green-700" />
                <h3 className="font-bold text-gray-900">SẢN LƯỢNG ƯỚC TÍNH</h3>
              </div>
              <div className="flex items-baseline space-x-2 mb-2">
                <span className="text-5xl font-bold text-green-700">
                  {yieldEstimate.amount}
                </span>
                <span className="text-xl text-gray-600">{yieldEstimate.unit}</span>
              </div>
              <div className="flex items-center space-x-2 text-green-600">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm font-semibold">{yieldEstimate.change}</span>
                <span className="text-sm text-gray-600">{yieldEstimate.comparison}</span>
              </div>
            </div>

            {/* Revenue Estimate */}
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl border border-yellow-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <DollarSign className="w-6 h-6 text-yellow-700" />
                <h3 className="font-bold text-gray-900">DOANH THU DỰ KIẾN</h3>
              </div>
              <div className="text-5xl font-bold text-yellow-700 mb-2">
                {revenueEstimate.amount}
              </div>
              <div className="flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-yellow-600" />
                <span className="text-sm text-gray-600">{revenueEstimate.note}</span>
              </div>
            </div>
          </div>

          {/* Strategic Recommendations */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Đề xuất Lập kế hoạch Chiến lược
            </h2>

            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded-xl p-6 hover:shadow-md transition"
                >
                  <div className="flex items-start space-x-4">
                    <div className="bg-green-100 rounded-xl p-3 flex-shrink-0">
                      {rec.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 mb-2">
                        {rec.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">
                        {rec.description}
                      </p>
                      <button className="text-green-700 font-medium hover:text-green-800 text-sm">
                        {rec.action}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - AI Confidence & Environmental Factors */}
        <div className="lg:col-span-1 space-y-6">
          {/* AI Confidence Score */}
          <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-2xl p-6 text-white">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-6 h-6" />
              <h3 className="font-bold">ĐIỂM TIN CẬY</h3>
            </div>
            <div className="text-6xl font-bold mb-4">
              {confidenceScore}%
            </div>
            <p className="text-green-100 text-sm mb-6">
              Dựa trên dữ liệu thời tiết 5 năm qua và độ ẩm đất hiện tại của vùng.
            </p>
            <div className="bg-green-800 rounded-xl p-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-green-200">Độ chính xác mô hình</span>
                <span className="font-bold">94.2%</span>
              </div>
              <div className="w-full bg-green-900 rounded-full h-2">
                <div className="bg-green-400 h-2 rounded-full" style={{ width: '94.2%' }}></div>
              </div>
            </div>
          </div>

          {/* Environmental Factors */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-6">
              Các Yếu tố Ảnh hưởng Môi trường
            </h3>

            <div className="space-y-4">
              {environmentalFactors.map((factor, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {factor.icon}
                      <div>
                        <div className="text-sm text-gray-600">{factor.label}</div>
                        <div className="font-bold text-gray-900">{factor.value}</div>
                      </div>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${factor.status === 'good' ? 'bg-green-500' :
                          factor.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                      style={{ width: `${factor.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-start space-x-2">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  RỦI RO THẤP: Khu cầu xuất khẩu Philippines tăng 15% đối với dòng lúa Indica. Cũng nên chốt giá cao?
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HarvestForecastPage;
