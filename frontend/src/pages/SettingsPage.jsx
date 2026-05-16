import {
  Bell,
  Check,
  CheckCircle2,
  Globe2,
  KeyRound,
  Loader2,
  Mail,
  MapPin,
  MessageSquare,
  Monitor,
  Save,
  Send,
  ShieldCheck,
  Smartphone,
  User,
  XCircle,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { InlineLoading, PageError } from '../components/StatusState';
import { useAuth } from '../contexts/AuthContext';
import { getApiErrorMessage } from '../services/api';
import { settingsApi } from '../services/settingsApi';

const TestButton = ({ channel, testState, onTest }) => {
  const active = testState.channel === channel;
  const isLoading = active && testState.status === 'loading';
  const isOk = active && testState.status === 'ok';
  const isErr = active && testState.status === 'error';

  return (
    <div className="mt-2 flex items-center gap-3">
      <button
        type="button"
        onClick={onTest}
        disabled={isLoading}
        className="inline-flex items-center gap-1.5 rounded border border-green-600 px-3 py-1.5 text-xs font-medium text-green-700 hover:bg-green-50 disabled:opacity-50"
      >
        {isLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
        Gửi thử
      </button>
      {isOk && (
        <span className="flex items-center gap-1 text-xs text-green-700">
          <CheckCircle2 className="h-3.5 w-3.5" /> {testState.message}
        </span>
      )}
      {isErr && (
        <span className="flex items-center gap-1 text-xs text-red-600">
          <XCircle className="h-3.5 w-3.5" /> {testState.message}
        </span>
      )}
    </div>
  );
};

const Toggle = ({ checked, onChange, label, description }) => (
  <div className="flex items-center justify-between gap-4 rounded-lg border border-gray-200 bg-white p-4">
    <div>
      <div className="font-medium text-gray-900">{label}</div>
      {description && <div className="mt-1 text-sm text-gray-600">{description}</div>}
    </div>
    <label className="relative inline-flex cursor-pointer items-center">
      <input type="checkbox" checked={checked} onChange={onChange} className="peer sr-only" />
      <span className="h-6 w-11 rounded-full bg-gray-200 transition peer-checked:bg-green-700" />
      <span className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition peer-checked:translate-x-5" />
    </label>
  </div>
);

const SettingsPage = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    fullName: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    location: user?.region || '',
    zaloUserId: '',
    language: 'vi',
    unit: 'hectare',
    theme: 'light',
    priceAlerts: true,
    weatherAlerts: true,
    harvestReminders: true,
    emailChannel: true,
    zaloChannel: false,
    smsChannel: false,
    twoFactor: false,
  });
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testState, setTestState] = useState({ channel: null, status: null, message: '' });

  useEffect(() => {
    let active = true;

    const loadSettings = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await settingsApi.getMe();
        if (!active) return;
        setSettings((current) => ({
          ...current,
          fullName: data.full_name || user?.name || '',
          email: data.email || user?.email || '',
          phone: data.phone_number || user?.phone || '',
          location: data.region || user?.region || '',
          language: data.language || current.language,
          unit: data.unit || current.unit,
          theme: data.theme || current.theme,
          priceAlerts: Boolean(data.price_alerts),
          weatherAlerts: Boolean(data.weather_alerts),
          harvestReminders: Boolean(data.harvest_reminders),
          emailChannel: Boolean(data.email_channel),
          zaloChannel: Boolean(data.zalo_channel),
          smsChannel: Boolean(data.sms_channel),
          twoFactor: Boolean(data.two_factor_enabled),
        }));
      } catch (err) {
        if (!active) return;
        setError(getApiErrorMessage(err, 'Khong the tai cai dat'));
        setSettings((current) => ({
          ...current,
          fullName: user?.name || '',
          email: user?.email || '',
          phone: user?.phone || '',
          location: user?.region || '',
        }));
      } finally {
        if (active) setLoading(false);
      }
    };

    loadSettings();

    return () => {
      active = false;
    };
  }, [user?.name, user?.email, user?.phone, user?.region]);

  const updateSetting = (key, value) => {
    setSettings((current) => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const handleSendTest = async (channel) => {
    const receiverMap = {
      email: settings.email,
      zalo: settings.zaloUserId,
      sms: settings.phone,
    };
    const receiver = receiverMap[channel];
    if (!receiver) {
      setTestState({ channel, status: 'error', message: 'Vui lòng điền thông tin nhận trước.' });
      return;
    }
    setTestState({ channel, status: 'loading', message: '' });
    try {
      const result = await settingsApi.sendTestNotification({ channel, receiver });
      const ok = result?.status === 'sent';
      setTestState({
        channel,
        status: ok ? 'ok' : 'error',
        message: ok ? 'Gửi thành công!' : (result?.error || 'Gửi thất bại.'),
      });
    } catch (err) {
      setTestState({ channel, status: 'error', message: err?.response?.data?.detail || 'Lỗi kết nối.' });
    }
    setTimeout(() => setTestState({ channel: null, status: null, message: '' }), 5000);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setSaved(false);
    try {
      const data = await settingsApi.updateMe({
        full_name: settings.fullName,
        email: settings.email,
        phone_number: settings.phone,
        region: settings.location,
        language: settings.language,
        unit: settings.unit,
        theme: settings.theme,
        price_alerts: settings.priceAlerts,
        weather_alerts: settings.weatherAlerts,
        harvest_reminders: settings.harvestReminders,
        email_channel: settings.emailChannel,
        zalo_channel: settings.zaloChannel,
        sms_channel: settings.smsChannel,
        two_factor_enabled: settings.twoFactor,
      });
      setSettings((current) => ({
        ...current,
        fullName: data.full_name || current.fullName,
        email: data.email || current.email,
        phone: data.phone_number || current.phone,
        location: data.region || current.location,
      }));
      setSaved(true);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Khong the luu cai dat'));
    }
  };

  if (loading) {
    return <InlineLoading text="Dang tai cai dat tu backend..." />;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Thiết lập hệ thống</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Cài đặt</h1>
          <p className="mt-2 text-gray-600">
            Thông tin tài khoản và tuỳ chọn hiển thị được lưu qua API backend.
          </p>
        </div>
        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800"
        >
          <Save className="h-5 w-5" />
          Lưu cài đặt
        </button>
      </div>

      {error && <PageError message={error} />}

      {saved && (
        <div className="flex items-center gap-3 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
          <Check className="h-5 w-5" />
          Đã lưu cấu hình vào backend.
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-green-50 p-2 text-green-700">
                <User className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Hồ sơ tài khoản</h2>
                <p className="text-sm text-gray-600">Thông tin dùng cho liên hệ và cá nhân hóa dashboard.</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Họ và tên</label>
                <input
                  value={settings.fullName}
                  onChange={(event) => updateSetting('fullName', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Số điện thoại</label>
                <input
                  value={settings.phone}
                  onChange={(event) => updateSetting('phone', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  value={settings.email}
                  onChange={(event) => updateSetting('email', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Khu vực</label>
                <input
                  value={settings.location}
                  onChange={(event) => updateSetting('location', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-blue-50 p-2 text-blue-700">
                <Monitor className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Hiển thị và vùng</h2>
                <p className="text-sm text-gray-600">Thiết lập ngôn ngữ, đơn vị đo và giao diện.</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Ngôn ngữ</label>
                <select
                  value={settings.language}
                  onChange={(event) => updateSetting('language', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Đơn vị diện tích</label>
                <select
                  value={settings.unit}
                  onChange={(event) => updateSetting('unit', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                >
                  <option value="hectare">Hecta</option>
                  <option value="acre">Acre</option>
                  <option value="cong">Công</option>
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">Giao diện</label>
                <select
                  value={settings.theme}
                  onChange={(event) => updateSetting('theme', event.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                >
                  <option value="light">Sáng</option>
                  <option value="system">Theo hệ thống</option>
                </select>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-amber-50 p-2 text-amber-700">
                <Bell className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Thông báo</h2>
                <p className="text-sm text-gray-600">Chọn loại cảnh báo và kênh nhận thông tin.</p>
              </div>
            </div>

            <div className="grid gap-4">
              <Toggle
                checked={settings.priceAlerts}
                onChange={() => updateSetting('priceAlerts', !settings.priceAlerts)}
                label="Cảnh báo giá"
                description="Nhận thông báo khi nông sản vượt ngưỡng mục tiêu."
              />
              <Toggle
                checked={settings.weatherAlerts}
                onChange={() => updateSetting('weatherAlerts', !settings.weatherAlerts)}
                label="Cảnh báo thời tiết"
                description="Theo dõi mưa lớn, nắng nóng và điều kiện bất lợi."
              />
              <Toggle
                checked={settings.harvestReminders}
                onChange={() => updateSetting('harvestReminders', !settings.harvestReminders)}
                label="Nhắc lịch mùa vụ"
                description="Nhắc việc bón phân, kiểm tra chất lượng và thu hoạch."
              />
            </div>
          </section>
        </div>

        <aside className="space-y-6">
          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-gray-100 p-2 text-gray-700">
                <Mail className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Kênh nhận thông báo</h2>
                <p className="text-xs text-gray-500">Cấu hình trong backend/.env để kích hoạt gửi thật</p>
              </div>
            </div>
            <div className="space-y-4">
              {/* Email */}
              <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                <Toggle
                  checked={settings.emailChannel}
                  onChange={() => updateSetting('emailChannel', !settings.emailChannel)}
                  label="Email"
                  description={settings.email || 'Chưa có địa chỉ email'}
                />
                {settings.emailChannel && (
                  <TestButton
                    channel="email"
                    testState={testState}
                    onTest={() => handleSendTest('email')}
                  />
                )}
              </div>

              {/* Zalo */}
              <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                <Toggle
                  checked={settings.zaloChannel}
                  onChange={() => updateSetting('zaloChannel', !settings.zaloChannel)}
                  label="Zalo OA"
                  description="Nhận cảnh báo khẩn cấp qua Zalo."
                />
                {settings.zaloChannel && (
                  <div className="mt-3">
                    <label className="mb-1 block text-xs font-medium text-gray-600">
                      Zalo User ID
                    </label>
                    <input
                      value={settings.zaloUserId}
                      onChange={(e) => updateSetting('zaloUserId', e.target.value)}
                      placeholder="Lấy tại: zalo.me/pc → Về tôi → ID"
                      className="w-full rounded border border-gray-300 px-3 py-2 text-sm outline-none focus:border-green-600 focus:ring-1 focus:ring-green-100"
                    />
                    <TestButton
                      channel="zalo"
                      testState={testState}
                      onTest={() => handleSendTest('zalo')}
                    />
                  </div>
                )}
              </div>

              {/* SMS */}
              <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                <Toggle
                  checked={settings.smsChannel}
                  onChange={() => updateSetting('smsChannel', !settings.smsChannel)}
                  label="SMS (ESMS.vn)"
                  description={settings.phone || 'Điền số điện thoại ở Hồ sơ'}
                />
                {settings.smsChannel && (
                  <TestButton
                    channel="sms"
                    testState={testState}
                    onTest={() => handleSendTest('sms')}
                  />
                )}
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-lg bg-green-50 p-2 text-green-700">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-bold text-gray-900">Bảo mật</h2>
            </div>
            <div className="space-y-4">
              <Toggle
                checked={settings.twoFactor}
                onChange={() => updateSetting('twoFactor', !settings.twoFactor)}
                label="Xác thực 2 lớp"
                description="FE đã có điều khiển, cần BE để kích hoạt thật."
              />
              <button
                type="button"
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-3 font-medium text-gray-700 hover:bg-gray-50"
              >
                <KeyRound className="h-5 w-5" />
                Đổi mật khẩu
              </button>
            </div>
          </section>

          <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900">Tóm tắt cấu hình</h2>
            <div className="mt-4 space-y-3 text-sm text-gray-700">
              <div className="flex items-center gap-3">
                <Globe2 className="h-4 w-4 text-green-700" />
                <span>{settings.language === 'vi' ? 'Tiếng Việt' : 'English'}</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="h-4 w-4 text-blue-600" />
                <span>{settings.location}</span>
              </div>
              <div className="flex items-center gap-3">
                <MessageSquare className="h-4 w-4 text-blue-500" />
                <span>{settings.zaloChannel ? 'Zalo bật' : 'Zalo tắt'}</span>
              </div>
              <div className="flex items-center gap-3">
                <Smartphone className="h-4 w-4 text-amber-600" />
                <span>{settings.smsChannel ? 'SMS bật' : 'SMS tắt'}</span>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </form>
  );
};

export default SettingsPage;
