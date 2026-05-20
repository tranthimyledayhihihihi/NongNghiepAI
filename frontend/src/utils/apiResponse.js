export const API_FAILURE_MESSAGE = 'Không thể tải dữ liệu từ nguồn chính thức.';

export function isApiSuccess(response) {
  if (!response) {
    return false;
  }

  // Axios response object: has numeric .status and .data, but no .success at top level.
  // Delegate to the actual JSON body.
  if (
    typeof response === 'object' &&
    typeof response.status === 'number' &&
    'data' in response &&
    !('success' in response)
  ) {
    return isApiSuccess(response.data);
  }

  if (typeof response === 'object' && 'success' in response) {
    return Boolean(response.success);
  }

  if (typeof response === 'object' && 'status' in response) {
    return String(response.status).toLowerCase() === 'success';
  }

  return true;
}

export function getApiErrorMessage(error, fallbackMessage = API_FAILURE_MESSAGE) {
  if (!error) {
    return fallbackMessage;
  }

  if (typeof error === 'string') {
    return error.trim() || fallbackMessage;
  }

  if (typeof error === 'object') {
    const candidates = [
      error.detail,
      error.message,
      error.error,
      error.response?.data?.detail,
      error.response?.data?.message,
      error.response?.data?.error,
      error.data?.detail,
      error.data?.message,
      error.data?.error,
    ];

    for (const candidate of candidates) {
      if (typeof candidate === 'string' && candidate.trim()) {
        return candidate.trim();
      }
    }
  }

  return fallbackMessage;
}

export function normalizeApiResponse(response, fallbackData = null) {
  if (response == null) {
    return {
      success: false,
      data: fallbackData,
      message: API_FAILURE_MESSAGE,
    };
  }

  if (isApiSuccess(response)) {
    if (typeof response === 'object' && response !== null && 'data' in response) {
      return {
        success: true,
        data: response.data,
        message: response.message || response.detail || '',
      };
    }

    return {
      success: true,
      data: response,
      message: '',
    };
  }

  return {
    success: false,
    data: fallbackData,
    message: getApiErrorMessage(response, API_FAILURE_MESSAGE),
  };
}

export function unwrapApiResponse(response, fallbackData = null) {
  const normalized = normalizeApiResponse(response, fallbackData);
  return normalized.success ? normalized.data : fallbackData;
}

export function getResponseData(response, fallbackData = null) {
  return unwrapApiResponse(response, fallbackData);
}

export function toApiErrorResponse(error, fallbackData = null, fallbackMessage = API_FAILURE_MESSAGE) {
  return {
    success: false,
    data: fallbackData,
    message: getApiErrorMessage(error, fallbackMessage),
  };
}

export function normalizeApiError(error, fallbackMessage = API_FAILURE_MESSAGE) {
  const message = getApiErrorMessage(error, fallbackMessage);
  return {
    success: false,
    data: null,
    source: error?.response?.data?.source || 'realtime_api',
    sourceName: error?.response?.data?.source_name || error?.response?.data?.source || 'realtime_api',
    source_name: error?.response?.data?.source_name || error?.response?.data?.source || 'realtime_api',
    isRealtime: false,
    is_realtime: false,
    isCache: false,
    is_cache: false,
    isMock: false,
    is_mock: false,
    warning: null,
    error: {
      code: error?.response?.data?.error?.code || error?.code || 'API_ERROR',
      message,
    },
    message,
  };
}

export function createApiSuccessResponse(data, message = '') {
  return {
    success: true,
    data,
    message,
  };
}

export function dedupeMessages(messages) {
  if (!Array.isArray(messages)) return [];
  return [...new Set(messages.filter((m) => typeof m === 'string' && m.trim()))];
}

export default {
  API_FAILURE_MESSAGE,
  isApiSuccess,
  getApiErrorMessage,
  normalizeApiResponse,
  unwrapApiResponse,
  getResponseData,
  toApiErrorResponse,
  normalizeApiError,
  createApiSuccessResponse,
  dedupeMessages,
};
