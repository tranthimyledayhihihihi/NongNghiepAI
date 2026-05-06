import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip
} from 'chart.js';
import {
  AlertCircle,
  ChevronRight,
  Filter,
  Globe,
  MapPin,
  Sun,
  TrendingDown,
  TrendingUp
} from 'lucide-react';
import { useState } from 'react';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PricingDashboard = () => {
  const [selectedCrop, setSelectedCrop] = useState('Cà phê Robusta');
  const [forecastData, setForecastData] = useState(null);
  const [priceComparison, setPriceComparison] = useState([]);
  const [loading, setLoading] = useState(false);

  // Mock data - sẽ thay bằng API call thực tế
  const currentPrice = 42500;
  const priceChange = '+14.2%';
  const confidence = '92%';

  const regionalPrices = [
    {
      region: 'Đắk Lắk',
      subRegion: 'Tây Nguyên',
      price: 42800,
      change: '+1.2%',
      trend: 'up',
      status: 'CAO'
    },
    {
      region: 'Lâm Đồng',
      subRegion: 'Tây Nguyên',
      price: 43100,
      change: '+0.8%',
      trend: 'up',
      status: 'RẤT CAO'
    },
    {
      region: 'Long An',
      subRegion: 'Đồng bằng sông Cửu Long',
      price: 41500,
      change: '0.0%',
      trend: 'stable',
      status: 'BÌNH THƯỜNG'
    }
  ];

  const internationalPrices = [
    {
      market: 'London Robusta (LCE)',
      price: '$2,450/tấn',
      change: '(+2%)',
      flag: '🇬🇧'
    },
    {
      market: 'Brazilian Conillon',
      price: '$2,100/tấn (-1%)',
      change: '(-1%)',
      flag: '🇧🇷'
    }
  ];

  const weatherAlert = {
    type: 'Tác Động Thời Tiết',
    title: 'Mưa khô kéo dài ở Tây Nguyên dự báo sẽ làm giảm sản lượng thu hoạch 15%, gây ra đợt tăng giá mạnh vào đầu quý 4.',
    icon: <Sun className="w-6 h-6 text-yellow-500" />
  };

  // Chart data
  const chartData = {
    labels: ['Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8 (Dự kiến)', 'Tháng 9 (Dự kiến)', 'Tháng 10 (Dự kiến)'],
    datasets: [
      {
        label: 'Lịch sử',
        data: [38000, 39500, 41000, 40500, null, null, null],
        borderColor: '#15803d',
        backgroundColor: 'rgba(21, 128, 61, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 6
      },
      {
        label: 'Dự báo AI',
        data: [null, null, null, 40500, 42500, 44000, 45500],
        borderColor: '#15803d',
        backgroundColor: 'rgba(21, 128, 61, 0.1)',
        borderWidth: 3,
        borderDash: [5, 5],
        tension: 0.4,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 6
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
        padding: 12,
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#15803d',
        borderWidth: 1
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
            return value.toLocaleString() + ' ₫';
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
            <span>Thứ Năm, Thu Tư</span>
            <ChevronRight className="w-4 h-4" />
            <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-medium">
              CẬP NHẬT THỰC TIẾP
            </span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dự Báo Giá Thông Minh
          </h1>
          <p className="text-gray-600">
            Phân tích cà phê Robusta thời gian thực cho vùng Tây Nguyên & Đồng bằng sông Cửu Long.
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-500 mb-1">THIẾT LẬP THEO HIỆN TẠI</div>
          <div className="text-4xl font-bold text-gray-900">{currentPrice.toLocaleString()} VNĐ/kg</div>
          <div className="flex items-center justify-end space-x-2 mt-1">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <span className="text-green-600 font-semibold">{priceChange}</span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Chart */}
        <div className="lg:col-span-2 space-y-6">
          {/* Price Forecast Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">Dự Báo Giá</h2>
                <p className="text-sm text-gray-500">
                  Phân tích dữ liệu với dự báo 3 tháng tới bằng AI
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <button className="px-4 py-2 bg-green-700 text-white rounded-lg text-sm font-medium">
                  Lịch sử
                </button>
                <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">
                  Dự báo AI
                </button>
              </div>
            </div>

            {/* Chart */}
            <div className="h-80">
              <Line data={chartData} options={chartOptions} />
            </div>

            {/* Chart Legend */}
            <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-1 bg-green-700 rounded"></div>
                  <span className="text-sm text-gray-600">Độ tin cậy</span>
                  <span className="text-sm font-bold text-gray-900">{confidence}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-1 bg-green-700 rounded opacity-30"></div>
                  <span className="text-sm text-gray-600">Lợi nhuận dự kiến</span>
                  <span className="text-sm font-bold text-green-600">{priceChange}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">AI</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">6x</span>
              </div>
            </div>
          </div>

          {/* Regional Price Comparison */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                So Sánh Giá Theo Khu Vực
              </h2>
              <button className="flex items-center space-x-2 text-green-700 font-medium hover:text-green-800">
                <span>Lọc Khu Vực</span>
                <Filter className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-6 gap-4 text-xs font-medium text-gray-500 uppercase pb-2 border-b border-gray-200">
                <div className="col-span-2">Khu vực / Tỉnh thành</div>
                <div className="text-right">Giá hôm nay</div>
                <div className="text-right">Thay đổi 24h</div>
                <div className="text-right">Mức tồn kho</div>
                <div className="text-right">Hành động</div>
              </div>

              {regionalPrices.map((item, index) => (
                <div key={index} className="grid grid-cols-6 gap-4 items-center py-4 border-b border-gray-100 hover:bg-gray-50 transition">
                  <div className="col-span-2 flex items-center space-x-3">
                    <MapPin className="w-5 h-5 text-gray-400" />
                    <div>
                      <div className="font-bold text-gray-900">{item.region}</div>
                      <div className="text-sm text-gray-500">{item.subRegion}</div>
                    </div>
                  </div>
                  <div className="text-right font-bold text-gray-900">
                    {item.price.toLocaleString()} VNĐ/kg
                  </div>
                  <div className={`text-right font-semibold flex items-center justify-end space-x-1 ${item.trend === 'up' ? 'text-green-600' :
                      item.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                    }`}>
                    {item.trend === 'up' && <TrendingUp className="w-4 h-4" />}
                    {item.trend === 'down' && <TrendingDown className="w-4 h-4" />}
                    <span>{item.change}</span>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${item.status === 'RẤT CAO' ? 'bg-red-100 text-red-700' :
                        item.status === 'CAO' ? 'bg-orange-100 text-orange-700' :
                          'bg-green-100 text-green-700'
                      }`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="text-right">
                    <button className="text-green-700 font-medium hover:text-green-800">
                      Xem Chi Tiết
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Weather Impact */}
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-2xl border border-yellow-200 p-6">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center flex-shrink-0">
                {weatherAlert.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="font-bold text-gray-900">{weatherAlert.type}</h3>
                  <span className="text-xs text-gray-500">2 giờ trước</span>
                </div>
                <p className="text-gray-700 leading-relaxed">
                  {weatherAlert.title}
                </p>
              </div>
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
            </div>
          </div>

          {/* International Market */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Globe className="w-5 h-5 text-gray-600" />
              <h2 className="text-xl font-bold text-gray-900">Thị Trường Quốc Tế</h2>
              <span className="text-xs text-gray-500 ml-auto">Tự vấn cập nhật</span>
            </div>

            <div className="space-y-4">
              {internationalPrices.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{item.flag}</span>
                    <div>
                      <div className="font-medium text-gray-900">{item.market}</div>
                      <div className="text-sm text-gray-500">
                        Nhu cầu toàn cầu dự kiến tăng trong 3 tháng tới
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">{item.price}</div>
                    <div className={`text-sm ${item.change.includes('+') ? 'text-green-600' : 'text-red-600'}`}>
                      {item.change}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 text-sm text-gray-600 italic">
              Nhu cầu toàn cầu dự kiến tăng trong 3 tháng tới do mua vụ tại Brazil.
            </div>
          </div>
        </div>

        {/* Right Column - B2B Recommendation */}
        <div className="lg:col-span-1">
          <div className="bg-gradient-to-br from-green-800 to-green-900 rounded-2xl p-6 text-white sticky top-6">
            <div className="text-sm font-medium text-green-200 mb-2">
              KHUYẾN NGHỊ CHO BẠN
            </div>
            <h2 className="text-2xl font-bold mb-4">
              Xuất Khẩu B2B Trực Tiếp
            </h2>
            <p className="text-green-100 mb-6 leading-relaxed">
              Dựa trên lượng hiện tại của bạn thông AI và sự thiếu hụt toàn cầu, bán
              cho các nhà xuất khẩu trực tiếp sẽ mang lại lợi nhuận cao hơn 8% so với
              thương lái địa phương.
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="text-green-100">Giá Hợp Đồng: 46,200 VNĐ/kg</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="text-green-100">Thời Hạn Thanh Toán: T+2 Ngày</span>
              </div>
            </div>

            <button className="w-full bg-white text-green-800 py-3 rounded-xl font-bold hover:bg-green-50 transition">
              Liên Hệ Đại Lý Thu Mua
            </button>

            <div className="mt-6 pt-6 border-t border-green-700">
              <div className="text-sm text-green-200 mb-2">Tư vấn cập nhật</div>
              <div className="text-3xl font-bold mb-1">+4,500 VNĐ/kg</div>
              <div className="text-sm text-green-200">
                Giá lợi nhuận có thể giúp tăng doanh thu của bạn thêm khoảng 18.5 triệu VNĐ.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingDashboard;
