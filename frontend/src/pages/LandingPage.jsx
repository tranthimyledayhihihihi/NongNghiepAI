import {
  ChevronRight,
  FileText,
  Leaf,
  Menu,
  Shield,
  Sprout,
  TrendingUp,
  X
} from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: <Sprout className="w-8 h-8 text-green-600" />,
      title: "Dự báo Thu hoạch",
      description: "Sử dụng AI để dự đoán năng suất và thời điểm thu hoạch tối ưu dựa trên dữ liệu thời tiết và lịch sử canh tác."
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-green-600" />,
      title: "Định giá Thông minh",
      description: "Phân tích thị trường theo thời gian thực và đưa ra giá bán tối ưu cho từng loại nông sản."
    },
    {
      icon: <Shield className="w-8 h-8 text-green-600" />,
      title: "Kiểm tra Chất lượng",
      description: "Nhận diện bệnh hại và đánh giá chất lượng nông sản qua hình ảnh với độ chính xác cao."
    },
    {
      icon: <FileText className="w-8 h-8 text-green-600" />,
      title: "Chat với Trí tuệ nhân tạo (AI)",
      description: "Tư vấn nông nghiệp 24/7 với AI được huấn luyện từ kiến thức chuyên gia và dữ liệu canh tác."
    }
  ];

  const articles = [
    {
      image: "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400&h=300&fit=crop",
      title: "Kỹ thuật canh tác lúa mùa mưa",
      description: "Hướng dẫn chi tiết về kỹ thuật trồng và chăm sóc lúa trong mùa mưa để đạt năng suất cao nhất.",
      date: "15/04/2026"
    },
    {
      image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&h=300&fit=crop",
      title: "Phòng trừ sâu bệnh bằng Drone",
      description: "Công nghệ drone giúp phát hiện và xử lý sâu bệnh hiệu quả, tiết kiệm chi phí và thời gian.",
      date: "12/04/2026"
    }
  ];

  const stats = [
    { value: "5000+", label: "Nông dân sử dụng" },
    { value: "95%", label: "Độ chính xác AI" },
    { value: "20%", label: "Tăng năng suất TB" }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header/Navbar */}
      <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <Leaf className="w-8 h-8 text-green-700" />
              <span className="text-xl font-bold text-gray-900">AgriAI</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-700 hover:text-green-700 transition">
                Tính năng
              </a>
              <a href="#articles" className="text-gray-700 hover:text-green-700 transition">
                Bài viết
              </a>
              <a href="#pricing" className="text-gray-700 hover:text-green-700 transition">
                Bảng giá
              </a>
              <a href="#contact" className="text-gray-700 hover:text-green-700 transition">
                Liên hệ
              </a>
            </div>

            {/* CTA Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <button className="text-gray-700 hover:text-green-700 transition">
                Đăng nhập
              </button>
              <Link
                to="/dashboard"
                className="bg-green-700 text-white px-6 py-2 rounded-lg hover:bg-green-800 transition"
              >
                Bắt đầu ngay
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="w-6 h-6 text-gray-700" />
              ) : (
                <Menu className="w-6 h-6 text-gray-700" />
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <div className="flex flex-col space-y-4">
                <a href="#features" className="text-gray-700 hover:text-green-700 transition">
                  Tính năng
                </a>
                <a href="#articles" className="text-gray-700 hover:text-green-700 transition">
                  Bài viết
                </a>
                <a href="#pricing" className="text-gray-700 hover:text-green-700 transition">
                  Bảng giá
                </a>
                <a href="#contact" className="text-gray-700 hover:text-green-700 transition">
                  Liên hệ
                </a>
                <button className="text-left text-gray-700 hover:text-green-700 transition">
                  Đăng nhập
                </button>
                <Link
                  to="/dashboard"
                  className="bg-green-700 text-white px-6 py-2 rounded-lg hover:bg-green-800 transition text-center"
                >
                  Bắt đầu ngay
                </Link>
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Hero Section */}
      <section className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div>
              <div className="inline-block bg-green-50 text-green-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
                Nền tảng nông nghiệp AI
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Nông tâm Nông nghiệp Việt bằng Trí tuệ nhân tạo
              </h1>

              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Giải pháp AI toàn diện giúp nông dân tối ưu hóa sản xuất, dự báo năng suất,
                định giá thông minh và kiểm tra chất lượng nông sản một cách chính xác.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Link
                  to="/dashboard"
                  className="bg-green-700 text-white px-8 py-3 rounded-lg hover:bg-green-800 transition font-medium text-center"
                >
                  Bắt đầu ngay
                </Link>
                <button className="border-2 border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:border-green-700 hover:text-green-700 transition font-medium">
                  Xem demo miễn phí
                </button>
              </div>

              {/* Trust Badge */}
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full bg-green-200 border-2 border-white"></div>
                  <div className="w-8 h-8 rounded-full bg-green-300 border-2 border-white"></div>
                  <div className="w-8 h-8 rounded-full bg-green-400 border-2 border-white"></div>
                </div>
                <span>
                  <strong className="text-gray-900">95%</strong> nông dân hài lòng
                </span>
              </div>
            </div>

            {/* Right Image */}
            <div className="relative">
              <div className="rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&h=600&fit=crop"
                  alt="Rice Field"
                  className="w-full h-auto"
                />
              </div>
              {/* Floating Stats Card */}
              <div className="absolute bottom-4 right-4 bg-white rounded-xl shadow-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-green-700" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900">95%</div>
                    <div className="text-sm text-gray-600">Độ chính xác</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-green-700 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Giải pháp Nông nghiệp Hiện đại
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Chúng tôi mang đến những công cụ AI tiên tiến giúp nông dân tối ưu hóa
              quy trình canh tác và tăng năng suất.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-shadow"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Articles Section */}
      <section id="articles" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                Thư viện Kỹ thuật
              </h2>
              <p className="text-gray-600">
                Cập nhật kiến thức canh tác từ các chuyên gia
              </p>
            </div>
            <button className="text-green-700 font-medium flex items-center hover:text-green-800 transition">
              Xem tất cả <ChevronRight className="w-5 h-5 ml-1" />
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {articles.map((article, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
              >
                <div className="h-48 overflow-hidden">
                  <img
                    src={article.image}
                    alt={article.title}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <div className="p-6">
                  <div className="text-sm text-gray-500 mb-2">{article.date}</div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {article.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {article.description}
                  </p>
                  <button className="text-green-700 font-medium flex items-center hover:text-green-800 transition">
                    Đọc thêm <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-3xl p-12">
            <div className="mb-6">
              <svg className="w-12 h-12 text-green-700 mx-auto" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
              </svg>
            </div>
            <p className="text-xl md:text-2xl text-gray-800 mb-8 leading-relaxed">
              "Từ khi sử dụng AgriAI, tôi không còn phải thăm lo dự vé giờ có phải thôm lo
              nào nên bán với giá bao nhiêu. AI bác cho tôi biết chính xác lúc nào là tốt nhất
              khẩu nên tin."
            </p>
            <div className="flex items-center justify-center space-x-4">
              <img
                src="https://i.pravatar.cc/100?img=12"
                alt="Farmer"
                className="w-16 h-16 rounded-full border-4 border-white shadow-lg"
              />
              <div className="text-left">
                <div className="font-bold text-gray-900">Chú Sáu Hữu</div>
                <div className="text-gray-600">Nông dân tại Cần Thơ</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-700 to-green-900">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Sẵn sàng số hóa nông trại của bạn?
          </h2>
          <p className="text-lg text-green-100 mb-8 max-w-2xl mx-auto">
            Hãy tham gia cùng hơn 5,000+ nông dân đã tin tưởng sử dụng AgriAI để
            tối ưu hóa sản xuất và tăng thu nhập.
          </p>
          <Link
            to="/dashboard"
            className="inline-block bg-white text-green-700 px-8 py-4 rounded-lg hover:bg-green-50 transition font-medium text-lg"
          >
            Dùng thử miễn phí
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Company Info */}
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Leaf className="w-6 h-6 text-green-500" />
                <span className="text-xl font-bold text-white">AgriAI</span>
              </div>
              <p className="text-sm text-gray-400">
                Nền tảng nông nghiệp thông minh hàng đầu Việt Nam
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="font-bold text-white mb-4">Sản phẩm</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-green-500 transition">Dự báo thu hoạch</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Định giá thông minh</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Kiểm tra chất lượng</a></li>
                <li><a href="#" className="hover:text-green-500 transition">AI Chat</a></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-bold text-white mb-4">Về chúng tôi</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-green-500 transition">Giới thiệu</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Đội ngũ</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Tin tức</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Liên hệ</a></li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h4 className="font-bold text-white mb-4">Hỗ trợ</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-green-500 transition">Trung tâm trợ giúp</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Điều khoản</a></li>
                <li><a href="#" className="hover:text-green-500 transition">Chính sách</a></li>
                <li><a href="#" className="hover:text-green-500 transition">FAQ</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-400">
              © 2026 AgriAI. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-green-500 transition">
                <span className="sr-only">Facebook</span>
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
              </a>
              <a href="#" className="text-gray-400 hover:text-green-500 transition">
                <span className="sr-only">Twitter</span>
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
