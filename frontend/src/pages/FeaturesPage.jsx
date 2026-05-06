import {
  BarChart3,
  BellRing,
  Bot,
  Camera,
  CheckCircle2,
  CloudSun,
  LineChart,
  Sprout,
  Store,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';

const featureGroups = [
  {
    icon: LineChart,
    title: 'Định giá nông sản',
    description: 'Theo dõi giá hiện tại, lịch sử biến động và dự báo ngắn hạn theo từng vùng.',
    points: ['Biểu đồ giá theo ngày', 'So sánh vùng bán', 'Khuyến nghị thời điểm bán'],
  },
  {
    icon: Camera,
    title: 'Kiểm định chất lượng',
    description: 'Upload ảnh nông sản để AI nhận diện chất lượng, bệnh hại và gợi ý xử lý.',
    points: ['Phân loại theo lô', 'Nhận diện rủi ro', 'Gợi ý cải thiện chất lượng'],
  },
  {
    icon: Sprout,
    title: 'Dự báo thu hoạch',
    description: 'Ước tính ngày thu hoạch, sản lượng và việc cần làm dựa trên lịch canh tác.',
    points: ['Lịch mùa vụ', 'Dự báo sản lượng', 'Nhắc việc trước mốc quan trọng'],
  },
  {
    icon: Store,
    title: 'Chiến lược thị trường',
    description: 'So sánh kênh bán buôn, bán lẻ, xuất khẩu và đề xuất kênh có lợi nhất.',
    points: ['Biên lợi nhuận từng kênh', 'Nhu cầu theo khu vực', 'Gợi ý B2B'],
  },
  {
    icon: BellRing,
    title: 'Cảnh báo tự động',
    description: 'Nhận thông báo khi giá vượt ngưỡng, thời tiết xấu hoặc lịch mùa vụ đến hạn.',
    points: ['Cảnh báo giá', 'Thông báo thời tiết', 'Lọc theo mức ưu tiên'],
  },
  {
    icon: Bot,
    title: 'Trợ lý AI nông nghiệp',
    description: 'Hỏi đáp kỹ thuật canh tác, sâu bệnh, thị trường và vận hành trang trại.',
    points: ['Gợi ý câu hỏi nhanh', 'Lịch sử hội thoại', 'Tư vấn theo ngữ cảnh trang trại'],
  },
];

const workflow = [
  {
    title: 'Nhập dữ liệu trang trại',
    description: 'Khai báo cây trồng, diện tích, khu vực, lịch gieo trồng và mục tiêu bán hàng.',
  },
  {
    title: 'AI phân tích',
    description: 'Hệ thống kết hợp giá thị trường, thời tiết, ảnh chất lượng và lịch mùa vụ.',
  },
  {
    title: 'Ra quyết định',
    description: 'Người dùng nhận khuyến nghị hành động, cảnh báo và báo cáo để theo dõi.',
  },
];

const FeaturesPage = () => {
  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main>
        <section className="relative isolate overflow-hidden bg-gray-950">
          <img
            src="https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1800&q=85"
            alt="Nông trại ứng dụng công nghệ"
            className="absolute inset-0 -z-10 h-full w-full object-cover opacity-55"
          />
          <div className="absolute inset-0 -z-10 bg-gray-950/35" />
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="max-w-3xl text-white">
              <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-green-200">
                Bộ công cụ FE đã sẵn sàng nối BE
              </p>
              <h1 className="text-4xl font-bold leading-tight md:text-5xl">
                Tính năng quản trị nông nghiệp từ mùa vụ đến thị trường
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-gray-100">
                AgriAI gom các nghiệp vụ quan trọng vào một giao diện thống nhất: dự báo, kiểm định, giá,
                cảnh báo và tư vấn AI cho nông dân, hợp tác xã và đơn vị thu mua.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  to="/dashboard"
                  className="rounded-lg bg-green-700 px-6 py-3 text-center font-semibold text-white hover:bg-green-800"
                >
                  Mở bảng điều khiển
                </Link>
                <Link
                  to="/contact"
                  className="rounded-lg border border-white/70 px-6 py-3 text-center font-semibold text-white hover:bg-white/10"
                >
                  Trao đổi triển khai
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Module chính</p>
                <h2 className="mt-2 text-3xl font-bold text-gray-900">Một hệ thống cho nhiều nghiệp vụ</h2>
              </div>
              <p className="max-w-2xl text-gray-600">
                Các màn hình này đang dùng dữ liệu mẫu hoặc API hiện có. Khi BE bổ sung auth, notification và billing,
                FE có thể nối service mà không cần đổi luồng chính.
              </p>
            </div>

            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {featureGroups.map((feature) => {
                const Icon = feature.icon;
                return (
                  <article key={feature.title} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-lg bg-green-50 text-green-700">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">{feature.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-gray-600">{feature.description}</p>
                    <div className="mt-5 space-y-2">
                      {feature.points.map((point) => (
                        <div key={point} className="flex items-center gap-2 text-sm text-gray-700">
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span>{point}</span>
                        </div>
                      ))}
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Quy trình sử dụng</p>
              <h2 className="mt-2 text-3xl font-bold text-gray-900">Từ dữ liệu rời rạc thành hành động cụ thể</h2>
              <p className="mt-4 leading-7 text-gray-600">
                Thiết kế ưu tiên thao tác nhanh trong môi trường vận hành: ít trang trí, dễ quét thông tin,
                có trạng thái rõ ràng cho cảnh báo, giá và chất lượng.
              </p>
              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-gray-200 p-4">
                  <BarChart3 className="mb-3 h-5 w-5 text-blue-600" />
                  <div className="text-2xl font-bold text-gray-900">8+</div>
                  <div className="text-sm text-gray-600">màn hình nghiệp vụ</div>
                </div>
                <div className="rounded-lg border border-gray-200 p-4">
                  <CloudSun className="mb-3 h-5 w-5 text-amber-600" />
                  <div className="text-2xl font-bold text-gray-900">24/7</div>
                  <div className="text-sm text-gray-600">cảnh báo tự động</div>
                </div>
                <div className="rounded-lg border border-gray-200 p-4">
                  <Bot className="mb-3 h-5 w-5 text-green-700" />
                  <div className="text-2xl font-bold text-gray-900">AI</div>
                  <div className="text-sm text-gray-600">tư vấn theo ngữ cảnh</div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {workflow.map((step, index) => (
                <div key={step.title} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                  <div className="flex gap-4">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-sm font-bold text-white">
                      {index + 1}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">{step.title}</h3>
                      <p className="mt-1 text-sm leading-6 text-gray-600">{step.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
};

export default FeaturesPage;
