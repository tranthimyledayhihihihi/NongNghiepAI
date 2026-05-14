import { Globe, ShoppingCart, TrendingUp } from 'lucide-react';

const ChannelCompare = () => {
  const channels = [
    {
      id: 'wholesale',
      name: 'Chợ đầu mối',
      icon: ShoppingCart,
      commission: '5-10%',
      pros: ['Tiêu thụ nhanh', 'Số lượng lớn'],
      cons: ['Giá thấp hơn', 'Phí hoa hồng'],
      color: 'blue',
    },
    {
      id: 'retail',
      name: 'Chợ bán lẻ',
      icon: TrendingUp,
      commission: '0%',
      pros: ['Giá cao hơn', 'Không phí'],
      cons: ['Tiêu thụ chậm', 'Cần thời gian'],
      color: 'green',
    },
    {
      id: 'export',
      name: 'Xuất khẩu',
      icon: Globe,
      commission: '15-20%',
      pros: ['Giá tốt nhất', 'Ổn định'],
      cons: ['Yêu cầu cao', 'Thủ tục phức tạp'],
      color: 'purple',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {channels.map((channel) => {
        const Icon = channel.icon;
        return (
          <div
            key={channel.id}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center mb-4">
              <div className={`p-3 bg-${channel.color}-100 rounded-lg`}>
                <Icon className={`h-6 w-6 text-${channel.color}-600`} />
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-semibold text-gray-900">
                  {channel.name}
                </h3>
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
  );
};

export default ChannelCompare;
