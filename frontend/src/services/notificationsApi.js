import api, { getApiErrorMessage } from './api';
import { normalizeApiResponse } from '../utils/apiResponse';

const unwrap = (response) => normalizeApiResponse(response);
const request = async (factory, fallback) => {
  try {
    return unwrap(await factory());
  } catch (error) {
    error.message = getApiErrorMessage(error, fallback);
    throw error;
  }
};

export const notificationsApi = {
  summary: async () => {
    return request(() => api.get('/api/notifications/summary'), 'Khong tai duoc tong quan thong bao');
  },

  unreadCount: async () => {
    return request(() => api.get('/api/notifications/unread-count'), 'Khong tai duoc so thong bao chua doc');
  },

  list: async ({ type, unreadOnly = false, limit = 50, offset = 0 } = {}) => {
    return request(() => api.get('/api/notifications', {
      params: {
        type: type || undefined,
        unread_only: unreadOnly,
        limit,
        offset,
      },
    }), 'Khong tai duoc danh sach thong bao');
  },

  detail: async (notificationId) => {
    return request(() => api.get(`/api/notifications/${notificationId}`), 'Khong tai duoc chi tiet thong bao');
  },

  deliveries: async (notificationId) => {
    return request(() => api.get(`/api/notifications/${notificationId}/deliveries`), 'Khong tai duoc delivery log');
  },

  bulk: async ({ action, ids, type, unreadOnly }) => {
    return request(() => api.patch('/api/notifications/bulk', {
      action,
      ids,
      type,
      unread_only: unreadOnly,
    }), 'Khong cap nhat duoc thong bao hang loat');
  },

  retryDelivery: async (notificationId) => {
    return request(() => api.post(`/api/notifications/${notificationId}/retry-delivery`), 'Khong gui lai duoc delivery');
  },

  markRead: async (notificationId) => {
    return request(() => api.post('/api/notifications/mark-read', {
      notification_id: notificationId,
    }), 'Khong danh dau doc duoc thong bao');
  },

  markAllRead: async () => {
    return request(() => api.post('/api/notifications/mark-all-read'), 'Khong danh dau doc tat ca thong bao');
  },

  generateFromAlert: async ({ alertId, alertType, title, message, priority, suggestedAction }) => {
    return request(() => api.post('/api/notifications/generate-from-alert', {
      alert_id: alertId,
      alert_type: alertType,
      title,
      message,
      priority,
      suggested_action: suggestedAction,
    }), 'Khong tao duoc thong bao tu alert');
  },

  priority: async ({ minPriority = 'high' } = {}) => {
    return request(() => api.get('/api/notifications/priority', {
      params: { min_priority: minPriority },
    }), 'Khong tai duoc thong bao uu tien');
  },

  remove: async (notificationId) => {
    return request(() => api.delete(`/api/notifications/${notificationId}`), 'Khong xoa duoc thong bao');
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
