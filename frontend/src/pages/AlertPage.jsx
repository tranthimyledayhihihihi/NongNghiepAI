import AlertHistory from '../components/Alert/AlertHistory';
import AlertSubscribe from '../components/Alert/AlertSubscribe';

const AlertPage = () => {
  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Cảnh báo biến động giá
        </h1>
        <p className="mt-2 text-gray-600">
          Đăng ký nhận thông báo khi giá nông sản thay đổi
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertSubscribe />
        <AlertHistory />
      </div>

      <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Lưu ý:</strong> Tính năng cảnh báo giá sẽ được hoàn thiện trong Phase 2 với tích hợp Zalo API và Email notifications.
        </p>
      </div>
    </div>
  );
};

export default AlertPage;
