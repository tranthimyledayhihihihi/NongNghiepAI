import { CalendarDays, ChevronRight, Search, Tag } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PublicFooter from '../components/PublicFooter';
import PublicHeader from '../components/PublicHeader';
import { useAuth } from '../contexts/AuthContext';

const categories = ['Tất cả', 'Canh tác', 'Thị trường', 'Sâu bệnh', 'Công nghệ'];

const articles = [
  {
    id: 1,
    title: 'Lập lịch chăm sóc lúa trong giai đoạn làm đòng',
    category: 'Canh tác',
    date: '02/05/2026',
    readTime: '6 phút đọc',
    image: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Các mốc kiểm tra nước, dinh dưỡng và sâu bệnh cần theo dõi để giảm rủi ro thất thoát năng suất.',
  },
  {
    id: 2,
    title: 'Cách đọc tín hiệu giá trước khi chốt bán nông sản',
    category: 'Thị trường',
    date: '28/04/2026',
    readTime: '5 phút đọc',
    image: 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Kết hợp giá vùng, tồn kho và nhu cầu thu mua để chọn thời điểm bán phù hợp thay vì chỉ nhìn giá hôm nay.',
  },
  {
    id: 3,
    title: 'Nhận diện sớm bệnh đạo ôn qua ảnh lá lúa',
    category: 'Sâu bệnh',
    date: '24/04/2026',
    readTime: '7 phút đọc',
    image: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Dấu hiệu hình ảnh thường gặp, điều kiện phát sinh và cách ghi nhận mẫu ảnh để AI phân tích ổn định hơn.',
  },
  {
    id: 4,
    title: 'Ứng dụng drone và cảm biến trong hợp tác xã',
    category: 'Công nghệ',
    date: '18/04/2026',
    readTime: '4 phút đọc',
    image: 'https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Các kịch bản dùng drone, cảm biến đất và dữ liệu thời tiết để giảm thao tác thủ công trong quản lý mùa vụ.',
  },
  {
    id: 5,
    title: 'Chuẩn bị dữ liệu để dự báo sản lượng tốt hơn',
    category: 'Canh tác',
    date: '12/04/2026',
    readTime: '5 phút đọc',
    image: 'https://images.unsplash.com/photo-1511735643442-503bb3bd348a?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Những trường dữ liệu nên ghi hằng tuần: diện tích, giống, ngày gieo, lượng mưa, phân bón và tình trạng cây.',
  },
  {
    id: 6,
    title: 'Khi nào nên bật cảnh báo giá theo vùng?',
    category: 'Thị trường',
    date: '06/04/2026',
    readTime: '3 phút đọc',
    image: 'https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=900&q=80',
    excerpt:
      'Gợi ý đặt ngưỡng giá theo chi phí đầu vào, mức lợi nhuận mục tiêu và độ biến động của từng nông sản.',
  },
];

const ArticlesPage = () => {
  const { isAuthenticated } = useAuth();
  const [activeCategory, setActiveCategory] = useState('Tất cả');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredArticles = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return articles.filter((article) => {
      const matchesCategory = activeCategory === 'Tất cả' || article.category === activeCategory;
      const matchesSearch =
        normalizedSearch.length === 0 ||
        article.title.toLowerCase().includes(normalizedSearch) ||
        article.excerpt.toLowerCase().includes(normalizedSearch);

      return matchesCategory && matchesSearch;
    });
  }, [activeCategory, searchTerm]);

  const featuredArticle = articles[0];

  return (
    <div className="min-h-screen bg-white">
      <PublicHeader />

      <main>
        <section className="border-b border-gray-200 bg-gray-50">
          <div className="mx-auto grid max-w-7xl gap-8 px-4 py-14 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-green-700">Thư viện kỹ thuật</p>
              <h1 className="mt-3 text-4xl font-bold text-gray-900">Bài viết nông nghiệp và thị trường</h1>
              <p className="mt-4 leading-7 text-gray-600">
                Tổng hợp hướng dẫn canh tác, phân tích giá và kinh nghiệm vận hành trang trại để dùng ngay trong
                các quyết định hằng ngày.
              </p>
            </div>

            <article className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
              <img src={featuredArticle.image} alt={featuredArticle.title} className="h-56 w-full object-cover" />
              <div className="p-5">
                <div className="mb-3 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                  <span className="rounded-full bg-green-50 px-3 py-1 font-semibold text-green-700">
                    {featuredArticle.category}
                  </span>
                  <span className="flex items-center gap-1">
                    <CalendarDays className="h-4 w-4" />
                    {featuredArticle.date}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-gray-900">{featuredArticle.title}</h2>
                <p className="mt-2 text-sm leading-6 text-gray-600">{featuredArticle.excerpt}</p>
              </div>
            </article>
          </div>
        </section>

        <section className="py-12">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex flex-wrap gap-2">
                {categories.map((category) => (
                  <button
                    key={category}
                    type="button"
                    onClick={() => setActiveCategory(category)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                      activeCategory === category
                        ? 'bg-green-700 text-white'
                        : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>

              <div className="relative w-full lg:max-w-sm">
                <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Tìm bài viết..."
                  className="w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredArticles.map((article) => (
                <article key={article.id} className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
                  <img src={article.image} alt={article.title} className="h-48 w-full object-cover" />
                  <div className="p-5">
                    <div className="mb-3 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-700">
                        <Tag className="h-3.5 w-3.5" />
                        {article.category}
                      </span>
                      <span>{article.readTime}</span>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">{article.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-gray-600">{article.excerpt}</p>
                    <button className="mt-4 flex items-center gap-1 text-sm font-semibold text-green-700 hover:text-green-800">
                      Đọc tiếp
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </div>
                </article>
              ))}
            </div>

            {filteredArticles.length === 0 && (
              <div className="rounded-lg border border-dashed border-gray-300 p-10 text-center">
                <p className="font-medium text-gray-900">Không tìm thấy bài viết phù hợp.</p>
                <p className="mt-2 text-sm text-gray-600">Thử đổi từ khóa hoặc chọn danh mục khác.</p>
              </div>
            )}

            {!isAuthenticated && (
              <div className="mt-12 rounded-lg bg-gray-950 p-8 text-white md:flex md:items-center md:justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Muốn nhận bản tin kỹ thuật hằng tuần?</h2>
                  <p className="mt-2 text-gray-300">Đăng nhập để lưu chủ đề quan tâm và nhận đề xuất bài viết theo cây trồng.</p>
                </div>
                <Link
                  to="/login"
                  className="mt-5 inline-flex rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800 md:mt-0"
                >
                  Đăng nhập
                </Link>
              </div>
            )}
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
};

export default ArticlesPage;
