import { Facebook, Leaf, Mail, MapPin, Phone } from 'lucide-react';
import { Link } from 'react-router-dom';

const PublicFooter = () => {
  return (
    <footer className="bg-gray-950 text-gray-300">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-4">
          <div>
            <div className="mb-4 flex items-center gap-2">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-700 text-white">
                <Leaf className="h-6 w-6" />
              </span>
              <span className="text-xl font-bold text-white">AgriAI</span>
            </div>
            <p className="text-sm leading-6 text-gray-400">
              Nền tảng hỗ trợ nông dân và hợp tác xã quản lý mùa vụ, giá bán và chất lượng nông sản bằng AI.
            </p>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-white">Sản phẩm</h3>
            <div className="space-y-3 text-sm">
              <Link to="/features" className="block hover:text-green-400">Tính năng</Link>
              <Link to="/pricing-plans" className="block hover:text-green-400">Bảng giá</Link>
              <Link to="/dashboard" className="block hover:text-green-400">Bảng điều khiển</Link>
              <Link to="/ai-chat" className="block hover:text-green-400">Trợ lý AI</Link>
            </div>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-white">Tài nguyên</h3>
            <div className="space-y-3 text-sm">
              <Link to="/articles" className="block hover:text-green-400">Bài viết</Link>
              <Link to="/contact" className="block hover:text-green-400">Liên hệ</Link>
              <Link to="/login" className="block hover:text-green-400">Đăng nhập</Link>
              <Link to="/register" className="block hover:text-green-400">Tạo tài khoản</Link>
            </div>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-white">Liên hệ</h3>
            <div className="space-y-3 text-sm text-gray-400">
              <div className="flex gap-3">
                <MapPin className="mt-0.5 h-4 w-4 text-green-400" />
                <span>TP. Hồ Chí Minh, Việt Nam</span>
              </div>
              <div className="flex gap-3">
                <Phone className="mt-0.5 h-4 w-4 text-green-400" />
                <span>1900 888 168</span>
              </div>
              <div className="flex gap-3">
                <Mail className="mt-0.5 h-4 w-4 text-green-400" />
                <span>support@agriai.vn</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-4 border-t border-gray-800 pt-6 text-sm text-gray-500 md:flex-row md:items-center md:justify-between">
          <p>© 2026 AgriAI. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="https://facebook.com" className="hover:text-green-400" aria-label="Facebook">
              <Facebook className="h-5 w-5" />
            </a>
            <Link to="/contact" className="hover:text-green-400">Hỗ trợ</Link>
            <Link to="/pricing-plans" className="hover:text-green-400">Gói dịch vụ</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default PublicFooter;
