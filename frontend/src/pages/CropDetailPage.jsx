import {
  Bell,
  ChevronLeft,
  Droplet,
  Leaf,
  MapPin,
  Share2,
  Thermometer,
  TrendingDown,
  TrendingUp,
  Wind
} from 'lucide-react';
import { useState } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import { useNavigate, useParams } from 'react-router-dom';

const CropDetailPage = () => {
  const { cropId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('30N'); // 30N, 90N, 1N

  // Mock data - sẽ thay bằng API call
  const cropData = {
    name: 'Lúa OM 5451',
    category: 'Ô Cần Thơ, Việt Nam',
    currentPrice: 18500,
    priceChange: '+2.4%',
    changeAmount: '+450',
    lastUpdate: 'Cập nhật 5 phút trước',
    status: 'THIẾT LẬP HÔM NAY'
  };

  const forecast7Days = [
    { date: '18', price: 18750, change: '+250', status: 'up' },
    { date: '19', price: 19100, change: '+350', status: 'up' },
    { date: '20', price: 19050, change: '-50', status: 'down' }
  ];

  const regionalPrices = [
    { region: 'Hà Nội', subRegion: 'Bắc Bộ', price: 18900, unit: 'VNĐ/kg' },
    { region: 'Cần Thơ', subRegion: 'Mekong', price: 18500, unit: 'VNĐ/kg' },
    { region: 'Bắc Lắc', subRegion: 'T. Nguyên', price: 17200, unit: 'VNĐ/kg' }
  ];

  const weatherData = {
    humidity: '32%',
    temperature: '28°C',
    rainfall: 'Thấp',
    disease: 'Khu vực xuất khẩu Philippines tăng 15% đối với dòng lúa Indica. Cũng nên chốt giá cao?',
    estimatedYield: '12.2t'
  };

  // Chart data for 30-day trend
  const chartData = {
    labels: Array.from({ length: 30 }, (_, i) => `Ngày ${i + 1}`),
    datasets: [
      {
        label: 'Giá trung bình',
        data: [
          17800, 17900, 18000, 17950, 18100, 18200, 18150, 18300, 18250, 18400,
          18350, 18500, 18450, 18600, 18550, 18700, 18650, 18800, 18750, 18900,
          18850, 19000, 18950, 19100, 19050, 19200, 19150, 19300, 19250, 18500
        ],
        borderColor: '#15803d',
        backgroundColor: 'rgba(21, 128, 61, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 5
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12
      }
    },
    scales: {
      x: {
        display: false
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function (value) {
            return (value / 1000).toFixed(0) + 'k';
          }
        }
      }
    }
  };

  // Bar chart for 30-day comparison
  const barChartData = {
    labels: ['01 TH05', '15 TH05', '30 TH05'],
    datasets: [
      {
        data: [17800, 18500, 19250],
        backgroundColor: (context) => {
          const value = context.parsed.y;
          if (value < 18000) return 'rgba(34, 197, 94, 0.3)';
          if (value < 19000) return 'rgba(34, 197, 94, 0.6)';
          return 'rgba(21, 128, 61, 1)';
        },
        borderRadius: 8,
        barThickness: 60
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return context.parsed.y.toLocaleString() + ' VNĐ/kg';
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        display: false
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
      >
        <ChevronLeft className="w-5 h-5" />
        <span>Quay lại</span>
      </button>

      {/* Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="inline-block bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-medium mb-3">
              {cropData.status}
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {cropData.name}
            </h1>
            <p className="text-gray-600 flex items-center space-x-2">
              <MapPin className="w-4 h-4" />
              <span>{cropData.category}</span>
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button className="p-3 border-2 border-gray-300 rounded-xl hover:border-green-700 hover:text-green-700 transition">
              <Share2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex items-end justify-between">
          <div>
            <div className="text-5xl font-bold text-gray-900 mb-2">
              {cropData.currentPrice.toLocaleString()}
              <span className="text-2xl text-gray-500 ml-2">VNĐ/kg</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1 text-green-600">
                <TrendingUp className="w-5 h-5" />
                <span className="font-semibold">{cropData.priceChange}</span>
              </div>
              <span className="text-gray-500">{cropData.changeAmount} VNĐ hôm nay</span>
            </div>
          </div>
          <button className="bg-green-700 text-white px-8 py-4 rounded-xl font-bold hover:bg-green-800 transition flex items-center space-x-2">
            <Bell className="w-5 h-5" />
            <span>Đặt Cảnh Báo Giá</span>
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* 7-Day Forecast */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Dự Báo 7 Ngày</h2>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-500">Cập nhật theo thời gian thực</span>
              </div>
            </div>

            <div className="space-y-3">
              {forecast7Days.map((day, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">{day.date}</div>
                      <div className="text-xs text-gray-500">Tháng 5</div>
                    </div>
                    <div>
                      <div className="text-xl font-bold text-gray-900">
                        {day.price.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-500">VNĐ/kg dự cập</div>
                    </div>
                  </div>
                  <div className={`flex items-center space-x-2 ${day.status === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                    {day.status === 'up' ? (
                      <TrendingUp className="w-5 h-5" />
                    ) : (
                      <TrendingDown className="w-5 h-5" />
                    )}
                    <span className="font-semibold">{day.change}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <p className="text-sm text-gray-700 italic">
                "Xu hướng ổn định nên cân nhắc bán trong tuần này."
              </p>
            </div>
          </div>

          {/* Price Trend Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Biến Động Giá (30 ngày)
              </h2>
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('30N')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === '30N'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  30N
                </button>
                <button
                  onClick={() => setActiveTab('90N')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === '90N'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  90N
                </button>
                <button
                  onClick={() => setActiveTab('1N')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === '1N'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  1N
                </button>
              </div>
            </div>

            <div className="h-64 mb-6">
              <Line data={chartData} options={chartOptions} />
            </div>

            <div className="h-48">
              <Bar data={barChartData} options={barChartOptions} />
            </div>
          </div>

          {/* Regional Map */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              So Sánh Vùng Miền
            </h2>

            {/* Map Placeholder */}
            <div className="relative h-96 bg-gradient-to-br from-green-50 to-green-100 rounded-xl mb-6 overflow-hidden">
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Vietnam_location_map.svg/800px-Vietnam_location_map.svg.png"
                alt="Vietnam Map"
                className="w-full h-full object-contain opacity-20"
              />

              {/* Price Markers */}
              <div className="absolute top-1/4 left-1/2 transform -translate-x-1/2">
                <div className="bg-white rounded-lg shadow-lg p-3 border-2 border-green-500">
                  <div className="text-xs text-gray-600">Hà Nội</div>
                  <div className="text-lg font-bold text-gray-900">18,900</div>
                </div>
              </div>

              <div className="absolute bottom-1/3 left-1/3">
                <div className="bg-white rounded-lg shadow-lg p-3 border-2 border-green-500">
                  <div className="text-xs text-gray-600">Cần Thơ</div>
                  <div className="text-lg font-bold text-gray-900">18,500</div>
                </div>
              </div>

              <div className="absolute top-1/2 right-1/4">
                <div className="bg-white rounded-lg shadow-lg p-3 border-2 border-orange-500">
                  <div className="text-xs text-gray-600">Đắc Lắc</div>
                  <div className="text-lg font-bold text-gray-900">17,200</div>
                </div>
              </div>
            </div>

            {/* Regional Price List */}
            <div className="space-y-3">
              {regionalPrices.map((region, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${index === 0 ? 'bg-green-500' :
                        index === 1 ? 'bg-green-500' : 'bg-orange-500'
                      }`}></div>
                    <div>
                      <div className="font-bold text-gray-900">{region.region}</div>
                      <div className="text-sm text-gray-500">{region.subRegion}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">
                      {region.price.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">{region.unit}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Weather & Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Weather Cards */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Tình trạng kho</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-xl">
                <div className="flex items-center space-x-3">
                  <Droplet className="w-6 h-6 text-blue-600" />
                  <span className="text-gray-700">Độ Ẩm Đất</span>
                </div>
                <span className="text-xl font-bold text-gray-900">{weatherData.humidity}</span>
              </div>

              <div className="flex items-center justify-between p-4 bg-orange-50 rounded-xl">
                <div className="flex items-center space-x-3">
                  <Thermometer className="w-6 h-6 text-orange-600" />
                  <span className="text-gray-700">Nhiệt Độ</span>
                </div>
                <span className="text-xl font-bold text-gray-900">{weatherData.temperature}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Thời tiết sắp tới</h3>
            <div className="p-4 bg-gray-50 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <Wind className="w-5 h-5 text-gray-600" />
                <span className="text-sm text-gray-600">Mưa nhẹ dự kiến trong 3 ngày tới</span>
              </div>
              <p className="text-sm text-gray-700">
                {weatherData.rainfall}
              </p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Leaf className="w-6 h-6 text-green-700" />
              <h3 className="font-bold text-gray-900">Nguy Cơ Sâu Bệnh</h3>
            </div>
            <p className="text-sm text-gray-700 mb-4">
              {weatherData.disease}
            </p>
            <button className="text-green-700 font-medium hover:text-green-800 text-sm">
              Xem chi tiết hơn cảo →
            </button>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Sản Lượng Ước Tính</h3>
            <div className="text-center py-6">
              <div className="text-5xl font-bold text-green-700 mb-2">
                {weatherData.estimatedYield}
              </div>
              <div className="text-gray-600">tấn dự kiến</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CropDetailPage;
