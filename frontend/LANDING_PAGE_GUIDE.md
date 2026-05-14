# Landing Page - Hướng dẫn

## Tổng quan
Landing Page được thiết kế dựa trên giao diện hiện đại với các tính năng:

### Các phần chính:
1. **Header/Navigation**
   - Logo AgriAI
   - Menu điều hướng (Tính năng, Bài viết, Bảng giá, Liên hệ)
   - Nút "Đăng nhập" và "Bắt đầu ngay"
   - Responsive menu cho mobile

2. **Hero Section**
   - Tiêu đề chính: "Nông tâm Nông nghiệp Việt bằng Trí tuệ nhân tạo"
   - Mô tả ngắn gọn về nền tảng
   - 2 CTA buttons: "Bắt đầu ngay" và "Xem demo miễn phí"
   - Hình ảnh ruộng lúa với floating stats card
   - Trust badge hiển thị 95% nông dân hài lòng

3. **Stats Section**
   - 5000+ Nông dân sử dụng
   - 95% Độ chính xác AI
   - 20% Tăng năng suất TB

4. **Features Section**
   - 4 tính năng chính:
     - Dự báo Thu hoạch
     - Định giá Thông minh
     - Kiểm tra Chất lượng
     - Chat với AI
   - Mỗi feature có icon, tiêu đề và mô tả

5. **Articles Section (Thư viện Kỹ thuật)**
   - Hiển thị 2 bài viết mẫu
   - Mỗi bài có hình ảnh, tiêu đề, mô tả và ngày đăng
   - Nút "Xem tất cả" để xem thêm

6. **Testimonial Section**
   - Phản hồi từ nông dân thực tế
   - Avatar và thông tin người đánh giá
   - Background gradient xanh lá

7. **CTA Section**
   - Call-to-action cuối trang
   - Background gradient xanh đậm
   - Nút "Dùng thử miễn phí"

8. **Footer**
   - 4 cột: Company Info, Sản phẩm, Về chúng tôi, Hỗ trợ
   - Social media links
   - Copyright info

## Routing
- `/` - Landing Page (không có sidebar/navbar)
- `/dashboard` - Dashboard chính (có sidebar/navbar)
- `/pricing` - Trang định giá
- `/quality` - Trang kiểm tra chất lượng
- `/harvest` - Trang dự báo thu hoạch
- `/market` - Trang thị trường
- `/alerts` - Trang cảnh báo

## Màu sắc chính
- Primary Green: `#15803d` (green-700)
- Light Green: `#22c55e` (green-500)
- Dark Green: `#14532d` (green-900)
- Background: `#f9fafb` (gray-50)

## Icons sử dụng
- `lucide-react` package
- Icons: Sprout, TrendingUp, Shield, FileText, Leaf, CloudRain, ChevronRight, Menu, X

## Responsive Design
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Cách chạy
```bash
cd frontend
npm install
npm run dev
```

## Tùy chỉnh
- Thay đổi hình ảnh trong các section bằng cách cập nhật URL trong component
- Thêm/bớt features trong mảng `features`
- Thêm/bớt articles trong mảng `articles`
- Cập nhật stats trong mảng `stats`

## Tích hợp Backend
Landing page hiện tại là static. Để tích hợp với backend:
1. Thêm API calls để lấy articles từ database
2. Thêm form đăng ký/đăng nhập
3. Thêm analytics tracking
4. Thêm newsletter subscription
