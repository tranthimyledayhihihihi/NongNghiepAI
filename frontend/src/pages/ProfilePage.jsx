import {
  Bell,
  Camera,
  Edit,
  Globe,
  Mail,
  MapPin,
  MoreVertical,
  Phone,
  Plus,
  Settings,
  Star
} from 'lucide-react';
import { useState } from 'react';

const ProfilePage = () => {
  const [editMode, setEditMode] = useState(false);
  const [language, setLanguage] = useState('vi');
  const [unit, setUnit] = useState('hecta');

  // User Profile Data
  const userProfile = {
    name: 'Nguyễn Văn An',
    avatar: 'https://i.pravatar.cc/150?img=12',
    location: 'Di Linh, Lâm Đồng, Việt Nam',
    phone: '+84 912 345 678',
    zaloId: 'an.nongnghiep.82',
    email: 'nguyenvanan@email.com',
    memberSince: 'Tháng 3, 2023',
    plan: 'Gói cao cấp',
    planBadge: 'GÓI HIỆN TẠI'
  };

  // Farm Areas
  const farmAreas = [
    {
      id: 1,
      name: 'Vườn Cà Phê Khu A',
      image: 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=400&fit=crop',
      area: '2.5',
      unit: 'Hecta',
      soilType: 'Đạt Độ Bazan',
      crop: 'Cà phê Robusta',
      status: 'Tốt',
      statusColor: 'bg-green-100 text-green-700',
      badge: 'Tốt',
      badgeColor: 'bg-green-500'
    },
    {
      id: 2,
      name: 'Vườn Tiêu Chân Đèo',
      image: 'https://images.unsplash.com/photo-1592419044706-39796d40f98c?w=600&h=400&fit=crop',
      area: '1.2',
      unit: 'Hecta',
      soilType: 'Đất Thịt Nhẹ',
      crop: 'Tiêu đen',
      status: 'Cần bón phân',
      statusColor: 'bg-yellow-100 text-yellow-700',
      badge: 'Cần bón phân',
      badgeColor: 'bg-yellow-500'
    }
  ];

  // Notification Settings
  const [notificationSettings, setNotificationSettings] = useState({
    weatherAlert: true,
    priceUpdate: true,
    harvestReminder: false
  });

  const handleToggleNotification = (key) => {
    setNotificationSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSaveProfile = () => {
    setEditMode(false);
    // API call to save profile
    console.log('Profile saved');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AgriAI Việt Nam
          </h1>
          <p className="text-gray-600">
            Hồ sơ người dùng & Quản lý trang trại
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
            <Settings className="w-4 h-4" />
            <span className="text-sm">Cài đặt</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Profile Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Profile Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="text-center mb-6">
              <div className="relative inline-block mb-4">
                <img
                  src={userProfile.avatar}
                  alt={userProfile.name}
                  className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
                />
                <button className="absolute bottom-0 right-0 w-8 h-8 bg-green-700 text-white rounded-full flex items-center justify-center hover:bg-green-800 transition">
                  <Camera className="w-4 h-4" />
                </button>
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-1">
                {userProfile.name}
              </h2>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-600 mb-3">
                <MapPin className="w-4 h-4" />
                <span>{userProfile.location}</span>
              </div>
              <div className="inline-flex items-center space-x-2 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full">
                <Star className="w-4 h-4 fill-current" />
                <span className="text-xs font-bold">{userProfile.planBadge}</span>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div className="flex items-center space-x-3">
                  <Phone className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-xs text-gray-500">SỐ ĐIỆN THOẠI</div>
                    <div className="font-medium text-gray-900">{userProfile.phone}</div>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div className="flex items-center space-x-3">
                  <Mail className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-xs text-gray-500">ID ZALO</div>
                    <div className="font-medium text-gray-900">{userProfile.zaloId}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-xl p-4 text-white mb-4">
              <div className="text-sm text-green-200 mb-1">{userProfile.planBadge}</div>
              <div className="text-xl font-bold mb-2">{userProfile.plan}</div>
              <p className="text-sm text-green-100 mb-4">
                Mở khóa phân tích sâu AI và tư vấn trực tiếp từ chuyên gia Lâm nghiệp.
              </p>
              <div className="space-y-2 mb-4">
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span>Quét bệnh cây trồng không giới hạn</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <span>Dự báo thời tiết nông vụ chi tiết</span>
                </div>
              </div>
              <button className="w-full bg-white text-green-800 py-2 rounded-lg font-medium hover:bg-green-50 transition text-sm">
                Gia hạn ngay
              </button>
            </div>

            <button
              onClick={() => setEditMode(!editMode)}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 border-2 border-green-700 text-green-700 rounded-xl hover:bg-green-50 transition font-medium"
            >
              <Edit className="w-5 h-5" />
              <span>Chỉnh sửa hồ sơ</span>
            </button>
          </div>
        </div>

        {/* Right Column - Farm Areas & Settings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Farm Areas */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Trang trại của tôi
              </h2>
              <button className="flex items-center space-x-2 px-4 py-2 bg-green-700 text-white rounded-xl hover:bg-green-800 transition">
                <Plus className="w-5 h-5" />
                <span>Thêm mảnh vườn</span>
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-6">
              {farmAreas.map((farm) => (
                <div key={farm.id} className="bg-white border-2 border-gray-200 rounded-2xl overflow-hidden hover:shadow-lg transition">
                  <div className="relative h-48">
                    <img
                      src={farm.image}
                      alt={farm.name}
                      className="w-full h-full object-cover"
                    />
                    <div className={`absolute top-3 left-3 ${farm.badgeColor} text-white px-3 py-1 rounded-full text-xs font-bold`}>
                      {farm.badge}
                    </div>
                    <button className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full flex items-center justify-center hover:bg-gray-100 transition">
                      <MoreVertical className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-gray-900 mb-3">
                      {farm.name}
                    </h3>
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">DIỆN TÍCH</span>
                        <span className="font-bold text-gray-900">{farm.area} {farm.unit}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">LOẠI ĐẤT</span>
                        <span className="font-bold text-gray-900">{farm.soilType}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 mb-3">
                      <Leaf className="w-4 h-4 text-green-600" />
                      <span className="text-sm text-gray-700">{farm.crop}</span>
                    </div>
                    <button className="w-full text-green-700 font-medium hover:text-green-800 text-sm flex items-center justify-center space-x-1">
                      <span>Chi tiết</span>
                      <span>→</span>
                    </button>
                  </div>
                </div>
              ))}

              {/* Add New Farm Card */}
              <div className="border-2 border-dashed border-gray-300 rounded-2xl p-8 flex flex-col items-center justify-center hover:border-green-500 hover:bg-green-50 transition cursor-pointer">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <Plus className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="font-bold text-gray-900 mb-2">
                  Thêm mảnh vườn mới
                </h3>
                <p className="text-sm text-gray-600 text-center">
                  Đăng ký thêm vị trí địa lý để AI theo dõi tốt hơn
                </p>
              </div>
            </div>
          </div>

          {/* Settings Section */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Notification Settings */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Bell className="w-5 h-5 text-gray-700" />
                <h3 className="font-bold text-gray-900">Cài đặt thông báo</h3>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-gray-700">Cảnh báo thời tiết cực đoan</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.weatherAlert}
                      onChange={() => handleToggleNotification('weatherAlert')}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-gray-700">Cập nhật giá thị trường</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.priceUpdate}
                      onChange={() => handleToggleNotification('priceUpdate')}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm text-gray-700">Nhắc nhở lịch bón phân</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.harvestReminder}
                      onChange={() => handleToggleNotification('harvestReminder')}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>
                </div>
              </div>

              <p className="text-xs text-gray-500 mt-4">
                Thông báo sẽ được gửi qua Zalo và Email
              </p>
            </div>

            {/* Language & Region */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Globe className="w-5 h-5 text-gray-700" />
                <h3 className="font-bold text-gray-900">Ngôn ngữ & Vùng</h3>
              </div>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    NGÔN NGỮ HIỆN THI
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="vi">Tiếng Việt (Mặc định)</option>
                    <option value="en">English</option>
                    <option value="zh">中文</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ĐƠN VỊ ĐO LƯỜNG
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setUnit('hecta')}
                      className={`px-4 py-3 rounded-lg font-medium transition ${unit === 'hecta'
                          ? 'bg-green-700 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      Hecta (m²)
                    </button>
                    <button
                      onClick={() => setUnit('acre')}
                      className={`px-4 py-3 rounded-lg font-medium transition ${unit === 'acre'
                          ? 'bg-green-700 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                    >
                      Acre (Mẫu Anh)
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex space-x-3">
                <button className="flex-1 px-4 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium">
                  Lưu thay đổi
                </button>
                <button className="px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition">
                  Hủy
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
