import { Bell, HelpCircle, LogOut, Menu, Search, Settings, User } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = ({ setSidebarOpen }) => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex flex-1 items-center">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="mr-4 rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 lg:hidden"
            aria-label="Mở menu"
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="relative w-full max-w-md">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm nông sản, mùa vụ hoặc thị trường..."
              className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 outline-none focus:border-transparent focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-3">
          <Link
            to="/notifications"
            className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            aria-label="Xem thông báo"
            title="Thông báo"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-green-600" />
          </Link>
          <Link
            to="/contact"
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            aria-label="Trợ giúp"
            title="Trợ giúp"
          >
            <HelpCircle className="h-5 w-5" />
          </Link>
          <Link
            to="/settings"
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            aria-label="Cài đặt"
            title="Cài đặt"
          >
            <Settings className="h-5 w-5" />
          </Link>
          <Link
            to="/profile"
            className="hidden items-center gap-2 rounded-lg p-2 hover:bg-gray-100 sm:flex"
            aria-label="Hồ sơ"
            title="Hồ sơ"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600">
              <User className="h-5 w-5 text-white" />
            </span>
            <span className="hidden max-w-32 truncate text-sm font-medium text-gray-700 xl:block">
              {user?.name || 'Tài khoản'}
            </span>
          </Link>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-red-600"
            aria-label="Đăng xuất"
            title="Đăng xuất"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
