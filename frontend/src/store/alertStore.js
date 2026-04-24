import { create } from 'zustand';

const useAlertStore = create((set) => ({
  alerts: [],
  subscriptions: [],

  setAlerts: (alerts) => set({ alerts }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
    })),

  markAsRead: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === alertId ? { ...alert, read: true } : alert
      ),
    })),

  setSubscriptions: (subscriptions) => set({ subscriptions }),

  addSubscription: (subscription) =>
    set((state) => ({
      subscriptions: [...state.subscriptions, subscription],
    })),

  removeSubscription: (subscriptionId) =>
    set((state) => ({
      subscriptions: state.subscriptions.filter(
        (sub) => sub.id !== subscriptionId
      ),
    })),
}));

export default useAlertStore;
