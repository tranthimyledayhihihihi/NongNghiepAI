import {
  ArrowRight,
  BarChart3,
  BellRing,
  Bot,
  Camera,
  CheckCircle2,
  CloudSun,
  Sprout,
  TrendingUp,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';

const featureHighlights = [
  {
    icon: TrendingUp,
    title: 'Định giá thông minh',
    description: 'Theo dõi giá hiện tại, lịch sử và dự báo để chọn thời điểm bán phù hợp.',
    to: '/pricing',
  },
  {
    icon: Camera,
    title: 'Kiểm định chất lượng',
    description: 'Phân tích ảnh nông sản để phát hiện rủi ro chất lượng và sâu bệnh.',
    to: '/quality',
  },
  {
    icon: Sprout,
    title: 'Dự báo thu hoạch',
    description: 'Ước tính ngày thu hoạch, sản lượng và nhắc việc theo lịch mùa vụ.',
    to: '/harvest',
  },
  {
    icon: Bot,
    title: 'Trợ lý AI',
    description: 'Hỏi đáp kỹ thuật canh tác, thị trường và vận hành trang trại.',
    to: '/ai-chat',
  },
];

const stats = [
  { value: '5.000+', label: 'hồ sơ nông hộ có thể quản lý' },
  { value: '8+', label: 'màn hình nghiệp vụ đã dựng' },
  { value: '24/7', label: 'luồng cảnh báo sẵn sàng mở rộng' },
];

const articles = [
  {
    title: 'Lập lịch chăm sóc lúa trong giai đoạn làm đòng',
    image: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=900&q=80',
    category: 'Canh tác',
  },
  {
    title: 'Cách đọc tín hiệu giá trước khi chốt bán nông sản',
    image: 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=900&q=80',
    category: 'Thị trường',
  },
  {
    title: 'Nhận diện sớm bệnh đạo ôn qua ảnh lá lúa',
    image: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80',
    category: 'Sâu bệnh',
  },
];

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main>
        <section className="relative isolate min-h-[78vh] overflow-hidden bg-gray-950">
          <img
            src="https://images.unsplash.com/photo-1495107334309-fcf20504a5ab?auto=format&fit=crop&w=1900&q=85"
            alt="Cánh đồng nông nghiệp Việt Nam"
            className="absolute inset-0 -z-10 h-full w-full object-cover opacity-60"
          />
          <div className="absolute inset-0 -z-10 bg-gray-950/35" />
          <div className="mx-auto flex min-h-[78vh] max-w-7xl items-center px-4 py-16 sm:px-6 lg:px-8">
            <div className="max-w-3xl text-white">
              <p className="mb-5 inline-flex rounded-full bg-white/15 px-4 py-2 text-sm font-semibold text-green-100 ring-1 ring-white/25">
                Nền tảng AI cho nông nghiệp Việt Nam
              </p>
              <h1 className="text-4xl font-bold leading-tight md:text-6xl">
                AgriAI
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-gray-100">
                Quản lý giá nông sản, chất lượng, mùa vụ, cảnh báo và tư vấn AI trong một hệ thống web dễ dùng.
                Phần FE đã sẵn sàng để nối các API BE tiếp theo.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/dashboard"
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
                >
                  Vào dashboard
                  <ArrowRight className="h-5 w-5" />
                </Link>
                <Link
                  to="/features"
                  className="inline-flex items-center justify-center rounded-lg border border-white/70 px-6 py-3 font-semibold text-white hover:bg-white/10"
                >
                  Xem tính năng
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-gray-200 bg-white">
          <div className="mx-auto grid max-w-7xl gap-4 px-4 py-8 sm:px-6 md:grid-cols-3 lg:px-8">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-lg border border-gray-200 p-5">
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="mt-1 text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-gray-50 py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Tính năng nổi bật</p>
                <h2 className="mt-2 text-3xl font-bold text-gray-900">Bộ công cụ cho vận hành nông nghiệp</h2>
              </div>
              <Link to="/features" className="inline-flex items-center gap-1 font-semibold text-green-700 hover:text-green-800">
                Xem tất cả
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              {featureHighlights.map((feature) => {
                const Icon = feature.icon;
                return (
                  <Link
                    key={feature.title}
                    to={feature.to}
                    className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
                  >
                    <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-lg bg-green-50 text-green-700">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-bold text-gray-900">{feature.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-gray-600">{feature.description}</p>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-[1fr_1fr] lg:px-8">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Dashboard vận hành</p>
              <h2 className="mt-2 text-3xl font-bold text-gray-900">Theo dõi rủi ro ngay khi mở hệ thống</h2>
              <p className="mt-4 leading-7 text-gray-600">
                Các màn hình trong app đã có khu vực cho cảnh báo giá, thời tiết, lịch thu hoạch, báo cáo và AI chat.
                Người dùng có thể thao tác demo ngay trong khi BE tiếp tục hoàn thiện.
              </p>
              <div className="mt-6 space-y-3">
                {[
                  'Nối nhanh với API giá, chất lượng, mùa vụ đang có.',
                  'Tách riêng trang public và trang quản trị để dễ mở rộng auth.',
                  'Thông báo và cài đặt dùng state local trước khi có BE.',
                ].map((item) => (
                  <div key={item} className="flex gap-3 text-sm text-gray-700">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-green-700" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8">
                <Link
                  to="/notifications"
                  className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-5 py-3 font-semibold text-gray-800 hover:bg-gray-50"
                >
                  <BellRing className="h-5 w-5" />
                  Xem thông báo demo
                </Link>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-gray-200 p-5 shadow-sm">
                <BarChart3 className="mb-4 h-6 w-6 text-blue-600" />
                <h3 className="font-bold text-gray-900">Phân tích giá</h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">Biểu đồ dự báo, so sánh vùng và đề xuất kênh bán.</p>
              </div>
              <div className="rounded-lg border border-gray-200 p-5 shadow-sm">
                <CloudSun className="mb-4 h-6 w-6 text-amber-600" />
                <h3 className="font-bold text-gray-900">Thời tiết mùa vụ</h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">Cảnh báo điều kiện bất lợi và lịch việc cần làm.</p>
              </div>
              <div className="rounded-lg border border-gray-200 p-5 shadow-sm sm:col-span-2">
                <img
                  src="https://images.unsplash.com/photo-1586771107445-d3ca888129ff?auto=format&fit=crop&w=1100&q=80"
                  alt="Nông dân kiểm tra cây trồng"
                  className="mb-4 h-56 w-full rounded-lg object-cover"
                />
                <h3 className="font-bold text-gray-900">Từ hiện trường đến quyết định</h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">
                  Upload ảnh, xem cảnh báo và hỏi trợ lý AI trên cùng một hệ thống thay vì dùng nhiều công cụ rời rạc.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Bài viết</p>
                <h2 className="mt-2 text-3xl font-bold text-gray-900">Kiến thức để vận hành tốt hơn</h2>
              </div>
              <Link to="/articles" className="inline-flex items-center gap-1 font-semibold text-green-700 hover:text-green-800">
                Mở thư viện
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              {articles.map((article) => (
                <article key={article.title} className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
                  <img src={article.image} alt={article.title} className="h-48 w-full object-cover" />
                  <div className="p-5">
                    <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
                      {article.category}
                    </span>
                    <h3 className="mt-4 text-lg font-bold text-gray-900">{article.title}</h3>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-gray-950 py-16 text-white">
          <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
            <div>
              <h2 className="text-3xl font-bold">Sẵn sàng thử giao diện quản trị?</h2>
              <p className="mt-2 max-w-2xl text-gray-300">
                Vào dashboard demo để xem các luồng FE đã có trước khi nối phần BE còn thiếu.
              </p>
            </div>
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center rounded-lg bg-green-700 px-6 py-3 font-semibold text-white hover:bg-green-800"
            >
              Mở dashboard
            </Link>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
};

export default LandingPage;
