import api, { getApiErrorMessage } from './api';
import { normalizeApiError, unwrapApiResponse } from '../utils/apiResponse';

const unwrap = (response) => unwrapApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    throw normalizeApiError({ ...error, message: getApiErrorMessage(error, fallback) });
  }
};

export const notificationsApi = {
  summary: async () => {
    return request(() => api.get('/api/notifications/summary'), 'Không tải được tổng quan thông báo');
  },

  unreadCount: async () => {
    return request(() => api.get('/api/notifications/unread-count'), 'Không tải được số thông báo chưa đọc');
  },

  list: async ({ type, unreadOnly = false, limit = 50, offset = 0 } = {}) => {
    return request(() => api.get('/api/notifications', {
      params: {
        type: type || undefined,
        unread_only: unreadOnly,
        limit,
        offset,
      },
    }), 'Không tải được danh sách thông báo');
  },

  detail: async (notificationId) => {
    return request(() => api.get(`/api/notifications/${notificationId}`), 'Không tải được chi tiết thông báo');
  },

  deliveries: async (notificationId) => {
    return request(() => api.get(`/api/notifications/${notificationId}/deliveries`), 'Không tải được nhật ký gửi');
  },

  bulk: async ({ action, ids, type, unreadOnly }) => {
    return request(() => api.patch('/api/notifications/bulk', {
      action,
      ids,
      type,
      unread_only: unreadOnly,
    }), 'Không cập nhật được thông báo hàng loạt');
  },

  retryDelivery: async (notificationId) => {
    return request(() => api.post(`/api/notifications/${notificationId}/retry-delivery`), 'Không gửi lại được thông báo');
  },

  markRead: async (notificationId) => {
    return request(() => api.post('/api/notifications/mark-read', {
      notification_id: notificationId,
    }), 'Không đánh dấu đọc được thông báo');
  },

  markAllRead: async () => {
    return request(() => api.post('/api/notifications/mark-all-read'), 'Không đánh dấu đọc tất cả thông báo');
  },

  generateFromAlert: async ({ alertId, alertType, title, message, priority, suggestedAction }) => {
    return request(() => api.post('/api/notifications/generate-from-alert', {
      alert_id: alertId,
      alert_type: alertType,
      title,
      message,
      priority,
      suggested_action: suggestedAction,
    }), 'Không tạo được thông báo từ cảnh báo');
  },

  priority: async ({ minPriority = 'high' } = {}) => {
    return request(() => api.get('/api/notifications/priority', {
      params: { min_priority: minPriority },
    }), 'Không tải được thông báo ưu tiên');
  },

  remove: async (notificationId) => {
    return request(() => api.delete(`/api/notifications/${notificationId}`), 'Không xóa được thông báo');
  },

  streamUrl: () => {
    const token = localStorage.getItem('token') || '';
    return `${api.defaults.baseURL}/api/notifications/stream?token=${encodeURIComponent(token)}`;
  },
};

notificationsApi.getNotifications = notificationsApi.list;
notificationsApi.getUnreadCount = notificationsApi.unreadCount;
notificationsApi.getPriorityNotifications = notificationsApi.priority;
notificationsApi.markNotificationRead = notificationsApi.markRead;
notificationsApi.markAllNotificationsRead = notificationsApi.markAllRead;
notificationsApi.generateNotificationFromAlert = notificationsApi.generateFromAlert;

