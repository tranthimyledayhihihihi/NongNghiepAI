import { Check, HelpCircle, ShieldCheck, Sparkles, Users } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';

const plans = [
  {
    name: 'Cơ bản',
    monthly: 0,
    yearly: 0,
    description: 'Phù hợp để trải nghiệm các nghiệp vụ chính trên một trang trại nhỏ.',
    badge: 'Bắt đầu nhanh',
    features: ['1 khu canh tác', 'Tra cứu giá cơ bản', '5 lượt kiểm định ảnh/tháng', 'Thông báo trong ứng dụng'],
  },
  {
    name: 'Nông trại',
    monthly: 249000,
    yearly: 2490000,
    description: 'Dành cho hộ sản xuất cần theo dõi mùa vụ, chất lượng và cảnh báo thường xuyên.',
    badge: 'Phổ biến',
    highlighted: true,
    features: [
      '10 khu canh tác',
      'Dự báo giá và thu hoạch',
      '200 lượt kiểm định ảnh/tháng',
      'Cảnh báo qua email/Zalo',
      'Báo cáo mùa vụ định kỳ',
    ],
  },
  {
    name: 'Hợp tác xã',
    monthly: 990000,
    yearly: 9900000,
    description: 'Cho đội vận hành nhiều vùng trồng, nhiều người dùng và nhu cầu báo cáo tổng hợp.',
    badge: 'Mở rộng',
    features: [
      'Không giới hạn khu canh tác',
      'Quản lý thành viên',
      'API tích hợp dữ liệu',
      'Dashboard tổng hợp vùng trồng',
      'Hỗ trợ ưu tiên',
    ],
  },
];

const faqs = [
  {
    question: 'Bảng giá này đã kết nối thanh toán chưa?',
    answer: 'Chưa. Đây là phần FE hoàn chỉnh để hiển thị gói dịch vụ; BE billing/payment có thể nối sau.',
  },
  {
    question: 'Có thể đổi gói sau khi dùng thử không?',
    answer: 'Có. Luồng đổi gói sẽ được xử lý khi có API tài khoản và thanh toán.',
  },
  {
    question: 'Dữ liệu cảnh báo qua Zalo lấy từ đâu?',
    answer: 'FE đã chuẩn bị luồng hiển thị. BE cần cung cấp cấu hình kênh nhận và trạng thái gửi thông báo.',
  },
];

const formatPrice = (value) => {
  if (value === 0) return 'Miễn phí';
  return new Intl.NumberFormat('vi-VN').format(value);
};

const SubscriptionPricingPage = () => {
  const [billingCycle, setBillingCycle] = useState('monthly');

  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main>
        <section className="bg-gray-50 py-16">
          <div className="mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
            <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Bảng giá</p>
            <h1 className="mx-auto mt-3 max-w-3xl text-4xl font-bold text-gray-900">
              Chọn gói phù hợp với quy mô canh tác
            </h1>
            <p className="mx-auto mt-4 max-w-2xl leading-7 text-gray-600">
              Các gói dưới đây phục vụ phần đăng ký và nâng cấp phía FE. Khi BE sẵn sàng, form có thể nối
              vào auth, subscription và payment API.
            </p>

            <div className="mt-8 inline-flex rounded-lg border border-gray-300 bg-white p-1">
              <button
                type="button"
                onClick={() => setBillingCycle('monthly')}
                className={`rounded-md px-5 py-2 text-sm font-semibold ${
                  billingCycle === 'monthly' ? 'bg-green-700 text-white' : 'text-gray-700'
                }`}
              >
                Theo tháng
              </button>
              <button
                type="button"
                onClick={() => setBillingCycle('yearly')}
                className={`rounded-md px-5 py-2 text-sm font-semibold ${
                  billingCycle === 'yearly' ? 'bg-green-700 text-white' : 'text-gray-700'
                }`}
              >
                Theo năm
              </button>
            </div>
          </div>
        </section>

        <section className="py-12">
          <div className="mx-auto grid max-w-7xl gap-6 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">
            {plans.map((plan) => {
              const price = billingCycle === 'monthly' ? plan.monthly : plan.yearly;
              return (
                <article
                  key={plan.name}
                  className={`rounded-lg border p-6 shadow-sm ${
                    plan.highlighted ? 'border-green-700 bg-green-50' : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{plan.name}</h2>
                      <p className="mt-2 text-sm leading-6 text-gray-600">{plan.description}</p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        plan.highlighted ? 'bg-green-700 text-white' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {plan.badge}
                    </span>
                  </div>

                  <div className="mt-6">
                    <div className="flex items-end gap-2">
                      <span className="text-4xl font-bold text-gray-900">{formatPrice(price)}</span>
                      {price > 0 && (
                        <span className="pb-1 text-sm text-gray-600">
                          đ/{billingCycle === 'monthly' ? 'tháng' : 'năm'}
                        </span>
                      )}
                    </div>
                    {billingCycle === 'yearly' && price > 0 && (
                      <p className="mt-2 text-sm font-medium text-green-700">Tiết kiệm khoảng 2 tháng phí.</p>
                    )}
                  </div>

                  <div className="mt-6 space-y-3">
                    {plan.features.map((feature) => (
                      <div key={feature} className="flex items-start gap-3 text-sm text-gray-700">
                        <Check className="mt-0.5 h-4 w-4 text-green-700" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Link
                    to={plan.monthly === 0 ? '/register' : '/contact'}
                    className={`mt-8 block rounded-lg px-5 py-3 text-center font-semibold ${
                      plan.highlighted
                        ? 'bg-green-700 text-white hover:bg-green-800'
                        : 'border border-gray-300 text-gray-800 hover:bg-gray-50'
                    }`}
                  >
                    {plan.monthly === 0 ? 'Dùng thử' : 'Tư vấn gói này'}
                  </Link>
                </article>
              );
            })}
          </div>
        </section>

        <section className="bg-gray-50 py-14">
          <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Bao gồm trong mọi gói</p>
              <h2 className="mt-2 text-3xl font-bold text-gray-900">Nền tảng vận hành ổn định trước khi mở rộng BE</h2>
              <div className="mt-6 grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                <div className="rounded-lg border border-gray-200 bg-white p-4">
                  <Sparkles className="mb-3 h-5 w-5 text-green-700" />
                  <h3 className="font-semibold text-gray-900">Giao diện AI-first</h3>
                  <p className="mt-1 text-sm text-gray-600">Các màn hình đã chuẩn bị vị trí cho dự báo và gợi ý AI.</p>
                </div>
                <div className="rounded-lg border border-gray-200 bg-white p-4">
                  <Users className="mb-3 h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">Sẵn sàng phân quyền</h3>
                  <p className="mt-1 text-sm text-gray-600">Có thể nối user, role và team khi BE hoàn thiện auth.</p>
                </div>
                <div className="rounded-lg border border-gray-200 bg-white p-4">
                  <ShieldCheck className="mb-3 h-5 w-5 text-amber-600" />
                  <h3 className="font-semibold text-gray-900">Theo dõi cảnh báo</h3>
                  <p className="mt-1 text-sm text-gray-600">Luồng thông báo và cài đặt kênh nhận đã có ở FE.</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {faqs.map((faq) => (
                <div key={faq.question} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                  <div className="flex gap-3">
                    <HelpCircle className="mt-0.5 h-5 w-5 text-green-700" />
                    <div>
                      <h3 className="font-bold text-gray-900">{faq.question}</h3>
                      <p className="mt-2 text-sm leading-6 text-gray-600">{faq.answer}</p>
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

export default SubscriptionPricingPage;
