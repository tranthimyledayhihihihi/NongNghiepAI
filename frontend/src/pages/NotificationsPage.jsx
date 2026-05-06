import {
  Bell,
  CheckCheck,
  ChevronRight,
  CloudSun,
  Filter,
  LineChart,
  ShieldAlert,
  Sprout,
  Trash2,
} from 'lucide-react';
import { useMemo, useState } from 'react';

const initialNotifications = [
  {
    id: 1,
    type: 'price',
    title: 'Giá cà phê Robusta vượt ngưỡng mục tiêu',
    description: 'Đắk Lắk ghi nhận 43.100 đ/kg, cao hơn ngưỡng cảnh báo 42.500 đ/kg.',
    time: '10 phút trước',
    read: false,
    priority: 'Cao',
    icon: LineChart,
    color: 'text-green-700 bg-green-50',
  },
  {
    id: 2,
    type: 'weather',
    title: 'Cảnh báo mưa lớn tại Cần Thơ',
    description: 'Dự báo mưa lớn trong 24 giờ tới, nên kiểm tra thoát nước khu lúa mới gieo.',
    time: '45 phút trước',
    read: false,
    priority: 'Cao',
    icon: CloudSun,
    color: 'text-amber-700 bg-amber-50',
  },
  {
    id: 3,
    type: 'harvest',
    title: 'Lịch thu hoạch lúa OM 5451 sắp đến hạn',
    description: 'Khu ruộng A dự kiến thu hoạch sau 5 ngày. Kiểm tra độ ẩm hạt trước khi cắt.',
    time: '2 giờ trước',
    read: true,
    priority: 'Trung bình',
    icon: Sprout,
    color: 'text-blue-700 bg-blue-50',
  },
  {
    id: 4,
    type: 'system',
    title: 'Kiểm định chất lượng đã hoàn tất',
    description: 'Lô cà chua CT-0426 đạt loại 1, độ tin cậy phân tích 92%.',
    time: 'Hôm qua',
    read: true,
    priority: 'Thấp',
    icon: ShieldAlert,
    color: 'text-gray-700 bg-gray-100',
  },
];

const filters = [
  { value: 'all', label: 'Tất cả' },
  { value: 'unread', label: 'Chưa đọc' },
  { value: 'price', label: 'Giá' },
  { value: 'weather', label: 'Thời tiết' },
  { value: 'harvest', label: 'Mùa vụ' },
  { value: 'system', label: 'Hệ thống' },
];

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedId, setSelectedId] = useState(initialNotifications[0]?.id);

  const filteredNotifications = useMemo(() => {
    if (activeFilter === 'all') return notifications;
    if (activeFilter === 'unread') return notifications.filter((item) => !item.read);
    return notifications.filter((item) => item.type === activeFilter);
  }, [activeFilter, notifications]);

  const selectedNotification =
    notifications.find((notification) => notification.id === selectedId) || filteredNotifications[0];

  const unreadCount = notifications.filter((notification) => !notification.read).length;

  const markAsRead = (id) => {
    setNotifications((current) =>
      current.map((notification) =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications((current) => current.map((notification) => ({ ...notification, read: true })));
  };

  const removeNotification = (id) => {
    setNotifications((current) => current.filter((notification) => notification.id !== id));
    if (selectedId === id) {
      setSelectedId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Trung tâm thông báo</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Thông báo</h1>
          <p className="mt-2 text-gray-600">
            Xem cảnh báo giá, thời tiết, mùa vụ và thông báo hệ thống. Dữ liệu hiện là state local phía FE.
          </p>
        </div>
        <button
          type="button"
          onClick={markAllAsRead}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
        >
          <CheckCheck className="h-5 w-5" />
          Đánh dấu đã đọc
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <Bell className="mb-3 h-6 w-6 text-green-700" />
          <div className="text-2xl font-bold text-gray-900">{notifications.length}</div>
          <div className="text-sm text-gray-600">tổng thông báo</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <Filter className="mb-3 h-6 w-6 text-amber-600" />
          <div className="text-2xl font-bold text-gray-900">{unreadCount}</div>
          <div className="text-sm text-gray-600">chưa đọc</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <LineChart className="mb-3 h-6 w-6 text-blue-600" />
          <div className="text-2xl font-bold text-gray-900">
            {notifications.filter((item) => item.type === 'price').length}
          </div>
          <div className="text-sm text-gray-600">cảnh báo giá</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((filter) => (
          <button
            key={filter.value}
            type="button"
            onClick={() => setActiveFilter(filter.value)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeFilter === filter.value
                ? 'bg-green-700 text-white'
                : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="space-y-3">
          {filteredNotifications.map((notification) => {
            const Icon = notification.icon;
            return (
              <article
                key={notification.id}
                className={`rounded-lg border bg-white p-4 shadow-sm transition ${
                  notification.read ? 'border-gray-200' : 'border-green-300'
                }`}
              >
                <button
                  type="button"
                  onClick={() => {
                    setSelectedId(notification.id);
                    markAsRead(notification.id);
                  }}
                  className="flex w-full items-start gap-4 text-left"
                >
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${notification.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="font-bold text-gray-900">{notification.title}</h2>
                      {!notification.read && <span className="h-2 w-2 rounded-full bg-green-600" />}
                    </div>
                    <p className="mt-1 text-sm leading-6 text-gray-600">{notification.description}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                      <span>{notification.time}</span>
                      <span className="rounded-full bg-gray-100 px-2.5 py-1 font-medium text-gray-700">
                        {notification.priority}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="mt-1 h-5 w-5 shrink-0 text-gray-400" />
                </button>
              </article>
            );
          })}

          {filteredNotifications.length === 0 && (
            <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center">
              <p className="font-medium text-gray-900">Không có thông báo trong bộ lọc này.</p>
              <p className="mt-2 text-sm text-gray-600">Thử chọn bộ lọc khác hoặc chờ dữ liệu từ BE.</p>
            </div>
          )}
        </div>

        <aside className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          {selectedNotification ? (
            <>
              <div className="mb-5 flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Chi tiết</p>
                  <h2 className="mt-2 text-xl font-bold text-gray-900">{selectedNotification.title}</h2>
                </div>
                <button
                  type="button"
                  onClick={() => removeNotification(selectedNotification.id)}
                  className="rounded-lg p-2 text-gray-500 hover:bg-red-50 hover:text-red-600"
                  aria-label="Xóa thông báo"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
              <p className="text-sm leading-7 text-gray-600">{selectedNotification.description}</p>
              <div className="mt-5 rounded-lg bg-gray-50 p-4 text-sm text-gray-700">
                <div className="font-semibold text-gray-900">Hành động gợi ý</div>
                <p className="mt-2">
                  Kiểm tra module liên quan trong dashboard và cập nhật cấu hình cảnh báo nếu ngưỡng hiện tại
                  không còn phù hợp.
                </p>
              </div>
              <button
                type="button"
                onClick={() => markAsRead(selectedNotification.id)}
                className="mt-5 w-full rounded-lg bg-green-700 px-4 py-3 font-semibold text-white hover:bg-green-800"
              >
                Đánh dấu đã đọc
              </button>
            </>
          ) : (
            <div className="py-10 text-center text-sm text-gray-600">Chọn một thông báo để xem chi tiết.</div>
          )}
        </aside>
      </div>
    </div>
  );
};

export default NotificationsPage;
