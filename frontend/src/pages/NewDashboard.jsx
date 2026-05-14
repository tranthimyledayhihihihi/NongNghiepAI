import {
  Calendar,
  CheckCircle,
  ChevronRight,
  Droplet,
  Leaf,
  Package,
  Sun,
  Thermometer,
  TrendingUp
} from 'lucide-react';
import { useState } from 'react';
import { Line } from 'react-chartjs-2';

const NewDashboard = () => {
  const [marketView, setMarketView] = useState('week'); // 'week' or 'month'

  // KPI Cards Data
  const kpiData = [
    {
      icon: <TrendingUp className="w-6 h-6 text-green-600" />,
      label: 'GIÁ THỊ TRƯỜNG TRUNG BÌNH',
      value: '18,500',
      unit: 'VNĐ/kg',
      change: '+12.4%',
      changeType: 'up',
      bgColor: 'bg-green-50'
    },
    {
      icon: <Package className="w-6 h-6 text-yellow-600" />,
      label: 'LÔ HÀNG CHỜ KIỂM ĐỊNH',
      value: '08',
      unit: 'Lô hàng',
      change: 'Ưu tiên',
      changeType: 'warning',
      bgColor: 'bg-yellow-50'
    },
    {
      icon: <Calendar className="w-6 h-6 text-orange-600" />,
      label: 'NGÀY THU HOẠCH TIẾP THEO',
      value: '07 Th11',
      unit: 'Lúa Jasmine',
      change: 'Còn 14 ngày',
      changeType: 'neutral',
      bgColor: 'bg-orange-50'
    }
  ];

  // Recent Alerts
  const alerts = [
    {
      type: 'weather',
      icon: <Sun className="w-5 h-5 text-yellow-600" />,
      title: 'Cảnh Báo Thời Tiết',
      description: 'Chỉ số nhiệt độ cao dự báo tại Kiên Giang. Xem xét chu...',
      time: '2 giờ trước',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    },
    {
      type: 'price',
      icon: <TrendingUp className="w-5 h-5 text-green-600" />,
      title: 'Cảnh Báo Giá',
      description: 'Giá lúa5451 giảm đột ngột 5% tại vùng An Giang. Khuyến...',
      time: '3 giờ trước',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    },
    {
      type: 'quality',
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
      title: 'Kiểm Định Hoàn Tất',
      description: 'Lô hàng #4492 đã đạt chuẩn Hạng Cao Cấp với độ đo...',
      time: 'Hôm qua',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    }
  ];

  // Market Chart Data
  const marketChartData = {
    labels: ['THL 2', 'THL 3', 'THL 4', 'THL 5', 'THL 6', 'THL 7', 'CHỦ NHẬT'],
    datasets: [
      {
        label: 'Jasmine 85',
        data: [17500, 17800, 18000, 18200, 18100, 18300, 18500],
        borderColor: '#15803d',
        backgroundColor: 'rgba(21, 128, 61, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 5
      },
      {
        label: 'OM 5451',
        data: [16800, 17000, 17200, 17100, 17300, 17500, 17400],
        borderColor: '#6b7280',
        backgroundColor: 'rgba(107, 114, 128, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 5
      }
    ]
  };

  const marketChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        align: 'end',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12
          }
        }
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
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 11
          }
        }
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

  // Weather & Farm Data
  const weatherData = [
    {
      icon: <Droplet className="w-6 h-6 text-blue-600" />,
      label: 'Độ Ẩm Đất',
      value: '32%',
      bgColor: 'bg-blue-50'
    },
    {
      icon: <Thermometer className="w-6 h-6 text-orange-600" />,
      label: 'Nhiệt Độ',
      value: '28°C',
      bgColor: 'bg-orange-50'
    }
  ];

  const farmAreas = [
    {
      name: 'Khu Vực Phía Bắc B',
      status: 'Địa hình tốt',
      progress: 74,
      details: 'Hệ thống tưới tự động đang chạy • Ước đo 74%',
      icon: '🌾'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Tổng Quan Bảng Điều Khiển
          </h1>
          <p className="text-gray-600">
            Giám sát hiệu quả canh tác tại khu vực Đồng bằng sông Cửu Long.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-lg px-4 py-2">
          <Calendar className="w-5 h-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-900">24 Tháng 10, 2023</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {kpiData.map((kpi, index) => (
          <div key={index} className={`${kpi.bgColor} rounded-2xl p-6 border border-gray-200`}>
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 ${kpi.bgColor} rounded-xl flex items-center justify-center`}>
                {kpi.icon}
              </div>
              {kpi.changeType === 'up' && (
                <div className="flex items-center space-x-1 text-green-600">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-sm font-semibold">{kpi.change}</span>
                </div>
              )}
            </div>
            <div className="text-sm text-gray-600 mb-2">{kpi.label}</div>
            <div className="flex items-baseline space-x-2">
              <div className="text-3xl font-bold text-gray-900">{kpi.value}</div>
              <div className="text-sm text-gray-600">{kpi.unit}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Market Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Market Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                  Tổng Quan Thị Trường
                </h2>
                <p className="text-sm text-gray-500">
                  Xu hướng giá tại các vùng lúa trong điểm
                </p>
              </div>
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setMarketView('week')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${marketView === 'week'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  Tuần
                </button>
                <button
                  onClick={() => setMarketView('month')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${marketView === 'month'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  Tháng
                </button>
              </div>
            </div>

            <div className="h-80">
              <Line data={marketChartData} options={marketChartOptions} />
            </div>
          </div>

          {/* Farm Area Card */}
          <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-2xl overflow-hidden shadow-lg">
            <div className="relative h-64">
              <img
                src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=400&fit=crop"
                alt="Farm Area"
                className="w-full h-full object-cover opacity-40"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-green-900 to-transparent"></div>

              <div className="absolute bottom-6 left-6 right-6">
                <div className="inline-block bg-green-700 text-white px-3 py-1 rounded-full text-xs font-medium mb-3">
                  Địa hình Tốt Ju
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">
                  Khu Vực Phía Bắc B
                </h3>
                <p className="text-green-100 text-sm mb-4">
                  Hệ thống tưới tự động đang chạy • Ước đo 74%
                </p>
                <div className="flex items-center space-x-4">
                  <button className="bg-white text-green-800 px-6 py-2 rounded-lg font-medium hover:bg-green-50 transition">
                    Xem Chi Tiết
                  </button>
                  <ChevronRight className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Alerts & Weather */}
        <div className="lg:col-span-1 space-y-6">
          {/* Alerts */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Thông Báo Gần Đây
              </h2>
              <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full">
                2
              </span>
            </div>

            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`${alert.bgColor} border ${alert.borderColor} rounded-xl p-4 hover:shadow-md transition`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">{alert.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="text-sm font-bold text-gray-900">
                          {alert.title}
                        </h3>
                        <span className="text-xs text-gray-500">{alert.time}</span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">
                        {alert.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full mt-4 text-green-700 font-medium hover:text-green-800 text-sm flex items-center justify-center space-x-1">
              <span>Xem Tất Cả Thông Báo</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Weather Cards */}
          <div className="grid grid-cols-2 gap-4">
            {weatherData.map((weather, index) => (
              <div
                key={index}
                className={`${weather.bgColor} rounded-xl p-4 border border-gray-200`}
              >
                <div className="mb-3">{weather.icon}</div>
                <div className="text-xs text-gray-600 mb-1">{weather.label}</div>
                <div className="text-2xl font-bold text-gray-900">{weather.value}</div>
              </div>
            ))}
          </div>

          {/* Disease Risk */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Leaf className="w-6 h-6 text-green-700" />
              <h3 className="font-bold text-gray-900">Nguy Cơ Sâu Bệnh</h3>
            </div>
            <p className="text-sm text-gray-700 mb-4">
              Khu cầu xuất khẩu Philippines tăng 15% đối với dòng lúa Indica.
              Cũng nên chốt giá cao?
            </p>
            <button className="text-green-700 font-medium hover:text-green-800 text-sm flex items-center space-x-1">
              <span>Xem chi tiết hơn</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Estimated Yield */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Package className="w-6 h-6 text-green-700" />
              <h3 className="font-bold text-gray-900">Sản Lượng Ước Tính</h3>
            </div>
            <div className="text-center py-4">
              <div className="text-5xl font-bold text-green-700 mb-2">12.2t</div>
              <div className="text-sm text-gray-600">Dự kiến thu hoạch</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewDashboard;
