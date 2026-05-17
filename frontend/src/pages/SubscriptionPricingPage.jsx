import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AgriNavbar from "../components/AgriNavbar";

const plans = [
  {
    name: "Miễn phí",
    audience: "Nông hộ mới dùng thử",
    monthly: 0,
    yearly: 0,
    description: "Phù hợp để trải nghiệm các tính năng cơ bản của hệ thống.",
    features: ["Xem thời tiết cơ bản", "Tra cứu giá mẫu", "5 lượt hỏi AI/ngày", "Bài viết hướng dẫn", "Lưu 1 mùa vụ"],
    cta: "Bắt đầu miễn phí",
    route: "/ai-chat",
  },
  {
    name: "Nhà nông Pro",
    audience: "Nông dân cá nhân",
    monthly: 99000,
    yearly: 990000,
    popular: true,
    description: "Gói cân bằng giữa chi phí và khả năng hỗ trợ ra quyết định hằng ngày.",
    features: ["Dự báo thời tiết nông nghiệp 7 ngày", "Cảnh báo mưa, gió, độ ẩm", "Dự báo ngày thu hoạch", "AI tư vấn không giới hạn hợp lý", "Theo dõi giá theo khu vực", "Tạo cảnh báo giá"],
    cta: "Chọn gói Pro",
    route: "/contact",
  },
  {
    name: "Hợp tác xã",
    audience: "Nhóm hộ và HTX",
    monthly: 299000,
    yearly: 2990000,
    description: "Quản lý nhiều mùa vụ, nhiều khu vực và hỗ trợ ra quyết định theo nhóm.",
    features: ["Quản lý nhiều nông hộ", "Báo cáo mùa vụ", "So sánh giá vùng miền", "Gợi ý kênh bán hàng", "Lịch nhắc công việc", "Xuất báo cáo PDF/Excel"],
    cta: "Tư vấn gói HTX",
    route: "/contact",
  },
  {
    name: "Doanh nghiệp",
    audience: "Đơn vị thu mua / phân phối",
    monthly: null,
    yearly: null,
    description: "Tùy chỉnh API, dashboard và tích hợp dữ liệu theo quy trình doanh nghiệp.",
    features: ["Dashboard tùy chỉnh", "Tích hợp API nội bộ", "Theo dõi vùng nguyên liệu", "Phân quyền tài khoản", "Hỗ trợ kỹ thuật ưu tiên", "Tư vấn triển khai riêng"],
    cta: "Liên hệ triển khai",
    route: "/contact",
  },
];

const comparisonRows = [
  ["Thời tiết realtime", "Cơ bản", "Nâng cao", "Nâng cao", "Tùy chỉnh"],
  ["Dự báo thu hoạch", "1 mùa vụ", "Không giới hạn hợp lý", "Nhiều mùa vụ", "Theo vùng nguyên liệu"],
  ["Giá nông sản", "Dữ liệu mẫu", "Theo khu vực", "So sánh vùng miền", "API riêng"],
  ["AI Chat", "5 lượt/ngày", "Ưu tiên", "Ưu tiên nhóm", "Tùy chỉnh tri thức"],
  ["Báo cáo", "Không", "Cơ bản", "PDF/Excel", "Theo yêu cầu"],
];

const formatPrice = (price) => {
  if (price === null) return "Liên hệ";
  if (price === 0) return "0đ";
  return new Intl.NumberFormat("vi-VN").format(price) + "đ";
};

export default function SubscriptionPricingPage() {
  const [billing, setBilling] = useState("monthly");

  const billingText = useMemo(() => (billing === "monthly" ? "/tháng" : "/năm"), [billing]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <AgriNavbar />
      <section className="overflow-hidden bg-gradient-to-br from-slate-950 via-emerald-950 to-green-800 text-white">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-bold text-emerald-50">
              💳 Gói dịch vụ AgriAI
            </span>
            <h1 className="mt-6 text-4xl font-black tracking-tight sm:text-5xl">
              Chọn gói phù hợp với quy mô sản xuất của bạn
            </h1>
            <p className="mt-5 text-lg leading-8 text-emerald-50">
              Trang pricing nên thể hiện rõ giá trị của hệ thống: thời tiết realtime, dự báo thu hoạch, định giá nông sản, thị trường và AI tư vấn.
            </p>

            <div className="mt-8 inline-flex rounded-2xl border border-white/15 bg-white/10 p-1 backdrop-blur">
              <button
                onClick={() => setBilling("monthly")}
                className={`rounded-xl px-5 py-3 font-bold transition ${billing === "monthly" ? "bg-white text-emerald-800" : "text-white hover:bg-white/10"}`}
              >
                Theo tháng
              </button>
              <button
                onClick={() => setBilling("yearly")}
                className={`rounded-xl px-5 py-3 font-bold transition ${billing === "yearly" ? "bg-white text-emerald-800" : "text-white hover:bg-white/10"}`}
              >
                Theo năm <span className="ml-1 rounded-full bg-lime-300 px-2 py-0.5 text-xs text-lime-950">tiết kiệm</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-4">
          {plans.map((plan) => {
            const price = plan[billing];
            return (
              <article
                key={plan.name}
                className={`relative flex flex-col rounded-[2rem] border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl ${
                  plan.popular ? "border-emerald-400 ring-4 ring-emerald-100" : "border-slate-200"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-emerald-600 px-4 py-2 text-xs font-black text-white shadow-lg">
                    Đề xuất tốt nhất
                  </div>
                )}
                <div className="min-h-[155px]">
                  <p className="text-sm font-bold text-emerald-700">{plan.audience}</p>
                  <h2 className="mt-2 text-2xl font-black">{plan.name}</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{plan.description}</p>
                </div>

                <div className="mt-5 rounded-2xl bg-slate-50 p-4">
                  <p className="text-3xl font-black text-slate-950">
                    {formatPrice(price)}
                    {price !== null && price !== 0 && <span className="text-sm font-bold text-slate-500"> {billingText}</span>}
                  </p>
                </div>

                <ul className="mt-6 flex-1 space-y-3 text-sm leading-6 text-slate-700">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex gap-2">
                      <span className="mt-0.5 text-emerald-600">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  to={plan.route}
                  className={`mt-7 inline-flex items-center justify-center rounded-2xl px-4 py-3 font-black transition ${
                    plan.popular ? "bg-emerald-600 text-white hover:bg-emerald-700" : "bg-slate-900 text-white hover:bg-emerald-700"
                  }`}
                >
                  {plan.cta}
                </Link>
              </article>
            );
          })}
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="rounded-[2rem] border border-emerald-100 bg-emerald-50 p-6">
            <p className="text-sm font-black uppercase tracking-wide text-emerald-700">Nâng cấp tính năng</p>
            <h2 className="mt-2 text-3xl font-black">Nên làm thêm để trang pricing chuyên nghiệp hơn</h2>
            <div className="mt-6 space-y-4">
              <div className="rounded-2xl bg-white p-4 shadow-sm">
                <h3 className="font-black">Tính giá theo nhu cầu</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">Cho người dùng chọn diện tích, số mùa vụ, số cảnh báo, số tài khoản để hệ thống gợi ý gói phù hợp.</p>
              </div>
              <div className="rounded-2xl bg-white p-4 shadow-sm">
                <h3 className="font-black">Liên kết thanh toán sau</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">Hiện tại có thể để nút liên hệ. Sau này có thể nối VNPay, Momo hoặc quản lý subscription trong DB.</p>
              </div>
              <div className="rounded-2xl bg-white p-4 shadow-sm">
                <h3 className="font-black">Phân quyền theo gói</h3>
                <p className="mt-1 text-sm leading-6 text-slate-600">Ẩn/hiện tính năng AI, cảnh báo giá, báo cáo và số mùa vụ theo plan của tài khoản.</p>
              </div>
            </div>
          </div>

          <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-6">
              <h2 className="text-2xl font-black">So sánh tính năng</h2>
              <p className="mt-2 text-slate-600">Bảng này giúp người dùng hiểu rõ vì sao nên nâng cấp gói.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-slate-50 text-slate-500">
                  <tr>
                    <th className="p-4 font-black">Tính năng</th>
                    {plans.map((plan) => (
                      <th key={plan.name} className="p-4 font-black">{plan.name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparisonRows.map((row) => (
                    <tr key={row[0]} className="border-t border-slate-100">
                      {row.map((cell, index) => (
                        <td key={`${row[0]}-${index}`} className={`p-4 ${index === 0 ? "font-bold text-slate-900" : "text-slate-600"}`}>
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="mt-12 rounded-[2rem] bg-slate-900 p-8 text-white lg:flex lg:items-center lg:justify-between">
          <div>
            <h2 className="text-3xl font-black">Chưa biết chọn gói nào?</h2>
            <p className="mt-2 max-w-2xl text-slate-300">Hãy để AI hoặc đội hỗ trợ tư vấn theo loại cây trồng, diện tích, khu vực và nhu cầu cảnh báo.</p>
          </div>
          <div className="mt-6 flex flex-wrap gap-3 lg:mt-0">
            <Link to="/ai-chat" className="rounded-2xl bg-white px-5 py-3 font-black text-slate-900 hover:bg-emerald-50">Hỏi AI tư vấn</Link>
            <Link to="/contact" className="rounded-2xl bg-emerald-600 px-5 py-3 font-black text-white hover:bg-emerald-700">Liên hệ hỗ trợ</Link>
          </div>
        </div>
      </section>
    </main>
  );
}
