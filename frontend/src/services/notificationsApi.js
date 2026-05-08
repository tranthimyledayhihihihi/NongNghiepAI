import api from './api';

const unwrap = (response) => response.data?.data ?? response.data;

export const notificationsApi = {
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
};
