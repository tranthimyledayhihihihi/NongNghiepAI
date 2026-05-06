import { Lock, Mail, Phone, Sprout, User } from 'lucide-react';
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = ({ initialMode = 'login' }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register, isAuthenticated, user } = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    email: '',
    password: '',
    remember: true,
  });
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const isLogin = mode === 'login';
  const redirectTo = location.state?.from?.pathname || '/dashboard';

  const handleChange = (event) => {
    const { name, value, checked, type } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      if (isLogin) {
        await login({
          email: formData.email,
          password: formData.password,
        });
      } else {
        await register({
          fullName: formData.fullName,
          email: formData.email,
          password: formData.password,
          phoneNumber: formData.phone,
        });
      }
      navigate(redirectTo, { replace: true });
    } catch (error) {
      const detail = error.response?.data?.detail;
      setMessage(detail || 'Không thể xác thực tài khoản. Vui lòng kiểm tra lại thông tin.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDemoLogin = async () => {
    setSubmitting(true);
    setMessage('');

    const demoPayload = {
      email: 'tranthimy2205@gmail.com',
      password: '123456',
    };

    try {
      await login(demoPayload);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      const detail = error.response?.data?.detail;
      setMessage(detail || 'Không thể đăng nhập tài khoản mẫu từ bảng Users.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main className="bg-gray-50">
        <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8">
          <div className="relative hidden overflow-hidden rounded-lg lg:block">
            <img
              src="https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=1200&q=85"
              alt="Trang trại xanh"
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gray-950/35" />
            <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-green-700">
                <Sprout className="h-6 w-6" />
              </div>
              <h1 className="text-3xl font-bold">Quản lý dữ liệu nông trại trong một nơi</h1>
              <p className="mt-3 max-w-lg leading-7 text-gray-100">
                Đăng nhập để mở dashboard, lưu cấu hình cảnh báo, theo dõi mùa vụ và dùng trợ lý AI theo hồ sơ trang trại.
              </p>
            </div>
          </div>

          <div className="flex items-center">
            <div className="w-full rounded-lg border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
              <div className="mb-6">
                <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Tài khoản</p>
                <h1 className="mt-2 text-3xl font-bold text-gray-900">
                  {isLogin ? 'Đăng nhập AgriAI' : 'Tạo tài khoản AgriAI'}
                </h1>
                <p className="mt-2 text-sm text-gray-600">
                  {isLogin
                    ? 'Dùng email hoặc số điện thoại đã đăng ký để vào hệ thống.'
                    : 'Tạo hồ sơ ban đầu để chuẩn bị kết nối BE xác thực sau.'}
                </p>
              </div>

              {isAuthenticated && (
                <div className="mb-5 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                  Bạn đang đăng nhập với tài khoản {user?.name}. Có thể vào dashboard ngay.
                </div>
              )}

              <div className="mb-6 grid grid-cols-2 rounded-lg border border-gray-300 bg-gray-50 p-1">
                <button
                  type="button"
                  onClick={() => {
                    setMode('login');
                    setMessage('');
                  }}
                  className={`rounded-md py-2 text-sm font-semibold ${
                    isLogin ? 'bg-white text-green-700 shadow-sm' : 'text-gray-600'
                  }`}
                >
                  Đăng nhập
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMode('register');
                    setMessage('');
                  }}
                  className={`rounded-md py-2 text-sm font-semibold ${
                    !isLogin ? 'bg-white text-green-700 shadow-sm' : 'text-gray-600'
                  }`}
                >
                  Đăng ký
                </button>
              </div>

              {message && (
                <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {message}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-gray-700">Họ và tên</label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                        <input
                          name="fullName"
                          value={formData.fullName}
                          onChange={handleChange}
                          required
                          className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                          placeholder="Nguyễn Văn An"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="mb-2 block text-sm font-medium text-gray-700">Số điện thoại</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                        <input
                          name="phone"
                          value={formData.phone}
                          onChange={handleChange}
                          required
                          className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                          placeholder="0912 345 678"
                        />
                      </div>
                    </div>
                  </div>
                )}

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                      placeholder="email@example.com"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Mật khẩu</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      minLength={6}
                      className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                      placeholder="Tối thiểu 6 ký tự"
                    />
                  </div>
                </div>

                {isLogin && (
                  <div className="flex items-center justify-between gap-4 text-sm">
                    <label className="flex items-center gap-2 text-gray-700">
                      <input
                        type="checkbox"
                        name="remember"
                        checked={formData.remember}
                        onChange={handleChange}
                        className="h-4 w-4 rounded border-gray-300 text-green-700 focus:ring-green-600"
                      />
                      Ghi nhớ đăng nhập
                    </label>
                    <button type="button" className="font-medium text-green-700 hover:text-green-800">
                      Quên mật khẩu?
                    </button>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? 'Đang xử lý...' : isLogin ? 'Đăng nhập' : 'Tạo tài khoản'}
                </button>
              </form>

              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={submitting}
                className="mt-3 w-full rounded-lg border border-gray-300 px-5 py-3 font-semibold text-gray-800 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Đăng nhập tài khoản mẫu từ Users
              </button>

              <p className="mt-6 text-center text-sm text-gray-600">
                {isLogin ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'}{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode(isLogin ? 'register' : 'login');
                    setMessage('');
                  }}
                  className="font-semibold text-green-700 hover:text-green-800"
                >
                  {isLogin ? 'Đăng ký ngay' : 'Đăng nhập'}
                </button>
              </p>

              <div className="mt-6 rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
                Form này gọi trực tiếp API auth của backend và lưu JWT trả về trong trình duyệt.
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
};

export default LoginPage;
