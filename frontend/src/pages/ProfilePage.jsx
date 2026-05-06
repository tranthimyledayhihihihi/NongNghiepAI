import {
  Bell,
  Camera,
  CheckCircle2,
  Globe,
  Mail,
  MapPin,
  Phone,
  Plus,
  Settings,
  Sprout,
  Star,
} from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const farmAreas = [];

const ProfilePage = () => {
  const { user } = useAuth();
  const [notificationSettings, setNotificationSettings] = useState({
    weatherAlert: true,
    priceUpdate: true,
    harvestReminder: false,
  });
  const [language, setLanguage] = useState('vi');
  const [unit, setUnit] = useState('hectare');

  const displayUser = {
    name: user?.name || 'Chưa cập nhật',
    email: user?.email || 'Chưa cập nhật',
    phone: user?.phone || 'Chưa cập nhật',
    region: user?.region || 'Chưa cập nhật',
    role: user?.role || 'farmer',
  };

  const initials =
    displayUser.name
      .split(' ')
      .filter(Boolean)
      .slice(-2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'AI';

  const toggleNotification = (key) => {
    setNotificationSettings((current) => ({ ...current, [key]: !current[key] }));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Hồ sơ</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Tài khoản & trang trại</h1>
          <p className="mt-2 text-gray-600">Quản lý thông tin cá nhân, khu canh tác và thiết lập hiển thị.</p>
        </div>
        <Link
          to="/settings"
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
        >
          <Settings className="h-4 w-4" />
          Cài đặt
        </Link>
      </div>

      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <aside className="space-y-6">
          <section className="rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm">
            <div className="relative mx-auto mb-4 inline-block">
              <div className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-white bg-green-700 text-2xl font-bold text-white shadow-lg">
                {initials}
              </div>
              <button
                type="button"
                className="absolute bottom-0 right-0 flex h-8 w-8 items-center justify-center rounded-full bg-green-700 text-white hover:bg-green-800"
                aria-label="Đổi ảnh đại diện"
              >
                <Camera className="h-4 w-4" />
              </button>
            </div>
            <h2 className="text-xl font-bold text-gray-900">{displayUser.name}</h2>
            <div className="mt-2 flex items-center justify-center gap-2 text-sm text-gray-600">
              <MapPin className="h-4 w-4" />
              <span>{displayUser.region}</span>
            </div>
            <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-amber-100 px-4 py-2 text-amber-800">
              <Star className="h-4 w-4 fill-current" />
              <span className="text-xs font-bold">Gói hiện tại</span>
            </div>

            <div className="mt-6 space-y-3 text-left">
              <div className="rounded-lg bg-gray-50 p-3">
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-gray-500" />
                  <div className="min-w-0">
                    <div className="text-xs uppercase text-gray-500">Số điện thoại</div>
                    <div className="truncate font-medium text-gray-900">{displayUser.phone}</div>
                  </div>
                </div>
              </div>
              <div className="rounded-lg bg-gray-50 p-3">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-gray-500" />
                  <div className="min-w-0">
                    <div className="text-xs uppercase text-gray-500">Email</div>
                    <div className="truncate font-medium text-gray-900">{displayUser.email}</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-gray-200 bg-gradient-to-br from-green-800 to-green-950 p-6 text-white shadow-sm">
            <p className="text-sm text-green-200">Gói nông trại</p>
            <h2 className="mt-2 text-2xl font-bold">Cao cấp</h2>
            <p className="mt-3 text-sm leading-6 text-green-100">
              Mở khóa phân tích sâu, cảnh báo nâng cao và tư vấn theo hồ sơ trang trại.
            </p>
            <div className="mt-5 space-y-2 text-sm text-green-100">
              {['Quét bệnh cây trồng không giới hạn', 'Dự báo thời tiết nông vụ', 'Cảnh báo giá theo khu vực'].map(
                (item) => (
                  <div key={item} className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-300" />
                    <span>{item}</span>
                  </div>
                )
              )}
            </div>
            <Link
              to="/pricing-plans"
              className="mt-6 block rounded-lg bg-white px-4 py-3 text-center font-semibold text-green-900 hover:bg-green-50"
            >
              Xem gói dịch vụ
            </Link>
          </section>
        </aside>

        <div className="space-y-6">
          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Trang trại của tôi</h2>
                <p className="mt-1 text-sm text-gray-600">Theo dõi khu canh tác và cây trồng chính.</p>
              </div>
              <button
                type="button"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-700 px-4 py-2 font-medium text-white hover:bg-green-800"
              >
                <Plus className="h-5 w-5" />
                Thêm mảnh vườn
              </button>
            </div>

            {farmAreas.length ? (
              <div className="grid gap-5 md:grid-cols-2">
                {farmAreas.map((farm) => (
                  <article key={farm.id} className="overflow-hidden rounded-lg border border-gray-200 bg-white">
                    <div className="relative h-48">
                      <img src={farm.image} alt={farm.name} className="h-full w-full object-cover" />
                      <span
                        className={`absolute left-3 top-3 rounded-full px-3 py-1 text-xs font-bold text-white ${farm.badgeColor}`}
                      >
                        {farm.status}
                      </span>
                    </div>
                    <div className="p-4">
                      <h3 className="font-bold text-gray-900">{farm.name}</h3>
                      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <div className="text-xs uppercase text-gray-500">Diện tích</div>
                          <div className="font-semibold text-gray-900">
                            {farm.area} {farm.unit}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs uppercase text-gray-500">Loại đất</div>
                          <div className="font-semibold text-gray-900">{farm.soilType}</div>
                        </div>
                      </div>
                      <div className="mt-4 flex items-center gap-2 text-sm text-gray-700">
                        <Sprout className="h-4 w-4 text-green-700" />
                        <span>{farm.crop}</span>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
                <Sprout className="mx-auto h-10 w-10 text-gray-400" />
                <p className="mt-3 font-semibold text-gray-900">Chưa có dữ liệu trang trại từ backend</p>
                <p className="mt-2 text-sm text-gray-600">
                  Khi có API trang trại hoặc mùa vụ theo người dùng, dữ liệu sẽ hiển thị theo tài khoản {displayUser.name}.
                </p>
              </div>
            )}
          </section>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center gap-2">
                <Bell className="h-5 w-5 text-gray-700" />
                <h2 className="font-bold text-gray-900">Cài đặt thông báo</h2>
              </div>
              <div className="space-y-3">
                {[
                  ['weatherAlert', 'Cảnh báo thời tiết cực đoan'],
                  ['priceUpdate', 'Cập nhật giá thị trường'],
                  ['harvestReminder', 'Nhắc lịch bón phân và thu hoạch'],
                ].map(([key, label]) => (
                  <label key={key} className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                    <span className="text-sm text-gray-700">{label}</span>
                    <input
                      type="checkbox"
                      checked={notificationSettings[key]}
                      onChange={() => toggleNotification(key)}
                      className="h-4 w-4 rounded border-gray-300 text-green-700 focus:ring-green-600"
                    />
                  </label>
                ))}
              </div>
            </section>

            <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center gap-2">
                <Globe className="h-5 w-5 text-gray-700" />
                <h2 className="font-bold text-gray-900">Ngôn ngữ & vùng</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Ngôn ngữ hiển thị</label>
                  <select
                    value={language}
                    onChange={(event) => setLanguage(event.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                  >
                    <option value="vi">Tiếng Việt</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Đơn vị diện tích</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      ['hectare', 'Hecta'],
                      ['acre', 'Acre'],
                    ].map(([value, label]) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setUnit(value)}
                        className={`rounded-lg px-4 py-3 font-medium ${
                          unit === value ? 'bg-green-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
