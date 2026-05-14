import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle,
  DollarSign,
  Download,
  Filter,
  Globe,
  Package,
  ShoppingCart,
  Store,
  Target,
  TrendingDown,
  TrendingUp,
  Users
} from 'lucide-react';
import { useState } from 'react';

const MarketStrategyPage = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('all');
  const [timeRange, setTimeRange] = useState('month');

  // Market Strategies
  const strategies = [
    {
      id: 1,
      icon: <Users className="w-6 h-6 text-green-600" />,
      title: 'Trực tiếp B2B',
      subtitle: 'Bán hàng trực tiếp cho nhà phân phối',
      percentage: '20-30%',
      profitMargin: '25-30%',
      color: 'bg-green-50',
      borderColor: 'border-green-200',
      badge: 'Lợi nhuận cao',
      badgeColor: 'bg-green-100 text-green-700'
    },
    {
      id: 2,
      icon: <Globe className="w-6 h-6 text-blue-600" />,
      title: 'Xuất khẩu',
      subtitle: 'Thị trường EU, Mỹ đặc, Hoa Kỳ',
      percentage: '40-60%',
      profitMargin: '40-60%',
      color: 'bg-blue-50',
      borderColor: 'border-blue-200',
      badge: 'Quy mô lớn',
      badgeColor: 'bg-blue-100 text-blue-700'
    },
    {
      id: 3,
      icon: <Store className="w-6 h-6 text-yellow-600" />,
      title: 'Chợ đầu mối',
      subtitle: 'Giao dịch Mỗi tuần tại thành phố',
      percentage: '10-15%',
      profitMargin: '10-15%',
      color: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      badge: 'Ổn định',
      badgeColor: 'bg-yellow-100 text-yellow-700'
    },
    {
      id: 4,
      icon: <ShoppingCart className="w-6 h-6 text-purple-600" />,
      title: 'Bán lẻ Online',
      subtitle: 'Thương mại điện tử, Xong nội khối, Ứng dụng',
      percentage: '20-30%',
      profitMargin: '20-30%',
      color: 'bg-purple-50',
      borderColor: 'border-purple-200',
      badge: 'Phát triển',
      badgeColor: 'bg-purple-100 text-purple-700'
    }
  ];

  // Financial Overview
  const financialData = {
    totalRevenue: '1.28B',
    totalCost: '420.5M',
    profit: '859.5M',
    profitMargin: '67%',
    growth: '+15.2%'
  };

  // Crop Recommendations Table
  const cropRecommendations = [
    {
      id: 1,
      crop: 'Lúa gạo ST25',
      grade: 'Xuất khẩu',
      gradeColor: 'bg-green-100 text-green-700',
      marketPrice: '38,000 - 42,000',
      strategy: 'Lúa gạo ST25',
      strategyIcon: <Globe className="w-4 h-4" />,
      profitMargin: '+12%',
      profitColor: 'text-green-600',
      action: 'Hạp đồi kỳ vọi',
      actionColor: 'text-green-600'
    },
    {
      id: 2,
      crop: 'Cà phê Robusta',
      grade: 'Trực tiếp cao',
      gradeColor: 'bg-green-100 text-green-700',
      marketPrice: '95,000 - 102,000',
      strategy: 'Trực tiếp cao',
      strategyIcon: <Users className="w-4 h-4" />,
      profitMargin: '+3%',
      profitColor: 'text-green-600',
      action: 'Trung gian thời điểm',
      actionColor: 'text-yellow-600'
    },
    {
      id: 3,
      crop: 'Thanh long Ruột đỏ',
      grade: 'Bán tại thị trường',
      gradeColor: 'bg-red-100 text-red-700',
      marketPrice: '25,000 - 28,000',
      strategy: 'Bán tại thị trường',
      strategyIcon: <Store className="w-4 h-4" />,
      profitMargin: '-3%',
      profitColor: 'text-red-600',
      action: 'Giảm phí bán (tránh lỗ)',
      actionColor: 'text-red-600'
    }
  ];

  // Regional Map Data (simplified)
  const regionalData = [
    { region: 'Miền Bắc', demand: 'Cao', price: 'Tăng 5%' },
    { region: 'Miền Trung', demand: 'Trung bình', price: 'Ổn định' },
    { region: 'Miền Nam', demand: 'Rất cao', price: 'Tăng 8%' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AgriAI Việt Nam
          </h1>
          <p className="text-gray-600">
            Trang chủ / Thị trường / Chiến lược
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
            <Filter className="w-4 h-4" />
            <span className="text-sm">Lọc</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition">
            <Download className="w-4 h-4" />
            <span className="text-sm">Tải báo cáo</span>
          </button>
        </div>
      </div>

      {/* Financial Overview Cards */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="w-8 h-8 text-green-600" />
            <div className="flex items-center space-x-1 text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-semibold">{financialData.growth}</span>
            </div>
          </div>
          <div className="text-sm text-gray-600 mb-2">CHI PHÍ HÀNH</div>
          <div className="text-3xl font-bold text-gray-900">{financialData.totalCost}</div>
          <div className="text-xs text-gray-500 mt-1">VNĐ</div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6 border border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-bold">
              Mục tiêu
            </span>
          </div>
          <div className="text-sm text-gray-600 mb-2">DOANH THU DỰ KIẾN</div>
          <div className="text-3xl font-bold text-gray-900">{financialData.totalRevenue}</div>
          <div className="text-xs text-gray-500 mt-1">VNĐ</div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6 border border-purple-200">
          <div className="flex items-center justify-between mb-4">
            <Target className="w-8 h-8 text-purple-600" />
            <CheckCircle className="w-5 h-5 text-purple-600" />
          </div>
          <div className="text-sm text-gray-600 mb-2">LỢI NHUẬN</div>
          <div className="text-3xl font-bold text-gray-900">{financialData.profit}</div>
          <div className="text-xs text-gray-500 mt-1">VNĐ</div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-6 border border-yellow-200">
          <div className="flex items-center justify-between mb-4">
            <Package className="w-8 h-8 text-yellow-600" />
          </div>
          <div className="text-sm text-gray-600 mb-2">TỈ SUẤT LỢI NHUẬN</div>
          <div className="text-3xl font-bold text-gray-900">{financialData.profitMargin}</div>
          <div className="text-xs text-gray-500 mt-1">Biên lợi nhuận</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Strategies */}
        <div className="lg:col-span-2 space-y-6">
          {/* Market Strategies */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                  Khuyến nghị Chi tiết theo Cây trồng
                </h2>
                <p className="text-sm text-gray-500">
                  Phân tích dựa trên thị trường hiện tại và xu hướng
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mb-6">
              {strategies.map((strategy) => (
                <div
                  key={strategy.id}
                  className={`${strategy.color} border-2 ${strategy.borderColor} rounded-2xl p-6 hover:shadow-lg transition cursor-pointer`}
                  onClick={() => setSelectedStrategy(strategy.id)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`${strategy.color} rounded-xl p-3`}>
                      {strategy.icon}
                    </div>
                    <span className={`${strategy.badgeColor} px-3 py-1 rounded-full text-xs font-bold`}>
                      {strategy.badge}
                    </span>
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">
                    {strategy.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {strategy.subtitle}
                  </p>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs text-gray-500">Biên lợi nhuận</div>
                      <div className="text-lg font-bold text-gray-900">{strategy.profitMargin}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">Tỷ trọng</div>
                      <div className="text-lg font-bold text-gray-900">{strategy.percentage}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Crop Recommendations Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Khuyến nghị Chi tiết theo Cây trồng
              </h2>
              <div className="flex items-center space-x-2 text-sm">
                <button className="px-4 py-2 bg-gray-100 rounded-lg font-medium">
                  Miền Bắc
                </button>
                <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                  Miền Trung
                </button>
                <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                  Miền Nam
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Loại cây trồng
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Phân loại chất lượng
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Kênh tối ưu
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Giá dự kiến (VNĐ/kg)
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Xu hướng cầu
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Rủi ro
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Hành động
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {cropRecommendations.map((crop) => (
                    <tr key={crop.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                      <td className="py-4 px-4 text-sm font-medium text-gray-900">
                        {crop.crop}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`${crop.gradeColor} px-3 py-1 rounded-full text-xs font-bold`}>
                          {crop.grade}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-end space-x-2">
                          {crop.strategyIcon}
                          <span className="text-sm text-gray-900">{crop.strategy}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-sm text-right font-semibold text-gray-900">
                        {crop.marketPrice}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <div className={`flex items-center justify-end space-x-1 ${crop.profitColor}`}>
                          {crop.profitMargin.includes('+') ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          )}
                          <span className="text-sm font-semibold">{crop.profitMargin}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-600">
                        Hạp đồi kỳ vọi
                      </td>
                      <td className="py-4 px-4 text-right">
                        <span className={`text-sm font-medium ${crop.actionColor}`}>
                          {crop.action}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right Column - Regional Map & Insights */}
        <div className="lg:col-span-1 space-y-6">
          {/* Regional Map */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-6">Bản đồ Cửu Vùng</h3>

            {/* Map Placeholder */}
            <div className="relative h-64 bg-gradient-to-br from-green-50 to-green-100 rounded-xl mb-6 overflow-hidden">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Vietnam_location_map.svg/800px-Vietnam_location_map.svg.png"
                alt="Vietnam Map"
                className="w-full h-full object-contain opacity-20"
              />

              {/* Regional Markers */}
              <div className="absolute top-1/4 left-1/2 transform -translate-x-1/2">
                <div className="bg-green-500 text-white rounded-lg shadow-lg p-2 text-xs font-bold">
                  Miền Bắc
                </div>
              </div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2">
                <div className="bg-yellow-500 text-white rounded-lg shadow-lg p-2 text-xs font-bold">
                  Miền Trung
                </div>
              </div>
              <div className="absolute bottom-1/4 left-1/2 transform -translate-x-1/2">
                <div className="bg-blue-500 text-white rounded-lg shadow-lg p-2 text-xs font-bold">
                  Miền Nam
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {regionalData.map((region, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div>
                    <div className="font-medium text-gray-900 text-sm">{region.region}</div>
                    <div className="text-xs text-gray-600">Cầu: {region.demand}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-green-600">{region.price}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-2xl p-6 text-white">
            <div className="flex items-center space-x-2 mb-4">
              <AlertCircle className="w-6 h-6" />
              <h3 className="font-bold">Phân tích AI</h3>
            </div>
            <p className="text-green-100 text-sm mb-6">
              Dựa trên xu hướng thị trường hiện tại, chúng tôi khuyến nghị tập trung vào xuất khẩu
              cho Lúa ST25 và B2B cho Cà phê Robusta để tối đa hóa lợi nhuận.
            </p>
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-2 text-sm">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>Cầu xuất khẩu tăng 15%</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>Giá B2B ổn định</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <AlertCircle className="w-5 h-5 text-yellow-400" />
                <span>Chợ đầu mối có rủi ro</span>
              </div>
            </div>
            <button className="w-full bg-white text-green-800 py-3 rounded-xl font-bold hover:bg-green-50 transition">
              Xem chi tiết phân tích
            </button>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Hành động nhanh</h3>
            <div className="space-y-3">
              <button className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition">
                <span className="text-sm text-gray-700">Tìm đối tác B2B</span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </button>
              <button className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition">
                <span className="text-sm text-gray-700">Đăng ký xuất khẩu</span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </button>
              <button className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition">
                <span className="text-sm text-gray-700">Xem giá chợ đầu mối</span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketStrategyPage;
