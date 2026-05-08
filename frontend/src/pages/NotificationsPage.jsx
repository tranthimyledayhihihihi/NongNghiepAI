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
import { useEffect, useMemo, useState } from 'react';
import { EmptyState, InlineLoading, PageError } from '../components/StatusState';
import { getApiErrorMessage } from '../services/api';
import { notificationsApi } from '../services/notificationsApi';

const filters = [
  { value: 'all', label: 'Tat ca' },
  { value: 'unread', label: 'Chua doc' },
  { value: 'price', label: 'Gia' },
  { value: 'weather', label: 'Thoi tiet' },
  { value: 'harvest', label: 'Mua vu' },
  { value: 'system', label: 'He thong' },
];

const iconMap = {
  price: { icon: LineChart, color: 'text-green-700 bg-green-50' },
  weather: { icon: CloudSun, color: 'text-amber-700 bg-amber-50' },
  harvest: { icon: Sprout, color: 'text-blue-700 bg-blue-50' },
  system: { icon: ShieldAlert, color: 'text-gray-700 bg-gray-100' },
};

const formatTime = (value) => {
  if (!value) return '';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('vi-VN');
};

const normalizeNotification = (item) => ({
  id: item.notification_id,
  type: item.type || 'system',
  title: item.title,
  description: item.message,
  time: formatTime(item.created_at),
  read: Boolean(item.is_read),
  priority: item.priority || 'medium',
  channel: item.channel || 'app',
});

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await notificationsApi.list({
        type: activeFilter === 'all' || activeFilter === 'unread' ? undefined : activeFilter,
        unreadOnly: activeFilter === 'unread',
        limit: 100,
      });
      const rows = (data.notifications || []).map(normalizeNotification);
      setNotifications(rows);
      setSelectedId((current) => current || rows[0]?.id || null);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Khong the tai thong bao'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [activeFilter]);

  const selectedNotification = notifications.find((notification) => notification.id === selectedId) || notifications[0];
  const unreadCount = useMemo(() => notifications.filter((notification) => !notification.read).length, [notifications]);
  const priceCount = useMemo(() => notifications.filter((notification) => notification.type === 'price').length, [notifications]);

  const markAsRead = async (id) => {
    await notificationsApi.markRead(id);
    setNotifications((current) =>
      current.map((notification) => (notification.id === id ? { ...notification, read: true } : notification))
    );
  };

  const markAllAsRead = async () => {
    await notificationsApi.markAllRead();
    setNotifications((current) => current.map((notification) => ({ ...notification, read: true })));
  };

  const removeNotification = async (id) => {
    await notificationsApi.remove(id);
    setNotifications((current) => current.filter((notification) => notification.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Notifications API</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Thong bao</h1>
          <p className="mt-2 text-gray-600">Inbox thong bao duoc luu trong backend theo tai khoan dang dang nhap.</p>
        </div>
        <button
          type="button"
          onClick={markAllAsRead}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
        >
          <CheckCheck className="h-5 w-5" />
          Danh dau da doc
        </button>
      </div>

      {error && <PageError message={error} onRetry={loadNotifications} />}
      {loading && <InlineLoading text="Dang tai thong bao..." />}

      {!loading && !error && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
              <Bell className="mb-3 h-6 w-6 text-green-700" />
              <div className="text-2xl font-bold text-gray-900">{notifications.length}</div>
              <div className="text-sm text-gray-600">tong thong bao</div>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
              <Filter className="mb-3 h-6 w-6 text-amber-600" />
              <div className="text-2xl font-bold text-gray-900">{unreadCount}</div>
              <div className="text-sm text-gray-600">chua doc</div>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
              <LineChart className="mb-3 h-6 w-6 text-blue-600" />
              <div className="text-2xl font-bold text-gray-900">{priceCount}</div>
              <div className="text-sm text-gray-600">canh bao gia</div>
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

          {notifications.length ? (
            <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
              <div className="space-y-3">
                {notifications.map((notification) => {
                  const iconConfig = iconMap[notification.type] || iconMap.system;
                  const Icon = iconConfig.icon;
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
                          if (!notification.read) markAsRead(notification.id);
                        }}
                        className="flex w-full items-start gap-4 text-left"
                      >
                        <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg ${iconConfig.color}`}>
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
              </div>

              <aside className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                {selectedNotification ? (
                  <>
                    <div className="mb-5 flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Chi tiet</p>
                        <h2 className="mt-2 text-xl font-bold text-gray-900">{selectedNotification.title}</h2>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeNotification(selectedNotification.id)}
                        className="rounded-lg p-2 text-gray-500 hover:bg-red-50 hover:text-red-600"
                        aria-label="Xoa thong bao"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                    <p className="text-sm leading-7 text-gray-600">{selectedNotification.description}</p>
                    <div className="mt-5 rounded-lg bg-gray-50 p-4 text-sm text-gray-700">
                      <div className="font-semibold text-gray-900">Kenh</div>
                      <p className="mt-2">{selectedNotification.channel}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => markAsRead(selectedNotification.id)}
                      className="mt-5 w-full rounded-lg bg-green-700 px-4 py-3 font-semibold text-white hover:bg-green-800"
                    >
                      Danh dau da doc
                    </button>
                  </>
                ) : (
                  <div className="py-10 text-center text-sm text-gray-600">Chon mot thong bao de xem chi tiet.</div>
                )}
              </aside>
            </div>
          ) : (
            <EmptyState
              title="Chua co thong bao"
              description="Cac canh bao gia, thoi tiet va nhac mua vu se xuat hien tai day khi backend tao inbox item."
            />
          )}
        </>
      )}
    </div>
  );
};

export default NotificationsPage;
