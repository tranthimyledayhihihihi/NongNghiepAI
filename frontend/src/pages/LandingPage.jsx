import { Link } from "react-router-dom";
import logo from "../assets/agri-ai-logo.png";
import AgriNavbar from "../components/AgriNavbar";

const coreModules = [
  {
    title: "Thời tiết nông nghiệp",
    route: "/weather",
    icon: "🌦️",
    description: "Theo dõi thời tiết thời gian thực, lượng mưa, độ ẩm, gió và cảnh báo rủi ro theo vùng trồng.",
    tag: "Dữ liệu thời gian thực",
  },
  {
    title: "Định giá nông sản",
    route: "/pricing",
    icon: "📈",
    description: "Cập nhật giá hiện tại, so sánh vùng miền, xem xu hướng và nhận gợi ý thời điểm bán.",
    tag: "Định giá AI",
  },
  {
    title: "Dự báo thu hoạch",
    route: "/harvest",
    icon: "🌾",
    description: "Dự báo ngày thu hoạch, hiển thị tiến độ mùa vụ và danh sách việc cần chuẩn bị trước thu hoạch.",
    tag: "Dự báo",
  },
  {
    title: "Thị trường tiêu thụ",
    route: "/market",
    icon: "🛒",
    description: "Theo dõi nhu cầu thị trường, tin tức nông sản và gợi ý kênh bán phù hợp.",
    tag: "Dữ liệu thị trường",
  },
];

const stats = [
  ["5+", "phân hệ chính"],
  ["24/7", "AI hỗ trợ"],
  ["Dữ liệu", "thời gian thực"],
  ["Lịch sử", "lưu trong hệ thống"],
];

const workflow = [
  {
    step: "01",
    title: "Nhập dữ liệu canh tác",
    description: "Người dùng chọn cây trồng, khu vực, ngày xuống giống, sản lượng hoặc chất lượng nông sản.",
  },
  {
    step: "02",
    title: "Kết hợp dữ liệu và AI",
    description: "Hệ thống lấy thời tiết, giá thị trường, lịch sử mùa vụ và dùng AI để phân tích dữ liệu.",
  },
  {
    step: "03",
    title: "Đưa ra khuyến nghị rõ ràng",
    description: "Nông dân nhận cảnh báo, dự báo, gợi ý bán hàng và hành động tiếp theo dễ hiểu.",
  },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AgriNavbar />

      <section className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-emerald-950 to-green-800 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.18),transparent_30%),radial-gradient(circle_at_bottom_left,rgba(132,204,22,0.24),transparent_34%)]" />
        <div className="relative mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="grid gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
            <div>
              <span className="inline-flex rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold text-emerald-50 backdrop-blur">
                🌱 AgriAI - Nông nghiệp thông minh
              </span>
              <h1 className="mt-6 max-w-4xl text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
                Nền tảng AI hỗ trợ nông dân dự báo, định giá và ra quyết định tốt hơn
              </h1>
              <p className="mt-6 max-w-2xl text-base leading-8 text-emerald-50 sm:text-lg">
                Trang chủ được thiết kế theo hướng hiện đại: có thanh menu, logo AgriAI, nút hành động rõ ràng, thẻ dữ liệu nhanh và điều hướng trực tiếp tới các tính năng chính.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/features" className="rounded-2xl bg-white px-5 py-3 font-bold text-emerald-800 shadow-lg shadow-black/10 transition hover:-translate-y-0.5 hover:bg-emerald-50">
                  Khám phá tính năng
                </Link>
                <Link to="/ai-chat" className="rounded-2xl border border-white/30 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                  Hỏi AI ngay
                </Link>
                <Link to="/pricing-plans" className="rounded-2xl border border-white/30 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                  Xem gói dịch vụ
                </Link>
              </div>

              <div className="mt-10 grid max-w-2xl grid-cols-2 gap-3 sm:grid-cols-4">
                {stats.map(([number, label]) => (
                  <div key={label} className="rounded-2xl border border-white/15 bg-white/10 p-4 text-center backdrop-blur">
                    <p className="text-2xl font-black">{number}</p>
                    <p className="mt-1 text-xs font-semibold text-emerald-100">{label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] border border-white/20 bg-white/10 p-5 shadow-2xl backdrop-blur">
              <div className="rounded-[1.5rem] bg-white p-6 text-slate-900">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Bảng điều khiển AgriAI</p>
                    <h2 className="mt-2 text-2xl font-black">Tình hình hôm nay</h2>
                  </div>
                  <div className="flex h-28 w-28 items-center justify-center overflow-hidden rounded-[1.5rem] border border-emerald-100 bg-white shadow-sm">
                    <img src={logo} alt="AgriAI" className="h-full w-full object-cover object-center" />
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="rounded-2xl bg-emerald-50 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <span className="font-bold text-slate-800">Thời tiết</span>
                      <span className="rounded-full bg-emerald-600 px-3 py-1 text-xs font-black text-white">Ổn định</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">Có thể tưới nhẹ vào sáng sớm, theo dõi mưa chiều.</p>
                  </div>
                  <div className="rounded-2xl bg-lime-50 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <span className="font-bold text-slate-800">Giá nông sản</span>
                      <span className="rounded-full bg-lime-600 px-3 py-1 text-xs font-black text-white">+3.2%</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">Giá đang tăng, nên so sánh thêm giữa các vùng trước khi bán.</p>
                  </div>
                  <div className="rounded-2xl bg-amber-50 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <span className="font-bold text-slate-800">Thu hoạch</span>
                      <span className="rounded-full bg-amber-500 px-3 py-1 text-xs font-black text-white">Sắp tới</span>
                    </div>
                    <p className="mt-2 text-sm text-slate-600">Chuẩn bị nhân công, bao bì và kiểm tra thời tiết trước 3 ngày.</p>
                  </div>
                </div>

                <Link to="/dashboard" className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 font-bold text-white transition hover:bg-emerald-700">
                  Vào bảng điều khiển
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Module nổi bật</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Đi thẳng tới công cụ bạn cần</h2>
            <p className="mt-3 max-w-2xl leading-7 text-slate-600">
              Các thẻ dưới đây giúp người dùng nhìn là hiểu hệ thống có những chức năng gì và bấm sang sử dụng ngay.
            </p>
          </div>
          <Link to="/features" className="inline-flex rounded-2xl border border-slate-200 bg-white px-5 py-3 font-bold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700">
            Xem tất cả tính năng
          </Link>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {coreModules.map((module) => (
            <article key={module.title} className="group rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-emerald-200 hover:shadow-xl hover:shadow-emerald-900/5">
              <div className="flex items-start justify-between gap-4">
                <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-3xl transition group-hover:scale-105">
                  {module.icon}
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
                  {module.tag}
                </span>
              </div>
              <h3 className="mt-5 text-xl font-black group-hover:text-emerald-700">{module.title}</h3>
              <p className="mt-3 leading-7 text-slate-600">{module.description}</p>
              <Link to={module.route} className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 font-bold text-white transition hover:bg-emerald-700">
                Mở tính năng
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Quy trình hoạt động</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Từ dữ liệu thực tế đến quyết định sản xuất</h2>
              <p className="mt-4 leading-8 text-slate-600">
                Phần này giúp giải thích rõ hệ thống không chỉ có giao diện đẹp mà còn có luồng xử lý hợp lý: nhập dữ liệu, phân tích, khuyến nghị.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link to="/articles" className="rounded-2xl bg-emerald-600 px-5 py-3 font-bold text-white transition hover:bg-emerald-700">
                  Đọc bài viết
                </Link>
                <Link to="/contact" className="rounded-2xl border border-slate-200 bg-white px-5 py-3 font-bold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700">
                  Liên hệ hỗ trợ
                </Link>
              </div>
            </div>

            <div className="space-y-4">
              {workflow.map((item) => (
                <div key={item.step} className="rounded-[2rem] border border-slate-200 bg-slate-50 p-5">
                  <div className="flex gap-4">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-emerald-600 text-lg font-black text-white">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="text-lg font-black">{item.title}</h3>
                      <p className="mt-2 leading-7 text-slate-600">{item.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] bg-slate-950 p-8 text-white sm:p-10 lg:p-12">
          <div className="grid gap-8 lg:grid-cols-[1fr_0.8fr] lg:items-center">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-emerald-300">Sẵn sàng trải nghiệm</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Bắt đầu với trợ lý AI nông nghiệp</h2>
              <p className="mt-4 max-w-2xl leading-8 text-slate-300">
                Người dùng có thể hỏi AI về thời tiết, giá cả, thu hoạch, thị trường hoặc chuyển sang bảng điều khiển để xem dữ liệu chi tiết.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 lg:justify-end">
              <Link to="/ai-chat" className="rounded-2xl bg-white px-5 py-3 font-bold text-slate-950 transition hover:bg-emerald-50">
                Hỏi AI ngay
              </Link>
              <Link to="/dashboard" className="rounded-2xl border border-white/20 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                Vào bảng điều khiển
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
