import { Globe, ShoppingCart, TrendingUp } from 'lucide-react';

const MarketPage = () => {
  const channels = [
    {
      id: 'wholesale',
      name: 'Chợ đầu mối',
      icon: ShoppingCart,
      description: 'Bán buôn số lượng lớn',
      commission: '5-10%',
      pros: ['Tiêu thụ nhanh', 'Số lượng lớn'],
      cons: ['Giá thấp hơn', 'Phí hoa hồng'],
    },
    {
      id: 'retail',
      name: 'Chợ bán lẻ',
      icon: TrendingUp,
      description: 'Bán lẻ trực tiếp',
      commission: '0%',
      pros: ['Giá cao hơn', 'Không phí'],
      cons: ['Tiêu thụ chậm', 'Cần thời gian'],
    },
    {
      id: 'export',
      name: 'Xuất khẩu',
      icon: Globe,
      description: 'Xuất khẩu ra nước ngoài',
      commission: '15-20%',
      pros: ['Giá tốt nhất', 'Ổn định'],
      cons: ['Yêu cầu cao', 'Thủ tục phức tạp'],
    },
  ];

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Tư vấn kênh bán hàng
        </h1>
        <p className="mt-2 text-gray-600">
          So sánh và chọn kênh bán hàng phù hợp nhất
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {channels.map((channel) => {
          const Icon = channel.icon;
          return (
            <div
              key={channel.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {channel.name}
                  </h3>
                  <p className="text-sm text-gray-600">{channel.description}</p>
                </div>
              </div>

              <div className="mb-4">
                <span className="text-sm font-medium text-gray-700">
                  Phí hoa hồng:
                </span>
                <span className="ml-2 text-sm text-gray-900">
                  {channel.commission}
                </span>
              </div>

              <div className="mb-4">
                <p className="text-sm font-medium text-green-700 mb-2">
                  Ưu điểm:
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  {channel.pros.map((pro, idx) => (
                    <li key={idx}>✓ {pro}</li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm font-medium text-red-700 mb-2">
                  Nhược điểm:
                </p>
                <ul className="text-sm text-gray-600 space-y-1">
                  {channel.cons.map((con, idx) => (
                    <li key={idx}>✗ {con}</li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">
          Công cụ so sánh lợi nhuận
        </h2>
        <p className="text-gray-600 mb-4">
          Nhập thông tin để so sánh lợi nhuận từng kênh bán
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số lượng (kg)
            </label>
            <input
              type="number"
              placeholder="1000"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Giá bán (đ/kg)
            </label>
            <input
              type="number"
              placeholder="20000"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-end">
            <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700">
              So sánh
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Lưu ý:</strong> Tính năng tư vấn kênh bán hàng chi tiết và so sánh lợi nhuận
          sẽ được hoàn thiện trong Phase 2 với AI recommendations.
        </p>
      </div>
    </div>
  );
};

export default MarketPage;
