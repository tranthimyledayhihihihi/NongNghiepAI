import {
  Calendar,
  CheckCircle,
  Clock,
  DollarSign,
  Download,
  FileText,
  Filter,
  MoreVertical,
  Package,
  TrendingUp
} from 'lucide-react';
import { useState } from 'react';
import { Bar } from 'react-chartjs-2';

const ReportsPage = () => {
  const [timeFilter, setTimeFilter] = useState('month'); // week, month, all
  const [exportFormat, setExportFormat] = useState('csv');

  // Summary Cards Data
  const summaryCards = [
    {
      icon: <DollarSign className="w-6 h-6 text-green-600" />,
      label: 'TỔNG DOANH THU MÙA TRƯỚC',
      value: '452,000,000',
      unit: 'đ',
      change: '+12.4%',
      changeType: 'up',
      bgColor: 'bg-green-50',
      progress: 75
    },
    {
      icon: <Package className="w-6 h-6 text-yellow-600" />,
      label: 'CHẤT LƯỢNG TRUNG BÌNH',
      value: 'Hạng A',
      subtitle: 'Dựa trên 154 đợt kiểm định',
      bgColor: 'bg-yellow-50',
      badge: 'Hạng A'
    },
    {
      icon: <TrendingUp className="w-6 h-6 text-red-600" />,
      label: 'TỔNG SẢN LƯỢNG',
      value: '24.8',
      unit: 'Tấn',
      subtitle: 'Vượt chỉ tiêu 2.1 tấn',
      bgColor: 'bg-red-50',
      badge: 'Tốt lắm'
    }
  ];

  // Sales Trend Chart Data
  const chartData = {
    labels: ['T1', 'T2', 'T3', 'T4', 'T5'],
    datasets: [
      {
        label: 'Giá thật/Vụng',
        data: [320000, 380000, 350000, 450000, 400000],
        backgroundColor: '#15803d',
        borderRadius: 8,
        barThickness: 60
      },
      {
        label: 'Chất lượng',
        data: [280000, 340000, 310000, 410000, 360000],
        backgroundColor: '#9ca3af',
        borderRadius: 8,
        barThickness: 60
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
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        callbacks: {
          label: function (context) {
            return context.dataset.label + ': ' + context.parsed.y.toLocaleString() + ' đ';
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
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          callback: function (value) {
            return (value / 1000) + 'k';
          }
        }
      }
    }
  };

  // Sales History Data
  const salesHistory = [
    {
      id: 1,
      date: '12/10/2023',
      crop: 'Lúa ST25',
      grade: 'Grade A++',
      gradeColor: 'bg-green-100 text-green-700',
      price: 22500,
      quantity: 1250,
      status: 'Đã xuất kho',
      statusColor: 'text-green-600',
      statusIcon: <CheckCircle className="w-4 h-4" />
    },
    {
      id: 2,
      date: '08/10/2023',
      crop: 'Cà phê Robusta',
      grade: 'Grade B+',
      gradeColor: 'bg-yellow-100 text-yellow-700',
      price: 48200,
      quantity: 850,
      status: 'Đang kiểm định',
      statusColor: 'text-yellow-600',
      statusIcon: <Clock className="w-4 h-4" />
    },
    {
      id: 3,
      date: '05/10/2023',
      crop: 'Lúa ST25',
      grade: 'Grade A',
      gradeColor: 'bg-green-100 text-green-700',
      price: 21800,
      quantity: 2100,
      status: 'Đã thanh toán',
      statusColor: 'text-green-600',
      statusIcon: <CheckCircle className="w-4 h-4" />
    },
    {
      id: 4,
      date: '01/10/2023',
      crop: 'Cacao Thô',
      grade: 'Grade A',
      gradeColor: 'bg-green-100 text-green-700',
      price: 55000,
      quantity: 420,
      status: 'Hoàn tất',
      statusColor: 'text-green-600',
      statusIcon: <CheckCircle className="w-4 h-4" />
    }
  ];

  // Expert Analysis
  const expertAnalysis = {
    title: 'Phân tích chuyên sâu',
    content: 'AI đề xuất tối ưu hóa quy trình bón phân để tăng thêm 5% chất lượng loại A.',
    suggestions: [
      {
        icon: <Package className="w-5 h-5 text-green-600" />,
        title: 'Gọi ý phân bón',
        description: 'Giảm 10% Đạm kỳ ba'
      },
      {
        icon: <Calendar className="w-5 h-5 text-blue-600" />,
        title: 'Tưới tiêu',
        description: 'Duy trì độ ẩm 65%'
      }
    ]
  };

  const handleExport = (format) => {
    console.log(`Exporting as ${format}...`);
    // API call to export data
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Báo cáo chi tiết
          </h1>
          <p className="text-gray-600">
            Hồ sơ người dùng & Quản lý trang trại
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
            <Filter className="w-4 h-4" />
            <span className="text-sm">Lọc</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {summaryCards.map((card, index) => (
          <div key={index} className={`${card.bgColor} rounded-2xl p-6 border border-gray-200`}>
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 ${card.bgColor} rounded-xl flex items-center justify-center`}>
                {card.icon}
              </div>
              {card.change && (
                <div className={`flex items-center space-x-1 ${card.changeType === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-sm font-semibold">{card.change}</span>
                </div>
              )}
              {card.badge && (
                <span className={`${card.gradeColor || 'bg-yellow-100 text-yellow-700'} px-3 py-1 rounded-full text-xs font-bold`}>
                  {card.badge}
                </span>
              )}
            </div>
            <div className="text-sm text-gray-600 mb-2">{card.label}</div>
            <div className="flex items-baseline space-x-2 mb-2">
              <div className="text-3xl font-bold text-gray-900">{card.value}</div>
              {card.unit && <div className="text-lg text-gray-600">{card.unit}</div>}
            </div>
            {card.subtitle && (
              <div className="text-sm text-gray-600">{card.subtitle}</div>
            )}
            {card.progress && (
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${card.progress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Chart & Table */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sales Trend Chart */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                  Xu hướng nghiệp suất
                </h2>
                <p className="text-sm text-gray-500">
                  So sánh Giá thật/Vụng vs. Chất lượng
                </p>
              </div>
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setTimeFilter('week')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${timeFilter === 'week'
                      ? 'bg-white text-gray-900 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  Tháng
                </button>
                <button
                  onClick={() => setTimeFilter('month')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition ${timeFilter === 'month'
                      ? 'bg-green-700 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                    }`}
                >
                  Quý
                </button>
              </div>
            </div>

            <div className="h-80 mb-4">
              <Bar data={chartData} options={chartOptions} />
            </div>

            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-700 rounded"></div>
                <span className="text-gray-600">Giá thật/Vụng</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-gray-400 rounded"></div>
                <span className="text-gray-600">Chất lượng</span>
              </div>
            </div>
          </div>

          {/* Sales History Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Lịch sử bán ghi
              </h2>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleExport('csv')}
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
                >
                  <FileText className="w-4 h-4" />
                  <span>CSV</span>
                </button>
                <button
                  onClick={() => handleExport('excel')}
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
                >
                  <FileText className="w-4 h-4" />
                  <span>Excel</span>
                </button>
                <button
                  onClick={() => handleExport('pdf')}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition text-sm"
                >
                  <Download className="w-4 h-4" />
                  <span>PDF</span>
                </button>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-6">
              Hiển thị lịch sử hoạch và giao dịch gần nhất
            </p>

            {/* Table Filters */}
            <div className="flex items-center space-x-4 mb-4 text-sm">
              <button className="px-4 py-2 bg-gray-100 rounded-lg font-medium">
                Tất cả
              </button>
              <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                Lúa gạo
              </button>
              <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg">
                Cà phê
              </button>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Ngày ghi nhận
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Loại cây trồng
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Phân loại chất lượng
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Giá thị trường (đ/kg)
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Sản lượng (kg)
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Trạng thái
                    </th>
                    <th className="text-center py-3 px-4 text-xs font-medium text-gray-500 uppercase">
                      Hành động
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {salesHistory.map((record) => (
                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                      <td className="py-4 px-4 text-sm text-gray-900">
                        {record.date}
                      </td>
                      <td className="py-4 px-4 text-sm font-medium text-gray-900">
                        {record.crop}
                      </td>
                      <td className="py-4 px-4">
                        <span className={`${record.gradeColor} px-3 py-1 rounded-full text-xs font-bold`}>
                          {record.grade}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-sm text-right font-semibold text-gray-900">
                        {record.price.toLocaleString()}
                      </td>
                      <td className="py-4 px-4 text-sm text-right text-gray-900">
                        {record.quantity.toLocaleString()}
                      </td>
                      <td className="py-4 px-4">
                        <div className={`flex items-center space-x-2 ${record.statusColor}`}>
                          {record.statusIcon}
                          <span className="text-sm font-medium">{record.status}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <button className="text-gray-400 hover:text-gray-600">
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-600">
                Hiển thị 4 trong số 128 bản ghi
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Trang:</span>
                <button className="w-8 h-8 bg-green-700 text-white rounded-lg font-medium">
                  1
                </button>
                <button className="w-8 h-8 hover:bg-gray-100 rounded-lg font-medium">
                  2
                </button>
                <button className="w-8 h-8 hover:bg-gray-100 rounded-lg font-medium">
                  3
                </button>
                <button className="px-3 h-8 hover:bg-gray-100 rounded-lg font-medium text-sm">
                  Sau
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Expert Analysis */}
        <div className="lg:col-span-1 space-y-6">
          {/* Expert Analysis Card */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200 p-6">
            <h3 className="font-bold text-gray-900 mb-4">
              {expertAnalysis.title}
            </h3>
            <p className="text-sm text-gray-700 mb-6">
              {expertAnalysis.content}
            </p>

            <div className="space-y-4">
              {expertAnalysis.suggestions.map((suggestion, index) => (
                <div key={index} className="bg-white rounded-xl p-4">
                  <div className="flex items-start space-x-3">
                    <div className="bg-green-100 rounded-lg p-2">
                      {suggestion.icon}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm mb-1">
                        {suggestion.title}
                      </div>
                      <div className="text-xs text-gray-600">
                        {suggestion.description}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button className="w-full mt-6 bg-green-700 text-white py-3 rounded-xl font-medium hover:bg-green-800 transition">
              Xem chi tiết phân tích
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
