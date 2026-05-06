import { Leaf, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const navItems = [
  { label: 'Tính năng', to: '/features' },
  { label: 'Bài viết', to: '/articles' },
  { label: 'Bảng giá', to: '/pricing-plans' },
  { label: 'Liên hệ', to: '/contact' },
];

const PublicHeader = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  const getNavClass = ({ isActive }) =>
    `text-sm font-medium transition ${
      isActive ? 'text-green-700' : 'text-gray-700 hover:text-green-700'
    }`;

  const handleLogout = () => {
    logout();
    setMobileOpen(false);
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-700 text-white">
            <Leaf className="h-6 w-6" />
          </span>
          <span className="text-xl font-bold text-gray-900">AgriAI</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={getNavClass}>
              {item.label}
            </NavLink>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {!isAuthenticated && (
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
            >
              Đăng nhập
            </Link>
          )}
          <Link
            to="/dashboard"
            className="rounded-lg bg-green-700 px-5 py-2 text-sm font-semibold text-white transition hover:bg-green-800"
          >
            Vào hệ thống
          </Link>
          {isAuthenticated && (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-red-600"
              aria-label="Đăng xuất"
              title="Đăng xuất"
            >
              <LogOut className="h-5 w-5" />
            </button>
          )}
        </div>

        <button
          type="button"
          onClick={() => setMobileOpen((value) => !value)}
          className="rounded-lg p-2 text-gray-700 hover:bg-gray-100 md:hidden"
          aria-label="Mở menu"
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {mobileOpen && (
        <div className="border-t border-gray-200 bg-white px-4 py-4 md:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium ${
                    isActive ? 'bg-green-50 text-green-700' : 'text-gray-700 hover:bg-gray-50'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
            <div className="mt-2 grid grid-cols-2 gap-3">
              {!isAuthenticated ? (
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-700"
                >
                  Đăng nhập
                </Link>
              ) : (
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-center text-sm font-medium text-gray-700"
                >
                  Đăng xuất
                </button>
              )}
              <Link
                to="/dashboard"
                onClick={() => setMobileOpen(false)}
                className="rounded-lg bg-green-700 px-4 py-2 text-center text-sm font-semibold text-white"
              >
                Vào hệ thống
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default PublicHeader;
