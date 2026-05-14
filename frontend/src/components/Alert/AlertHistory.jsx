import { Trash2, TrendingDown, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { alertApi } from '../../services/alertApi';
import { getApiErrorMessage } from '../../services/api';
import { EmptyState, InlineLoading, PageError } from '../StatusState';

const AlertHistory = ({ refreshKey = 0 }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadAlerts = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await alertApi.getAlerts();
      setAlerts(data.alerts || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tải danh sách cảnh báo'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [refreshKey]);

  const handleDeactivate = async (alertId) => {
    try {
      await alertApi.deactivate(alertId);
      await loadAlerts();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tắt cảnh báo'));
    }
  };

  return (
    <section className="rounded-lg border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-200 p-5">
        <h2 className="text-lg font-semibold text-gray-900">Lịch sử cảnh báo</h2>
        <p className="mt-1 text-sm text-gray-600">Danh sách cảnh báo giá đang được lưu trên backend.</p>
      </div>

      <div className="p-5">
        {error && <PageError message={error} onRetry={loadAlerts} />}
        {loading && <InlineLoading text="Đang tải cảnh báo..." />}

        {!loading && !error && alerts.length === 0 && (
          <EmptyState
            title="Chưa có cảnh báo"
            description="Tạo cảnh báo mới để theo dõi biến động giá theo nông sản và khu vực."
          />
        )}

        {!loading && !error && alerts.length > 0 && (
          <div className="divide-y divide-gray-200 overflow-hidden rounded-lg border border-gray-200">
            {alerts.map((alert) => (
              <div key={alert.alert_id} className="bg-white p-4 hover:bg-gray-50">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
                  <div className="flex items-start gap-3 sm:flex-1">
                    {alert.condition === 'above' ? (
                      <TrendingUp className="mt-1 h-6 w-6 shrink-0 text-green-600" />
                    ) : (
                      <TrendingDown className="mt-1 h-6 w-6 shrink-0 text-red-600" />
                    )}
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900">
                        {alert.crop_name} - {alert.region}
                      </p>
                      <p className="mt-1 text-sm text-gray-600">
                        {alert.condition === 'above' ? 'Giá trên' : 'Giá dưới'}{' '}
                        {Number(alert.target_price).toLocaleString('vi-VN')} đ/kg qua{' '}
                        {alert.notification_channel}
                      </p>
                      <p className="mt-1 text-xs text-gray-500">
                        {alert.created_at ? new Date(alert.created_at).toLocaleString('vi-VN') : alert.message}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-3 sm:justify-end">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${
                        alert.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {alert.is_active ? 'Đang bật' : 'Đã tắt'}
                    </span>
                    {alert.is_active && (
                      <button
                        type="button"
                        onClick={() => handleDeactivate(alert.alert_id)}
                        className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600"
                        title="Tắt cảnh báo"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default AlertHistory;
