import { AlertCircle, Inbox, Loader2, RefreshCw } from 'lucide-react';

export const PageError = ({ message, onRetry }) => (
  <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
    <div className="flex items-start gap-3">
      <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
      <div className="flex-1">
        <p className="font-medium">Có lỗi xảy ra</p>
        <p className="mt-1">{message}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-2 rounded-lg border border-red-200 bg-white px-3 py-2 font-medium text-red-700 hover:bg-red-100"
          >
            <RefreshCw className="h-4 w-4" />
            Thử lại
          </button>
        )}
      </div>
    </div>
  </div>
);

export const EmptyState = ({ title = 'Chưa có dữ liệu', description, action }) => (
  <div className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center">
    <Inbox className="mx-auto h-12 w-12 text-gray-400" />
    <p className="mt-4 font-semibold text-gray-900">{title}</p>
    {description && <p className="mx-auto mt-2 max-w-md text-sm text-gray-600">{description}</p>}
    {action && <div className="mt-5">{action}</div>}
  </div>
);

export const InlineLoading = ({ text = 'Đang tải dữ liệu...' }) => (
  <div className="flex items-center justify-center gap-3 rounded-lg border border-gray-200 bg-white p-8 text-gray-600">
    <Loader2 className="h-5 w-5 animate-spin text-green-700" />
    <span className="text-sm font-medium">{text}</span>
  </div>
);
