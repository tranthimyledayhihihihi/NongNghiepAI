import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AgriNavbar from "../components/AgriNavbar";
import logo from "../assets/agri-ai-logo.png";

const categories = ["Tất cả", "Thời tiết", "Giá nông sản", "Thu hoạch", "Thị trường", "AI Chat"];

const featureCards = [
  {
    title: "Thời tiết nông nghiệp realtime",
    category: "Thời tiết",
    icon: "🌦️",
    route: "/weather",
    badge: "Realtime API",
    description: "Theo dõi nhiệt độ, lượng mưa, độ ẩm, gió và cảnh báo rủi ro thời tiết theo khu vực canh tác.",
    highlights: ["Dự báo 7 ngày", "Cảnh báo mưa lớn", "Gợi ý tưới tiêu"],
  },
  {
    title: "Định giá nông sản thông minh",
    category: "Giá nông sản",
    icon: "📈",
    route: "/pricing",
    badge: "AI Pricing",
    description: "Cập nhật giá nông sản, so sánh vùng miền và hỗ trợ nông dân quyết định nên bán hay theo dõi thêm.",
    highlights: ["Giá hiện tại", "Biểu đồ xu hướng", "So sánh khu vực"],
  },
  {
    title: "Dự báo ngày thu hoạch",
    category: "Thu hoạch",
    icon: "🌾",
    route: "/harvest",
    badge: "Forecast",
    description: "Ước tính ngày thu hoạch dựa trên cây trồng, ngày xuống giống, khu vực, thời tiết và lịch sử mùa vụ.",
    highlights: ["Timeline mùa vụ", "Độ tin cậy", "Checklist chuẩn bị"],
  },
  {
    title: "Phân tích thị trường tiêu thụ",
    category: "Thị trường",
    icon: "🛒",
    route: "/market",
    badge: "Market Data",
    description: "Theo dõi nhu cầu thị trường, tin tức nông sản và gợi ý kênh bán phù hợp với sản lượng thực tế.",
    highlights: ["Tin tức thị trường", "Kênh bán hàng", "Chiến lược tiêu thụ"],
  },
  {
    title: "Trợ lý AI nông nghiệp",
    category: "AI Chat",
    icon: "🤖",
    route: "/ai-chat",
    badge: "GenAI",
    description: "Cho phép người dùng hỏi về thời tiết, giá cả, sâu bệnh, thu hoạch, thị trường và nhận tư vấn dễ hiểu.",
    highlights: ["Gợi ý câu hỏi", "Trả lời có ngữ cảnh", "Nút hành động nhanh"],
  },
  {
    title: "Bài viết và kiến thức nông nghiệp",
    category: "Thị trường",
    icon: "📰",
    route: "/articles",
    badge: "Content",
    description: "Tập hợp bài viết, hướng dẫn và tin tức giúp người dùng hiểu thị trường và cách vận hành hệ thống.",
    highlights: ["Bộ lọc chủ đề", "Tóm tắt nội dung", "Liên kết module"],
  },
];

const dataLayers = [
  {
    name: "Realtime API",
    value: "Dữ liệu bên ngoài",
    description: "Dùng cho thời tiết, giá thị trường, tin tức hoặc các nguồn dữ liệu thay đổi liên tục theo ngày.",
  },
  {
    name: "Database",
    value: "Dữ liệu nội bộ",
    description: "Lưu hồ sơ mùa vụ, lịch sử giá, lịch sử chat, thông tin người dùng và các cảnh báo đã tạo.",
  },
  {
    name: "AI Model",
    value: "Dự báo và khuyến nghị",
    description: "AI dùng dữ liệu đầu vào để dự báo thu hoạch, gợi ý bán hàng và tư vấn nông nghiệp có ngữ cảnh.",
  },
];

const roadmap = [
  "Tạo bộ lọc cây trồng/khu vực dùng chung cho các trang chính.",
  "Hiển thị badge nguồn dữ liệu: API realtime, DB, AI Model.",
  "Thêm trạng thái loading skeleton, empty state và error state.",
  "Cho phép lưu cảnh báo giá/thời tiết trực tiếp từ từng tính năng.",
  "Liên kết AI Chat với dữ liệu trang hiện tại để tư vấn có ngữ cảnh.",
];

export default function FeaturesPage() {
  const [selectedCategory, setSelectedCategory] = useState("Tất cả");

  const filteredFeatures = useMemo(() => {
    if (selectedCategory === "Tất cả") return featureCards;
    return featureCards.filter((feature) => feature.category === selectedCategory);
  }, [selectedCategory]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AgriNavbar />

      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-950 via-green-900 to-lime-700 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.20),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(190,242,100,0.24),transparent_34%)]" />
        <div className="relative mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-20">
          <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
            <div>
              <span className="inline-flex rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold text-emerald-50 backdrop-blur">
                ✨ Trung tâm tính năng AgriAI
              </span>
              <h1 className="mt-6 max-w-3xl text-4xl font-black tracking-tight sm:text-5xl">
                Tất cả công cụ cần thiết để nông dân ra quyết định nhanh hơn
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-8 text-emerald-50 sm:text-lg">
                Trang features được bổ sung thanh menu, logo và bố cục đồng bộ với trang chủ, bài viết, bảng giá và liên hệ. Người dùng có thể hiểu từng module dùng dữ liệu gì và bấm sang dùng ngay.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/ai-chat" className="rounded-2xl bg-white px-5 py-3 font-bold text-emerald-800 shadow-lg shadow-black/10 transition hover:-translate-y-0.5 hover:bg-emerald-50">
                  Dùng thử AI Chat
                </Link>
                <Link to="/pricing-plans" className="rounded-2xl border border-white/30 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                  Xem gói dịch vụ
                </Link>
                <Link to="/contact" className="rounded-2xl border border-white/30 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                  Liên hệ hỗ trợ
                </Link>
              </div>
            </div>

            <div className="rounded-[2rem] border border-white/20 bg-white/10 p-5 shadow-2xl backdrop-blur">
              <div className="rounded-[1.5rem] bg-white p-6 text-slate-900">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Tổng quan hệ thống</p>
                    <h2 className="mt-2 text-2xl font-black">5 module chính + AI hỗ trợ</h2>
                  </div>
                  <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-[1.5rem] border border-emerald-100 bg-white shadow-sm">
                    <img src={logo} alt="AgriAI" className="h-full w-full object-cover object-center" />
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <div className="rounded-2xl bg-emerald-50 p-4">
                    <p className="text-2xl font-black text-emerald-700">API</p>
                    <p className="text-sm text-slate-600">Dữ liệu realtime</p>
                  </div>
                  <div className="rounded-2xl bg-lime-50 p-4">
                    <p className="text-2xl font-black text-lime-700">AI</p>
                    <p className="text-sm text-slate-600">Tư vấn thông minh</p>
                  </div>
                  <div className="rounded-2xl bg-amber-50 p-4">
                    <p className="text-2xl font-black text-amber-700">DB</p>
                    <p className="text-sm text-slate-600">Lưu lịch sử</p>
                  </div>
                  <div className="rounded-2xl bg-sky-50 p-4">
                    <p className="text-2xl font-black text-sky-700">UX</p>
                    <p className="text-sm text-slate-600">Dễ dùng hơn</p>
                  </div>
                </div>

                <div className="mt-6 rounded-2xl bg-slate-900 p-4 text-white">
                  <p className="text-sm font-bold text-emerald-200">Luồng trải nghiệm đề xuất</p>
                  <p className="mt-2 text-sm leading-6 text-slate-200">
                    Chọn khu vực → xem dữ liệu realtime → nhận phân tích AI → lưu cảnh báo hoặc hành động.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Danh sách tính năng</p>
              <h2 className="mt-1 text-2xl font-black">Lọc theo nhóm chức năng</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  type="button"
                  onClick={() => setSelectedCategory(category)}
                  className={`rounded-2xl px-4 py-3 text-sm font-bold transition ${
                    selectedCategory === category
                      ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20"
                      : "bg-slate-100 text-slate-600 hover:bg-emerald-50 hover:text-emerald-700"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredFeatures.map((feature) => (
            <article key={feature.title} className="group rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-emerald-200 hover:shadow-xl hover:shadow-emerald-900/5">
              <div className="flex items-start justify-between gap-4">
                <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-3xl transition group-hover:scale-105">
                  {feature.icon}
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">
                  {feature.badge}
                </span>
              </div>
              <p className="mt-5 text-sm font-black uppercase tracking-wide text-emerald-600">{feature.category}</p>
              <h3 className="mt-2 text-xl font-black leading-snug group-hover:text-emerald-700">{feature.title}</h3>
              <p className="mt-3 leading-7 text-slate-600">{feature.description}</p>
              <div className="mt-5 space-y-2">
                {feature.highlights.map((item) => (
                  <div key={item} className="flex items-center gap-2 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700">
                    <span className="text-emerald-600">✓</span>
                    {item}
                  </div>
                ))}
              </div>
              <Link to={feature.route} className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-slate-900 px-4 py-3 font-bold text-white transition hover:bg-emerald-700">
                Mở tính năng
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-6 lg:grid-cols-3">
            {dataLayers.map((layer) => (
              <div key={layer.name} className="rounded-[2rem] border border-slate-200 bg-slate-50 p-6">
                <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-black text-emerald-700">
                  {layer.name}
                </span>
                <h3 className="mt-4 text-2xl font-black">{layer.value}</h3>
                <p className="mt-3 leading-7 text-slate-600">{layer.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div>
            <p className="text-sm font-black uppercase tracking-wide text-emerald-600">Nâng cấp nên làm tiếp</p>
            <h2 className="mt-3 text-3xl font-black tracking-tight sm:text-4xl">Biến trang features thành trung tâm điều hướng thật sự</h2>
            <p className="mt-4 leading-8 text-slate-600">
              Không nên chỉ liệt kê tính năng. Hãy cho người dùng thấy mỗi tính năng lấy dữ liệu từ đâu, giải quyết vấn đề gì và có thể bấm sang dùng ngay.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/weather" className="rounded-2xl bg-emerald-600 px-5 py-3 font-bold text-white transition hover:bg-emerald-700">
                Xem thời tiết
              </Link>
              <Link to="/market" className="rounded-2xl border border-slate-200 bg-white px-5 py-3 font-bold text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700">
                Xem thị trường
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-2xl font-black">Checklist chỉnh sửa / nâng cấp</h3>
            <div className="mt-5 space-y-3">
              {roadmap.map((item) => (
                <div key={item} className="flex gap-3 rounded-2xl bg-slate-50 p-4 text-sm font-semibold text-slate-700">
                  <span className="mt-0.5 text-emerald-600">✓</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
