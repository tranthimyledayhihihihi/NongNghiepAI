import {
  AlertTriangle,
  Bell,
  CheckCircle,
  ChevronDown,
  Mail,
  MapPin,
  MessageSquare,
  Plus,
  Smartphone,
  Sun,
  TrendingDown,
  TrendingUp,
  X
} from 'lucide-react';
import { useState } from 'react';

const AlertManagementPage = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedAlertType, setSelectedAlertType] = useState('price');
  const [notificationSettings, setNotificationSettings] = useState({
    zalo: true,
    sms: false,
    email: true
  });

  // Active Alerts
  const activeAlerts = [
    {
      id: 1,
      type: 'price',
      icon: <TrendingUp className="w-6 h-6 text-orange-600" />,
      title: 'Cảnh báo Giá',
      subtitle: 'Gạo Jasmine 85',
      location: 'Long An',
      condition: 'Ngưỡng +/- 5%',
      status: 'ĐANG HOẠT ĐỘNG',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200'
    },
    {
      id: 2,
      type: 'weather',
      icon: <Sun className="w-6 h-6 text-green-600" />,
      title: 'Cảnh báo Thời tiết',
      subtitle: 'Mưa lớn & Sông nhiệt',
      location: 'Đồng bằng sông Cửu Long',
      condition: 'Cập nhật thời gian thực',
      status: 'ĐANG HOẠT ĐỘNG',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    },
    {
      id: 3,
      type: 'pest',
      icon: <AlertTriangle className="w-6 h-6 text-yellow-600" />,
      title: 'Cảnh báo Sâu bệnh',
      subtitle: 'Cảnh báo Rầy nâu',
      location: '',
      condition: 'Trong tầm chính DBSCL',
      status: 'ĐANG HOẠT ĐỘNG',
      tags: ['Cảnh động lúa'],
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    }
  ];

  // Alert History
  const alertHistory = [
    {
      id: 1,
      icon: <TrendingDown className="w-5 h-5 text-red-600" />,
      title: 'Cảnh báo sóng nhiệt trong 48 giờ tới',
      subtitle: 'Cảnh báo Thời tiết • Đồng bằng sông Cửu Long',
      time: '24 thg 10, 10:00 SA',
      bgColor: 'bg-red-50'
    },
    {
      id: 2,
      icon: <TrendingUp className="w-5 h-5 text-orange-600" />,
      title: 'Giá Jasmine 85 tăng 2% tại Long An',
      subtitle: 'Cảnh báo Giá • Thị trường Long An',
      time: '23 thg 10, 03:30 CH',
      bgColor: 'bg-orange-50'
    },
    {
      id: 3,
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
      title: 'Đã có báo cáo phân tích thị trường hàng tuần',
      subtitle: 'Thông báo Hệ thống • Thông tin chuyên sâu',
      time: '22 thg 10, 09:15 SA',
      bgColor: 'bg-green-50'
    }
  ];

  const handleToggleNotification = (type) => {
    setNotificationSettings(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Trung tâm Cảnh báo & Đăng ký
        </h1>
        <p className="text-gray-600">
          Quản lý các cảnh báo thời gian thực về giá thật/Vụng, điều kiện thời tiết và dịch bệnh sâu bệnh.
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Active Alerts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Alerts Section */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                  Đăng ký đang hoạt động
                </h2>
                <p className="text-sm text-gray-500">
                  <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs font-medium">
                    3 Cảnh báo đang hoạt động
                  </span>
                </p>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-green-700 text-white px-6 py-3 rounded-xl font-medium hover:bg-green-800 transition flex items-center space-x-2"
              >
                <Plus className="w-5 h-5" />
                <span>Thêm Cảnh báo Mới</span>
              </button>
            </div>

            <div className="space-y-4">
              {activeAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`${alert.bgColor} border ${alert.borderColor} rounded-2xl p-6 hover:shadow-md transition`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      <div className={`${alert.bgColor} rounded-xl p-3`}>
                        {alert.icon}
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900 mb-1">
                          {alert.title}
                        </h3>
                        <p className="text-sm text-gray-700 mb-2">
                          {alert.subtitle}
                        </p>
                        {alert.location && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
                            <MapPin className="w-4 h-4" />
                            <span>{alert.location}</span>
                          </div>
                        )}
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Bell className="w-4 h-4" />
                          <span>{alert.condition}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">
                        {alert.status}
                      </span>
                      <button className="text-gray-400 hover:text-red-600 transition">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  {alert.tags && (
                    <div className="flex flex-wrap gap-2">
                      {alert.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="bg-white px-3 py-1 rounded-full text-xs text-gray-700 border border-gray-200"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Alert History */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Lịch sử thông báo
              </h2>
              <button className="text-green-700 font-medium hover:text-green-800 text-sm">
                Xem tất cả lịch sử →
              </button>
            </div>

            <div className="space-y-4">
              {alertHistory.map((item) => (
                <div
                  key={item.id}
                  className={`${item.bgColor} rounded-xl p-4 hover:shadow-md transition cursor-pointer`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 mt-1">
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-gray-900 mb-1">
                        {item.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">
                        {item.subtitle}
                      </p>
                      <span className="text-xs text-gray-500">
                        {item.time}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Notification Settings */}
        <div className="lg:col-span-1 space-y-6">
          {/* Notification Methods */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Bell className="w-5 h-5 text-gray-700" />
              <h2 className="text-xl font-bold text-gray-900">
                Phương thức nhận tin
              </h2>
            </div>

            <div className="space-y-4">
              {/* Zalo */}
              <div className="flex items-center justify-between p-4 bg-blue-50 rounded-xl border border-blue-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-medium text-gray-900">
                    Zalo Official Account
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationSettings.zalo}
                    onChange={() => handleToggleNotification('zalo')}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                </label>
              </div>

              {/* SMS */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-400 rounded-lg flex items-center justify-center">
                    <Smartphone className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-medium text-gray-900">
                    Thông báo SMS
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationSettings.sms}
                    onChange={() => handleToggleNotification('sms')}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                </label>
              </div>

              {/* Email */}
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-xl border border-green-200">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-medium text-gray-900">
                    Bản tin Email
                  </span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationSettings.email}
                    onChange={() => handleToggleNotification('email')}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Create New Alert Card */}
          <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-2xl p-6 text-white">
            <h3 className="text-xl font-bold mb-3">
              Thêm Cảnh báo Mới
            </h3>
            <p className="text-green-100 text-sm mb-6">
              Thiết lập quy tắc giám sát tùy chỉnh cho trang trại của bạn.
            </p>

            {/* Alert Type Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-green-100 mb-2">
                LOẠI CẢNH BÁO
              </label>
              <div className="relative">
                <select
                  value={selectedAlertType}
                  onChange={(e) => setSelectedAlertType(e.target.value)}
                  className="w-full bg-green-800 text-white px-4 py-3 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="price">Giá Thị trường</option>
                  <option value="weather">Thời tiết</option>
                  <option value="pest">Sâu bệnh</option>
                  <option value="harvest">Thu hoạch</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-green-300 pointer-events-none" />
              </div>
            </div>

            {/* Region Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-green-100 mb-2">
                KHU VỰC / CẢNH BÁO ĐỊ NG
              </label>
              <input
                type="text"
                placeholder="VD: Cần Thơ"
                className="w-full bg-green-800 text-white placeholder-green-300 px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <button
              onClick={() => setShowCreateModal(true)}
              className="w-full bg-white text-green-800 py-3 rounded-xl font-bold hover:bg-green-50 transition flex items-center justify-center space-x-2"
            >
              <CheckCircle className="w-5 h-5" />
              <span>Kích hoạt Giám sát</span>
            </button>
          </div>

          {/* AI Help Card */}
          <div className="bg-gray-50 rounded-2xl border border-gray-200 p-6 text-center">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <Bell className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="font-bold text-gray-900 mb-2">
              Cần mô hình AI tùy chỉnh?
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Các kỹ sư của chúng tôi có thể giúp lập thuật toán phát hiện sâu bệnh riêng cho địa hình của bạn.
            </p>
            <button className="text-green-700 font-medium hover:text-green-800 text-sm">
              Trao đổi với chuyên gia
            </button>
          </div>
        </div>
      </div>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Tạo Cảnh Báo Mới
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            {/* Modal content here */}
            <p className="text-gray-600 mb-6">
              Form tạo cảnh báo sẽ được hiển thị ở đây...
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                Hủy
              </button>
              <button className="px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition">
                Tạo Cảnh Báo
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertManagementPage;
