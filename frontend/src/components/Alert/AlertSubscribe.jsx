import { Bell } from 'lucide-react';
import { useState } from 'react';
import { alertApi } from '../../services/alertApi';
import { getApiErrorMessage } from '../../services/api';
import { PageError } from '../StatusState';

const crops = ['ca chua', 'dua chuot', 'rau muong', 'cai xanh', 'ot', 'lua'];
const regions = ['Ha Noi', 'TP.HCM', 'Da Nang', 'Can Tho', 'Hai Phong'];

const AlertSubscribe = ({ onCreated }) => {
  const [formData, setFormData] = useState({
    crop: 'ca chua',
    region: 'Ha Noi',
    targetPrice: 25000,
    condition: 'above',
    notifyMethod: 'email',
    contact: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const updateField = (key, value) => {
    setFormData((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const alert = await alertApi.createPriceAlert({
        cropName: formData.crop,
        region: formData.region,
        targetPrice: formData.targetPrice,
        condition: formData.condition,
        notificationChannel: formData.notifyMethod,
        receiver: formData.contact,
      });
      setMessage(alert.message || 'Đã tạo cảnh báo giá');
      onCreated?.(alert);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tạo cảnh báo'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex items-center gap-3">
        <div className="rounded-lg bg-green-50 p-2 text-green-700">
          <Bell className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Đăng ký cảnh báo giá</h2>
          <p className="text-sm text-gray-600">Tạo ngưỡng cảnh báo qua email, Zalo hoặc SMS.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Loại nông sản</label>
            <select
              value={formData.crop}
              onChange={(event) => updateField('crop', event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              {crops.map((crop) => (
                <option key={crop} value={crop}>
                  {crop}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Khu vực</label>
            <select
              value={formData.region}
              onChange={(event) => updateField('region', event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              {regions.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Điều kiện</label>
            <select
              value={formData.condition}
              onChange={(event) => updateField('condition', event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            >
              <option value="above">Giá trên</option>
              <option value="below">Giá dưới</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Giá mục tiêu</label>
            <input
              type="number"
              min="1"
              value={formData.targetPrice}
              onChange={(event) => updateField('targetPrice', event.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
              required
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Phương thức nhận thông báo</label>
          <select
            value={formData.notifyMethod}
            onChange={(event) => updateField('notifyMethod', event.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
          >
            <option value="email">Email</option>
            <option value="zalo">Zalo</option>
            <option value="sms">SMS</option>
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            {formData.notifyMethod === 'email' ? 'Email' : 'Số điện thoại/Zalo ID'}
          </label>
          <input
            type={formData.notifyMethod === 'email' ? 'email' : 'text'}
            value={formData.contact}
            onChange={(event) => updateField('contact', event.target.value)}
            placeholder={formData.notifyMethod === 'email' ? 'your@email.com' : '0123456789'}
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            required
          />
        </div>

        {message && <p className="rounded-lg bg-green-50 p-3 text-sm text-green-700">{message}</p>}
        {error && <PageError message={error} />}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-green-700 px-4 py-3 font-semibold text-white transition-colors hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Đang tạo...' : 'Đăng ký cảnh báo'}
        </button>
      </form>
    </section>
  );
};

export default AlertSubscribe;
