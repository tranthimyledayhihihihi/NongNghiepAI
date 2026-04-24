import { create } from 'zustand';

const usePriceStore = create((set) => ({
  currentPrices: {},
  forecasts: {},
  histories: {},

  setCurrentPrice: (key, data) =>
    set((state) => ({
      currentPrices: {
        ...state.currentPrices,
        [key]: data,
      },
    })),

  setForecast: (key, data) =>
    set((state) => ({
      forecasts: {
        ...state.forecasts,
        [key]: data,
      },
    })),

  setHistory: (key, data) =>
    set((state) => ({
      histories: {
        ...state.histories,
        [key]: data,
      },
    })),

  clearCache: () =>
    set({
      currentPrices: {},
      forecasts: {},
      histories: {},
    }),
}));

export default usePriceStore;
