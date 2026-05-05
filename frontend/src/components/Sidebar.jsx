import {
  BarChart3,
  Bell,
  Camera,
  LayoutDashboard,
  Sprout,
  TrendingUp,
  X
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Bảng điều khiển', href: '/', icon: LayoutDashboard },
    { name: 'Định giá thông minh', href: '/pricing', icon: TrendingUp },
    { name: 'Kiểm định chất lượng', href: '/quality', icon: Camera },
    { name: 'Dự báo thu hoạch', href: '/harvest', icon: Sprout },
    { name: 'Quản lý mùa vụ', href: '/season-management', icon: Calendar },
    { name: 'Phân tích thị trường', href: '/market', icon: BarChart3 },
    { name: 'Cảnh báo giá', href: '/alerts', icon: Bell },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0
          ${open ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">🌾</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AgriAI</h1>
                <p className="text-xs text-gray-500">Nông nghiệp Chuyên gia</p>
              </div>
            </Link>
            <button
              onClick={() => setOpen(false)}
              className="lg:hidden text-gray-500 hover:text-gray-700"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg
                    transition-colors duration-150
                    ${active
                      ? 'bg-emerald-50 text-emerald-700'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 mr-3 ${active ? 'text-emerald-600' : 'text-gray-400'}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Bottom Action */}
          <div className="p-4 border-t border-gray-200">
            <button className="w-full flex items-center justify-center px-4 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors">
              <span className="text-lg mr-2">+</span>
              Phân tích mới
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
