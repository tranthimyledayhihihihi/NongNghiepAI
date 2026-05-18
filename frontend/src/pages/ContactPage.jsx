import React, { useState } from "react";
import { Link } from "react-router-dom";
import AgriNavbar from "../components/AgriNavbar";

const supportChannels = [
  {
    title: "Tư vấn sử dụng hệ thống",
    value: "support@agriai.vn",
    description: "Hỏi về tài khoản, gói dịch vụ, bảng điều khiển và cách dùng AI.",
    icon: "💬",
  },
  {
    title: "Hỗ trợ kỹ thuật",
    value: "tech@agriai.vn",
    description: "Báo lỗi hệ thống, dữ liệu thời tiết, giá nông sản hoặc cảnh báo.",
    icon: "🛠️",
  },
  {
    title: "Hợp tác dữ liệu",
    value: "partner@agriai.vn",
    description: "Kết nối nguồn giá, tin tức thị trường, vùng nguyên liệu và doanh nghiệp thu mua.",
    icon: "🤝",
  },
];

const topics = [
  "Tư vấn gói dịch vụ",
  "Báo lỗi hệ thống",
  "Kết nối nguồn dữ liệu",
  "Triển khai cho hợp tác xã",
  "Góp ý giao diện / tính năng",
];

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    topic: topics[0],
    region: "",
    message: "",
  });

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // Có thể thay bằng lời gọi hệ thống thật: await contactApi.createMessage(form)
    setSubmitted(true);
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AgriNavbar />
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-green-800 to-lime-700 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.18),transparent_30%),radial-gradient(circle_at_80%_10%,rgba(132,204,22,0.22),transparent_35%)]" />
        <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-10 lg:grid-cols-[1fr_420px] lg:items-center">
            <div>
              <span className="inline-flex rounded-full border border-white/25 bg-white/10 px-4 py-2 text-sm font-bold backdrop-blur">
                📞 Trung tâm hỗ trợ AgriAI
              </span>
              <h1 className="mt-6 text-4xl font-black tracking-tight sm:text-5xl">
                Liên hệ để được hỗ trợ về AI nông nghiệp, dữ liệu và triển khai hệ thống
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-emerald-50">
                Trang liên hệ giúp người dùng gửi yêu cầu nhanh, chọn đúng nhóm hỗ trợ và đi tiếp sang các tính năng chính như Trợ lý AI, thời tiết, giá nông sản hoặc gói dịch vụ.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Link to="/ai-chat" className="rounded-2xl bg-white px-5 py-3 font-black text-emerald-800 shadow-lg shadow-black/10 hover:bg-emerald-50">
                  Hỏi AI trước
                </Link>
                <Link to="/pricing-plans" className="rounded-2xl border border-white/30 px-5 py-3 font-black text-white hover:bg-white/10">
                  Xem gói dịch vụ
                </Link>
              </div>
            </div>

            <div className="rounded-[2rem] border border-white/20 bg-white/10 p-5 shadow-2xl backdrop-blur">
              <div className="rounded-[1.5rem] bg-white p-6 text-slate-900">
                <p className="text-sm font-black uppercase tracking-wide text-emerald-700">Cam kết hỗ trợ</p>
                <div className="mt-5 grid gap-3">
                  <div className="rounded-2xl bg-emerald-50 p-4">
                    <p className="text-2xl font-black text-emerald-700">24h</p>
                    <p className="text-sm text-slate-600">phản hồi yêu cầu thông thường</p>
                  </div>
                  <div className="rounded-2xl bg-lime-50 p-4">
                    <p className="text-2xl font-black text-lime-700">3 nhóm</p>
                    <p className="text-sm text-slate-600">hỗ trợ: sử dụng, kỹ thuật, hợp tác dữ liệu</p>
                  </div>
                  <div className="rounded-2xl bg-amber-50 p-4">
                    <p className="text-2xl font-black text-amber-700">Sẵn sàng tích hợp</p>
                    <p className="text-sm text-slate-600">có thể lưu yêu cầu vào hệ thống và gửi Email/Zalo</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-3">
          {supportChannels.map((channel) => (
            <div key={channel.title} className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-emerald-200 hover:shadow-xl hover:shadow-emerald-900/5">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-2xl">{channel.icon}</div>
              <h2 className="mt-5 text-xl font-black">{channel.title}</h2>
              <p className="mt-2 font-bold text-emerald-700">{channel.value}</p>
              <p className="mt-3 leading-7 text-slate-600">{channel.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-10 grid gap-8 lg:grid-cols-[1fr_0.85fr]">
          <form onSubmit={handleSubmit} className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="mb-7">
              <p className="text-sm font-black uppercase tracking-wide text-emerald-700">Gửi yêu cầu hỗ trợ</p>
              <h2 className="mt-2 text-3xl font-black">Chúng tôi có thể giúp gì cho bạn?</h2>
              <p className="mt-2 text-slate-600">Biểu mẫu này có thể kết nối hệ thống để lưu yêu cầu và gửi thông báo qua Email/Zalo.</p>
            </div>

            {submitted && (
              <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-bold text-emerald-700">
                Đã ghi nhận yêu cầu mẫu. Khi kết nối hệ thống thật, nội dung này sẽ được lưu lại và gửi cho đội hỗ trợ.
              </div>
            )}

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm font-bold text-slate-700">Họ tên</span>
                <input
                  value={form.name}
                  onChange={(event) => updateField("name", event.target.value)}
                  required
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                  placeholder="Nguyễn Văn A"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm font-bold text-slate-700">Số điện thoại</span>
                <input
                  value={form.phone}
                  onChange={(event) => updateField("phone", event.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                  placeholder="09xx xxx xxx"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm font-bold text-slate-700">Email</span>
                <input
                  type="email"
                  value={form.email}
                  onChange={(event) => updateField("email", event.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                  placeholder="email@example.com"
                />
              </label>
              <label className="space-y-2">
                <span className="text-sm font-bold text-slate-700">Khu vực</span>
                <input
                  value={form.region}
                  onChange={(event) => updateField("region", event.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                  placeholder="VD: Đà Lạt, Lâm Đồng"
                />
              </label>
              <label className="space-y-2 sm:col-span-2">
                <span className="text-sm font-bold text-slate-700">Chủ đề</span>
                <select
                  value={form.topic}
                  onChange={(event) => updateField("topic", event.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                >
                  {topics.map((topic) => (
                    <option key={topic}>{topic}</option>
                  ))}
                </select>
              </label>
              <label className="space-y-2 sm:col-span-2">
                <span className="text-sm font-bold text-slate-700">Nội dung</span>
                <textarea
                  value={form.message}
                  onChange={(event) => updateField("message", event.target.value)}
                  required
                  rows={5}
                  className="w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100"
                  placeholder="Mô tả nhu cầu, lỗi gặp phải hoặc tính năng muốn được tư vấn..."
                />
              </label>
            </div>

            <button type="submit" className="mt-6 w-full rounded-2xl bg-emerald-600 px-5 py-4 font-black text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700">
              Gửi yêu cầu hỗ trợ
            </button>
          </form>

          <aside className="space-y-6">
            <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-black">Đi nhanh đến tính năng liên quan</h2>
              <div className="mt-5 grid gap-3">
                <Link to="/weather" className="rounded-2xl bg-slate-50 p-4 font-bold text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-700">🌦️ Kiểm tra thời tiết</Link>
                <Link to="/pricing" className="rounded-2xl bg-slate-50 p-4 font-bold text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-700">💰 Xem giá nông sản</Link>
                <Link to="/harvest" className="rounded-2xl bg-slate-50 p-4 font-bold text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-700">🌾 Dự báo thu hoạch</Link>
                <Link to="/market" className="rounded-2xl bg-slate-50 p-4 font-bold text-slate-700 transition hover:bg-emerald-50 hover:text-emerald-700">🛒 Chiến lược thị trường</Link>
              </div>
            </div>

            <div className="rounded-[2rem] border border-amber-200 bg-amber-50 p-6">
              <h2 className="text-2xl font-black">Nâng cấp hệ thống nên có</h2>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
                <li>• Lưu yêu cầu liên hệ vào hệ thống.</li>
                <li>• Gửi email/Zalo OA khi có yêu cầu mới.</li>
                <li>• Thêm trạng thái: mới, đang xử lý, đã xử lý.</li>
                <li>• Cho quản trị viên xem và phản hồi trong bảng điều khiển.</li>
              </ul>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
