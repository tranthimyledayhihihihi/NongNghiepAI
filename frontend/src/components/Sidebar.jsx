import {
  BarChart3,
  Bell,
  Bot,
  Camera,
  Calendar,
  FileText,
  LayoutDashboard,
  Leaf,
  Settings,
  Sprout,
  TrendingUp,
  X,
} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const navigation = [
  { name: 'Bảng điều khiển', href: '/dashboard', icon: LayoutDashboard, match: ['/dashboard', '/dashboard-new'] },
  { name: 'Định giá nông sản', href: '/pricing', icon: TrendingUp, match: ['/pricing', '/pricing-dashboard', '/crop'] },
  { name: 'Kiểm định chất lượng', href: '/quality', icon: Camera, match: ['/quality', '/quality-check'] },
  { name: 'Dự báo thu hoạch', href: '/harvest', icon: Sprout, match: ['/harvest', '/harvest-forecast'] },
  { name: 'Quản lý mùa vụ', href: '/season-management', icon: Calendar, match: ['/season-management'] },
  { name: 'Phân tích thị trường', href: '/market', icon: BarChart3, match: ['/market', '/market-strategy'] },
  { name: 'Cảnh báo giá', href: '/alerts', icon: Bell, match: ['/alerts', '/alerts-management'] },
  { name: 'Báo cáo', href: '/reports', icon: FileText, match: ['/reports'] },
  { name: 'Trợ lý AI', href: '/ai-chat', icon: Bot, match: ['/ai-chat'] },
  { name: 'Thông báo', href: '/notifications', icon: Bell, match: ['/notifications'] },
  { name: 'Cài đặt', href: '/settings', icon: Settings, match: ['/settings'] },
];

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();

  const isActive = (item) =>
    item.match.some((path) =>
      path === item.href ? location.pathname === path : location.pathname.startsWith(path)
    );

  return (
    <>
      {open && (
        <button
          type="button"
          className="fixed inset-0 z-20 bg-gray-600/75 lg:hidden"
          onClick={() => setOpen(false)}
          aria-label="Đóng menu"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 transform border-r border-gray-200 bg-white transition-transform duration-300 ease-in-out lg:static lg:inset-0 lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center justify-between border-b border-gray-200 px-6">
            <Link to="/" className="flex items-center gap-2" onClick={() => setOpen(false)}>
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-600 text-white">
                <Leaf className="h-6 w-6" />
              </span>
              <span>
                <span className="block text-xl font-bold text-gray-900">AgriAI</span>
                <span className="block text-xs text-gray-500">Nông nghiệp thông minh</span>
              </span>
            </Link>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700 lg:hidden"
              aria-label="Đóng menu"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <nav className="flex-1 space-y-1 overflow-y-auto px-4 py-6">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setOpen(false)}
                  className={`flex items-center rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                    active ? 'bg-emerald-50 text-emerald-700' : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 ${active ? 'text-emerald-600' : 'text-gray-400'}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="border-t border-gray-200 p-4">
            <Link
              to="/quality-check"
              onClick={() => setOpen(false)}
              className="flex w-full items-center justify-center rounded-lg bg-emerald-600 px-4 py-3 font-medium text-white transition-colors hover:bg-emerald-700"
            >
              Phân tích mới
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
