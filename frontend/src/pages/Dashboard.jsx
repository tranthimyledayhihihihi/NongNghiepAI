import { ArrowRight, Cloud, Droplets, MapPin, Sparkles, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  // Mock data - sẽ được thay thế bằng API calls
  const featuredCrop = {
    name: 'Lúa OM 5451',
    location: 'Cần Thơ, Việt Nam',
    price: 18500,
    change: '+2.4%',
    trend: 'up',
    lastUpdate: 'Cập nhật 15 phút trước'
  };

  const forecast7Days = [
    { day: '18', date: 'T3', price: 18750, change: 'ĐỘ TIN CẬY CAO', trend: 'up' },
    { day: '19', date: 'T4', price: 19100, change: 'ĐỘ TIN CẬY CAO', trend: 'up' },
    { day: '20', date: 'T5', price: 19050, change: 'ĐỘ TIN CẬY TB', trend: 'neutral' },
  ];

  const regionalPrices = [
    { region: 'Hà Nội (Bắc Bộ)', price: 18900, unit: 'VNĐ/kg' },
    { region: 'Cần Thơ (Mekong)', price: 18500, unit: 'VNĐ/kg' },
    { region: 'Đắk Lắk (T. Nguyên)', price: 17200, unit: 'VNĐ/kg' },
  ];

  const aiRecommendation = {
    title: 'Nên Giữ Lại (HOLD)',
    description: 'Dựa trên xu hướng xuất khẩu và dự báo thời tiết, giá lúa có khả năng tăng mạnh trong 10 ngày tới.',
    confidence: '+5.2%',
    period: 'trong 10 ngày'
  };

  const weather = {
    temp: 28,
    condition: 'Nắng nhẹ',
    humidity: '85%',
    rainfall: 'Dự báo mưa vào 5 ngày tới'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Chào mừng trở lại! 👋</h1>
        <p className="text-gray-600 mt-1">Đây là tổng quan thị trường nông sản hôm nay</p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Featured Crop */}
        <div className="lg:col-span-2 space-y-6">
          {/* Featured Crop Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700 mb-2">
                  THỊTRƯỜNG NỔI BẬT HÔM NAY
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mt-2">{featuredCrop.name}</h2>
                <p className="text-sm text-gray-600 flex items-center mt-1">
                  <MapPin className="w-4 h-4 mr-1" />
                  {featuredCrop.location}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center text-emerald-600 text-sm font-medium">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  {featuredCrop.change}
                </div>
                <p className="text-xs text-gray-500 mt-1">{featuredCrop.lastUpdate}</p>
              </div>
            </div>

            <div className="mb-6">
              <div className="text-4xl font-bold text-gray-900">
                {featuredCrop.price.toLocaleString()}
                <span className="text-lg text-gray-600 font-normal ml-2">VNĐ/kg</span>
              </div>
            </div>

            <button className="w-full bg-emerald-800 text-white py-3 rounded-lg hover:bg-emerald-900 transition-colors flex items-center justify-center">
              <span className="mr-2">🔔</span>
              Đặt Cảnh Báo Giá
            </button>
          </div>

          {/* 7-Day Forecast */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Dự Báo 7 Ngày</h3>
                <p className="text-sm text-gray-500 italic mt-1">
                  "Xu hướng giá định nhịp như cầu tiêu thụ nội địa tăng 3% so với tuần trước."
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {forecast7Days.map((day, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">{day.day}</div>
                      <div className="text-xs text-gray-500">{day.date}</div>
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-gray-900">
                        {day.price.toLocaleString()}
                      </div>
                      <div className={`text-xs font-medium ${day.change.includes('CAO') ? 'text-emerald-600' : 'text-orange-600'
                        }`}>
                        {day.change}
                      </div>
                    </div>
                  </div>
                  <div>
                    {day.trend === 'up' && <TrendingUp className="w-5 h-5 text-emerald-600" />}
                    {day.trend === 'neutral' && <ArrowRight className="w-5 h-5 text-gray-400" />}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Regional Comparison */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">So Sánh Vùng Miền</h3>

            {/* Map placeholder */}
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-8 mb-4 flex items-center justify-center">
              <div className="text-center">
                <MapPin className="w-12 h-12 text-emerald-600 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Bản đồ giá theo khu vực</p>
              </div>
            </div>

            <div className="space-y-2">
              {regionalPrices.map((region, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${idx === 0 ? 'bg-emerald-500' : idx === 1 ? 'bg-emerald-400' : 'bg-emerald-300'
                      }`} />
                    <span className="text-sm text-gray-700">{region.region}</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    {region.price.toLocaleString()} {region.unit}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - AI Insights & Weather */}
        <div className="space-y-6">
          {/* AI Recommendation */}
          <div className="bg-gradient-to-br from-emerald-800 to-emerald-900 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center mb-3">
              <Sparkles className="w-5 h-5 mr-2" />
              <span className="text-sm font-medium">Khuyến Nghị AI</span>
            </div>

            <h3 className="text-2xl font-bold mb-3">{aiRecommendation.title}</h3>

            <p className="text-emerald-100 text-sm mb-4">
              {aiRecommendation.description}
            </p>

            <div className="bg-emerald-700/50 rounded-lg p-4 mb-4">
              <div className="text-sm text-emerald-200 mb-1">LỢI NHUẬN DỰ KIẾN</div>
              <div className="text-3xl font-bold">{aiRecommendation.confidence}</div>
              <div className="text-sm text-emerald-200">{aiRecommendation.period}</div>
            </div>

            <Link
              to="/pricing"
              className="block w-full bg-white text-emerald-900 text-center py-3 rounded-lg font-medium hover:bg-emerald-50 transition-colors"
            >
              Xem Chi Tiết →
            </Link>
          </div>

          {/* Weather Card */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Thời tiết sắp tới</h3>
              <Cloud className="w-6 h-6 text-gray-400" />
            </div>

            <div className="text-center mb-4">
              <div className="text-5xl font-bold text-gray-900">{weather.temp}°C</div>
              <p className="text-gray-600 mt-2">{weather.condition}</p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center">
                  <Droplets className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="text-sm text-gray-700">Độ ẩm</span>
                </div>
                <span className="text-sm font-semibold text-gray-900">{weather.humidity}</span>
              </div>

              <div className="p-3 bg-amber-50 rounded-lg">
                <p className="text-sm text-amber-800">{weather.rainfall}</p>
              </div>
            </div>
          </div>

          {/* Market News */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tin tức thị trường</h3>

            <div className="space-y-4">
              <div className="pb-4 border-b border-gray-200">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 mr-3" />
                  <div>
                    <p className="text-sm text-gray-900 font-medium">
                      Xuất khẩu gạo tăng 15%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">2 giờ trước</p>
                  </div>
                </div>
              </div>

              <div className="pb-4 border-b border-gray-200">
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3" />
                  <div>
                    <p className="text-sm text-gray-900 font-medium">
                      Dự báo mưa ảnh hưởng thu hoạch
                    </p>
                    <p className="text-xs text-gray-500 mt-1">5 giờ trước</p>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex items-start">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 mr-3" />
                  <div>
                    <p className="text-sm text-gray-900 font-medium">
                      Giá phân bón giảm 8%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">1 ngày trước</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
