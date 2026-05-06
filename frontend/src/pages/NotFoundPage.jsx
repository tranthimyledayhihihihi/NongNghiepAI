import { ArrowLeft, Home } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';

const NotFoundContent = () => {
  const navigate = useNavigate();

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center px-4 py-16 text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-green-700">404</p>
      <h1 className="mt-3 text-4xl font-bold text-gray-900">Không tìm thấy trang</h1>
      <p className="mt-4 max-w-xl leading-7 text-gray-600">
        Đường dẫn này chưa tồn tại hoặc đã được đổi tên. Bạn có thể quay lại trang trước hoặc mở bảng điều khiển.
      </p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-5 py-3 font-semibold text-gray-800 hover:bg-gray-50"
        >
          <ArrowLeft className="h-5 w-5" />
          Quay lại
        </button>
        <Link
          to="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800"
        >
          <Home className="h-5 w-5" />
          Vào dashboard
        </Link>
      </div>
    </div>
  );
};

const NotFoundPage = ({ publicLayout = true }) => {
  if (!publicLayout) {
    return <NotFoundContent />;
  }

  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />
      <NotFoundContent />
      <PublicFooter />
    </div>
  );
};

export default NotFoundPage;
