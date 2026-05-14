import { Clock, Mail, MapPin, MessageCircle, Phone, Send } from 'lucide-react';
import { useState } from 'react';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';

const contactChannels = [
  {
    icon: Phone,
    title: 'Hotline',
    value: '1900 888 168',
    description: 'Tư vấn gói dịch vụ và hỗ trợ vận hành trong giờ hành chính.',
  },
  {
    icon: Mail,
    title: 'Email',
    value: 'support@agriai.vn',
    description: 'Gửi yêu cầu tích hợp, phản hồi lỗi hoặc đề xuất tính năng.',
  },
  {
    icon: MessageCircle,
    title: 'Zalo OA',
    value: 'AgriAI Việt Nam',
    description: 'Kênh phù hợp cho thông báo giá, thời tiết và nhắc việc mùa vụ.',
  },
];

const ContactPage = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    email: '',
    topic: 'Tư vấn triển khai',
    message: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main>
        <section className="relative isolate overflow-hidden bg-gray-950">
          <img
            src="https://images.unsplash.com/photo-1495107334309-fcf20504a5ab?auto=format&fit=crop&w=1800&q=85"
            alt="Cánh đồng nông nghiệp"
            className="absolute inset-0 -z-10 h-full w-full object-cover opacity-55"
          />
          <div className="absolute inset-0 -z-10 bg-gray-950/40" />
          <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
            <div className="max-w-3xl text-white">
              <p className="text-sm font-semibold uppercase tracking-wide text-green-200">Liên hệ</p>
              <h1 className="mt-3 text-4xl font-bold md:text-5xl">Trao đổi về nhu cầu triển khai AgriAI</h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-gray-100">
                Gửi thông tin trang trại, hợp tác xã hoặc bài toán tích hợp. FE sẽ ghi nhận form ngay bây giờ,
                BE có thể bổ sung API gửi yêu cầu sau.
              </p>
            </div>
          </div>
        </section>

        <section className="py-14">
          <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:px-6 lg:grid-cols-[0.95fr_1.05fr] lg:px-8">
            <div>
              <div className="grid gap-4">
                {contactChannels.map((channel) => {
                  const Icon = channel.icon;
                  return (
                    <div key={channel.title} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                      <div className="flex gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-green-50 text-green-700">
                          <Icon className="h-6 w-6" />
                        </div>
                        <div>
                          <h2 className="font-bold text-gray-900">{channel.title}</h2>
                          <p className="mt-1 font-semibold text-green-700">{channel.value}</p>
                          <p className="mt-2 text-sm leading-6 text-gray-600">{channel.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-5">
                <div className="flex gap-4">
                  <Clock className="h-6 w-6 text-amber-600" />
                  <div>
                    <h2 className="font-bold text-gray-900">Thời gian phản hồi</h2>
                    <p className="mt-2 text-sm leading-6 text-gray-600">
                      Yêu cầu tư vấn thường được phản hồi trong 1 ngày làm việc. Các yêu cầu lỗi hệ thống sẽ được
                      ưu tiên theo mức ảnh hưởng vận hành.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 rounded-lg border border-gray-200 p-5">
                <div className="flex gap-4">
                  <MapPin className="h-6 w-6 text-blue-600" />
                  <div>
                    <h2 className="font-bold text-gray-900">Khu vực hỗ trợ</h2>
                    <p className="mt-2 text-sm leading-6 text-gray-600">
                      Ưu tiên triển khai dữ liệu thử nghiệm cho Đồng bằng sông Cửu Long, Tây Nguyên và các vùng rau
                      màu quanh đô thị lớn.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-bold text-gray-900">Gửi yêu cầu</h2>
              <p className="mt-2 text-sm text-gray-600">Các trường này đang xử lý ở FE, chưa gửi về server.</p>

              {submitted && (
                <div className="mt-5 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                  Đã ghi nhận yêu cầu của {formData.fullName || 'bạn'} trên giao diện FE.
                </div>
              )}

              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Họ và tên</label>
                  <input
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                    placeholder="Nguyễn Văn An"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Số điện thoại</label>
                  <input
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                    placeholder="0912 345 678"
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="mb-2 block text-sm font-medium text-gray-700">Email</label>
                <input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                  placeholder="email@example.com"
                />
              </div>

              <div className="mt-4">
                <label className="mb-2 block text-sm font-medium text-gray-700">Chủ đề</label>
                <select
                  name="topic"
                  value={formData.topic}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                >
                  <option>Tư vấn triển khai</option>
                  <option>Hỗ trợ kỹ thuật</option>
                  <option>Tích hợp API</option>
                  <option>Góp ý sản phẩm</option>
                </select>
              </div>

              <div className="mt-4">
                <label className="mb-2 block text-sm font-medium text-gray-700">Nội dung</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={6}
                  className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                  placeholder="Mô tả quy mô trang trại, cây trồng, khu vực và nhu cầu chính..."
                />
              </div>

              <button
                type="submit"
                className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800"
              >
                <Send className="h-5 w-5" />
                Gửi yêu cầu
              </button>
            </form>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
};

export default ContactPage;
