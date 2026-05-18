import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AgriNavbar from "../components/AgriNavbar";

const categories = ["Tất cả", "Thời tiết", "Giá nông sản", "Thu hoạch", "Thị trường", "AI nông nghiệp"];

const articles = [
  {
    id: 1,
    title: "5 dấu hiệu thời tiết cần theo dõi trước khi thu hoạch",
    category: "Thời tiết",
    badge: "Dữ liệu thời gian thực",
    readTime: "5 phút đọc",
    date: "Hôm nay",
    description:
      "Cách đọc nhanh lượng mưa, độ ẩm, gió và nhiệt độ để quyết định lịch tưới, phun thuốc hoặc thu hoạch.",
    action: "/weather",
    actionLabel: "Xem thời tiết",
  },
  {
    id: 2,
    title: "Khi nào nên bán nông sản? Cách đọc xu hướng giá đơn giản",
    category: "Giá nông sản",
    badge: "Định giá AI",
    readTime: "7 phút đọc",
    date: "Mới cập nhật",
    description:
      "Hướng dẫn dùng biến động giá, chênh lệch vùng miền và dữ liệu lịch sử để ra quyết định bán phù hợp hơn.",
    action: "/pricing",
    actionLabel: "Xem giá",
  },
  {
    id: 3,
    title: "Checklist chuẩn bị thu hoạch cho nông hộ nhỏ",
    category: "Thu hoạch",
    badge: "Gợi ý mùa vụ",
    readTime: "4 phút đọc",
    date: "Tuần này",
    description:
      "Danh sách việc cần chuẩn bị: nhân công, phương tiện, bao bì, kiểm tra chất lượng và cập nhật giá thị trường.",
    action: "/harvest",
    actionLabel: "Dự báo thu hoạch",
  },
  {
    id: 4,
    title: "So sánh kênh bán: thương lái, chợ đầu mối, sàn TMĐT và doanh nghiệp thu mua",
    category: "Thị trường",
    badge: "Thông tin thị trường",
    readTime: "8 phút đọc",
    date: "Nổi bật",
    description:
      "Phân tích ưu nhược điểm từng kênh bán để chọn chiến lược tiêu thụ phù hợp theo sản lượng và chất lượng nông sản.",
    action: "/market",
    actionLabel: "Xem thị trường",
  },
  {
    id: 5,
    title: "Cách đặt câu hỏi để AI tư vấn nông nghiệp chính xác hơn",
    category: "AI nông nghiệp",
    badge: "Trợ lý AI",
    readTime: "3 phút đọc",
    date: "Gợi ý",
    description:
      "Mẫu câu hỏi nên dùng khi hỏi AI về thời tiết, giá nông sản, bệnh cây, lịch thu hoạch và chiến lược bán hàng.",
    action: "/ai-chat",
    actionLabel: "Hỏi AI",
  },
];

const quickGuides = [
  "Không phun thuốc khi xác suất mưa cao trong 6-12 giờ tới.",
  "So sánh giá theo vùng trước khi quyết định bán toàn bộ sản lượng.",
  "Theo dõi lịch thu hoạch kết hợp thời tiết để giảm rủi ro sau thu hoạch.",
];

export default function ArticlesPage() {
  const [selectedCategory, setSelectedCategory] = useState("Tất cả");
  const [keyword, setKeyword] = useState("");

  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      const matchCategory = selectedCategory === "Tất cả" || article.category === selectedCategory;
      const matchKeyword = `${article.title} ${article.description} ${article.category}`
        .toLowerCase()
        .includes(keyword.trim().toLowerCase());
      return matchCategory && matchKeyword;
    });
  }, [keyword, selectedCategory]);

  const featuredArticle = articles[0];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AgriNavbar />
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-green-800 to-lime-700 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.22),transparent_32%),radial-gradient(circle_at_bottom_left,rgba(132,204,22,0.25),transparent_35%)]" />
        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
            <div>
              <span className="inline-flex rounded-full border border-white/25 bg-white/10 px-4 py-2 text-sm font-semibold backdrop-blur">
                🌱 Kiến thức nông nghiệp thông minh
              </span>
              <h1 className="mt-6 max-w-3xl text-4xl font-black tracking-tight sm:text-5xl">
                Bài viết, hướng dẫn và mẹo vận hành cho nông dân số
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-8 text-emerald-50 sm:text-lg">
                Tổng hợp nội dung thực tế về thời tiết, giá nông sản, thu hoạch, thị trường và cách dùng AI để ra quyết định nhanh hơn.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/ai-chat" className="rounded-2xl bg-white px-5 py-3 font-bold text-emerald-800 shadow-lg shadow-black/10 transition hover:-translate-y-0.5 hover:bg-emerald-50">
                  Hỏi AI ngay
                </Link>
                <Link to="/market" className="rounded-2xl border border-white/30 px-5 py-3 font-bold text-white transition hover:bg-white/10">
                  Xem thị trường
                </Link>
              </div>
            </div>

            <div className="rounded-[2rem] border border-white/20 bg-white/12 p-5 shadow-2xl backdrop-blur">
              <div className="rounded-[1.5rem] bg-white p-6 text-slate-900">
                <div className="mb-4 flex items-center justify-between gap-4">
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700">
                    {featuredArticle.badge}
                  </span>
                  <span className="text-sm text-slate-500">{featuredArticle.readTime}</span>
                </div>
                <h2 className="text-2xl font-black leading-snug">{featuredArticle.title}</h2>
                <p className="mt-3 text-slate-600">{featuredArticle.description}</p>
                <div className="mt-6 grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-2xl bg-emerald-50 p-3">
                    <p className="text-2xl font-black text-emerald-700">24/7</p>
                    <p className="text-xs text-slate-500">AI hỗ trợ</p>
                  </div>
                  <div className="rounded-2xl bg-lime-50 p-3">
                    <p className="text-2xl font-black text-lime-700">5</p>
                    <p className="text-xs text-slate-500">chủ đề</p>
                  </div>
                  <div className="rounded-2xl bg-amber-50 p-3">
                    <p className="text-2xl font-black text-amber-700">Dữ liệu</p>
                    <p className="text-xs text-slate-500">có thể tích hợp</p>
                  </div>
                </div>
                <Link to={featuredArticle.action} className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-emerald-600 px-4 py-3 font-bold text-white transition hover:bg-emerald-700">
                  {featuredArticle.actionLabel}
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-center">
            <div className="relative">
              <input
                value={keyword}
                onChange={(event) => setKeyword(event.target.value)}
                placeholder="Tìm bài viết về thời tiết, giá, thu hoạch, thị trường..."
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 font-medium outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category}
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

        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
          <div className="grid gap-5 md:grid-cols-2">
            {filteredArticles.map((article) => (
              <article key={article.id} className="group rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-emerald-200 hover:shadow-xl hover:shadow-emerald-900/5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">{article.category}</span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-500">{article.badge}</span>
                  <span className="ml-auto text-xs font-semibold text-slate-400">{article.date}</span>
                </div>
                <h3 className="mt-5 text-xl font-black leading-snug text-slate-900 group-hover:text-emerald-700">{article.title}</h3>
                <p className="mt-3 leading-7 text-slate-600">{article.description}</p>
                <div className="mt-6 flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-slate-400">{article.readTime}</span>
                  <Link to={article.action} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-emerald-700">
                    {article.actionLabel}
                  </Link>
                </div>
              </article>
            ))}
          </div>

          <aside className="space-y-5">
            <div className="rounded-[2rem] border border-emerald-100 bg-emerald-50 p-6">
              <p className="text-sm font-black uppercase tracking-wide text-emerald-700">Gợi ý nhanh</p>
              <h3 className="mt-2 text-2xl font-black text-slate-900">Nên đưa vào trang này</h3>
              <div className="mt-5 space-y-3">
                {quickGuides.map((guide) => (
                  <div key={guide} className="rounded-2xl bg-white p-4 text-sm font-medium leading-6 text-slate-700 shadow-sm">
                    ✅ {guide}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-xl font-black">Nguồn nội dung nên nâng cấp</h3>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                <li>• Tin tức thị trường: lấy từ nguồn tin nông nghiệp đáng tin cậy.</li>
                <li>• Bài hướng dẫn: lưu trong hệ thống để quản trị viên quản lý.</li>
                <li>• Bài gợi ý AI: sinh tóm tắt theo dữ liệu thời tiết/giá.</li>
              </ul>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
