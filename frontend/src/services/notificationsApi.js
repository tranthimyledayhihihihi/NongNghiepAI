import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const notificationsApi = {
  summary: async () => {
    const response = await api.get('/api/notifications/summary');
    return unwrap(response);
  },

  unreadCount: async () => {
    const response = await api.get('/api/notifications/unread-count');
    return unwrap(response);
  },

  list: async ({ type, unreadOnly = false, limit = 50, offset = 0 } = {}) => {
    const response = await api.get('/api/notifications', {
      params: {
        type: type || undefined,
        unread_only: unreadOnly,
        limit,
        offset,
      },
    });
    return unwrap(response);
  },

  detail: async (notificationId) => {
    const response = await api.get(`/api/notifications/${notificationId}`);
    return unwrap(response);
  },

  deliveries: async (notificationId) => {
    const response = await api.get(`/api/notifications/${notificationId}/deliveries`);
    return unwrap(response);
  },

  bulk: async ({ action, ids, type, unreadOnly }) => {
    const response = await api.patch('/api/notifications/bulk', {
      action,
      ids,
      type,
      unread_only: unreadOnly,
    });
    return unwrap(response);
  },

  retryDelivery: async (notificationId) => {
    const response = await api.post(`/api/notifications/${notificationId}/retry-delivery`);
    return unwrap(response);
  },

  markRead: async (notificationId) => {
    const response = await api.post('/api/notifications/mark-read', {
      notification_id: notificationId,
    });
    return unwrap(response);
  },

  markAllRead: async () => {
    const response = await api.post('/api/notifications/mark-all-read');
    return unwrap(response);
  },

  generateFromAlert: async ({ alertId, alertType, title, message, priority, suggestedAction }) => {
    const response = await api.post('/api/notifications/generate-from-alert', {
      alert_id: alertId,
      alert_type: alertType,
      title,
      message,
      priority,
      suggested_action: suggestedAction,
    });
    return unwrap(response);
  },

  priority: async ({ minPriority = 'high' } = {}) => {
    const response = await api.get('/api/notifications/priority', {
      params: { min_priority: minPriority },
    });
    return unwrap(response);
  },

  remove: async (notificationId) => {
    const response = await api.delete(`/api/notifications/${notificationId}`);
    return unwrap(response);
  },

  streamUrl: () => {
    const token = localStorage.getItem('token') || '';
    return `${api.defaults.baseURL}/api/notifications/stream?token=${encodeURIComponent(token)}`;
  },
};
