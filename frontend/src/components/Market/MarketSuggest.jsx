import { TrendingUp } from 'lucide-react';
import { useState } from 'react';

const MarketSuggest = () => {
  const [formData, setFormData] = useState({
    quantity: '',
    price: '',
  });

  const [result, setResult] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();

    const quantity = parseFloat(formData.quantity);
    const price = parseFloat(formData.price);

    // Mock calculation
    const wholesale = {
      channel: 'Chợ đầu mối',
      revenue: quantity * price * 0.92, // -8% commission
      profit: quantity * price * 0.92 - quantity * price * 0.5,
    };

    const retail = {
      channel: 'Chợ bán lẻ',
      revenue: quantity * price * 1.1, // +10% price
      profit: quantity * price * 1.1 - quantity * price * 0.5,
    };

    const exportChannel = {
      channel: 'Xuất khẩu',
      revenue: quantity * price * 1.2 * 0.85, // +20% price, -15% commission
      profit: quantity * price * 1.2 * 0.85 - quantity * price * 0.5,
    };

    setResult({
      channels: [wholesale, retail, exportChannel].sort(
        (a, b) => b.profit - a.profit
      ),
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <TrendingUp className="h-5 w-5 text-primary-600 mr-2" />
        Công cụ so sánh lợi nhuận
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số lượng (kg)
            </label>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) =>
                setFormData({ ...formData, quantity: e.target.value })
              }
              placeholder="1000"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Giá bán (đ/kg)
            </label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) =>
                setFormData({ ...formData, price: e.target.value })
              }
              placeholder="20000"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700"
        >
          So sánh
        </button>
      </form>

      {result && (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">
            Kết quả so sánh:
          </h3>
          {result.channels.map((channel, index) => (
            <div
              key={channel.channel}
              className={`p-4 rounded-lg border-2 ${index === 0
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200'
                }`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-medium text-gray-900">
                    {channel.channel}
                    {index === 0 && (
                      <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">
                        Tốt nhất
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    Doanh thu: {channel.revenue.toLocaleString()} đ
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">
                    {channel.profit.toLocaleString()} đ
                  </p>
                  <p className="text-xs text-gray-500">Lợi nhuận</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MarketSuggest;
