import { Bell } from 'lucide-react';
import { useState } from 'react';

const AlertSubscribe = () => {
  const [formData, setFormData] = useState({
    crop: 'Cà chua',
    region: 'Hà Nội',
    priceChange: 10,
    notifyMethod: 'email',
    contact: '',
  });

  const crops = ['Cà chua', 'Dưa chuột', 'Rau muống', 'Cải xanh', 'Ớt'];
  const regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng'];

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement API call in Phase 2
    alert('Tính năng đăng ký cảnh báo sẽ có trong Phase 2');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-6">
        <Bell className="h-6 w-6 text-primary-600 mr-2" />
        <h2 className="text-lg font-semibold">Đăng ký cảnh báo giá</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Loại nông sản
          </label>
          <select
            value={formData.crop}
            onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {crops.map((crop) => (
              <option key={crop} value={crop}>
                {crop}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Khu vực
          </label>
          <select
            value={formData.region}
            onChange={(e) =>
              setFormData({ ...formData, region: e.target.value })
            }
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cảnh báo khi giá thay đổi
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={formData.priceChange}
              onChange={(e) =>
                setFormData({ ...formData, priceChange: e.target.value })
              }
              className="w-24 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <span className="text-gray-600">%</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Phương thức nhận thông báo
          </label>
          <select
            value={formData.notifyMethod}
            onChange={(e) =>
              setFormData({ ...formData, notifyMethod: e.target.value })
            }
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="email">Email</option>
            <option value="zalo">Zalo (Coming soon)</option>
            <option value="sms">SMS (Coming soon)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {formData.notifyMethod === 'email' ? 'Email' : 'Số điện thoại'}
          </label>
          <input
            type={formData.notifyMethod === 'email' ? 'email' : 'tel'}
            value={formData.contact}
            onChange={(e) =>
              setFormData({ ...formData, contact: e.target.value })
            }
            placeholder={
              formData.notifyMethod === 'email'
                ? 'your@email.com'
                : '0123456789'
            }
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>

        <button
          type="submit"
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition-colors"
        >
          Đăng ký cảnh báo
        </button>

        <p className="text-xs text-gray-500 text-center">
          Tính năng cảnh báo sẽ được hoàn thiện trong Phase 2
        </p>
      </form>
    </div>
  );
};

export default AlertSubscribe;
