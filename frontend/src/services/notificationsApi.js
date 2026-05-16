import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const notificationsApi = {
  summary: async () => {
    const response = await api.get('/api/notifications/summary');
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
    const response = await api.patch(`/api/notifications/${notificationId}/read`);
    return unwrap(response);
  },

  markAllRead: async () => {
    const response = await api.post('/api/notifications/mark-all-read');
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
