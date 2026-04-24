import { Bell, TrendingDown, TrendingUp } from 'lucide-react';

const AlertHistory = () => {
  // Mock data - sẽ được thay bằng API call trong Phase 2
  const alerts = [
    {
      id: 1,
      crop: 'Cà chua',
      region: 'Hà Nội',
      type: 'price_increase',
      message: 'Giá tăng 15% so với tuần trước',
      date: '2024-01-15',
      read: false,
    },
    {
      id: 2,
      crop: 'Dưa chuột',
      region: 'TP.HCM',
      type: 'price_decrease',
      message: 'Giá giảm 10% so với tuần trước',
      date: '2024-01-14',
      read: true,
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold">Lịch sử cảnh báo</h2>
      </div>

      <div className="divide-y">
        {alerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Bell className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p>Chưa có cảnh báo nào</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 hover:bg-gray-50 ${!alert.read ? 'bg-blue-50' : ''
                }`}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  {alert.type === 'price_increase' ? (
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  ) : (
                    <TrendingDown className="h-6 w-6 text-red-600" />
                  )}
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {alert.crop} - {alert.region}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {alert.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{alert.date}</p>
                </div>
                {!alert.read && (
                  <div className="ml-3">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Mới
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertHistory;
