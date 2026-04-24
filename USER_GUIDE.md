# 📖 Hướng dẫn sử dụng AgriAI

## Giới thiệu

AgriAI là hệ thống AI giúp nông dân:
- 💰 Tra cứu và dự báo giá nông sản
- 📸 Kiểm tra chất lượng nông sản qua ảnh
- 📊 Phân tích xu hướng thị trường
- 💡 Nhận khuyến nghị bán hàng

## Truy cập hệ thống

Mở trình duyệt và truy cập: **http://localhost:5173**

## Các tính năng chính

### 1. 📊 Trang Tổng quan (Dashboard)

Khi vào hệ thống, bạn sẽ thấy trang tổng quan với:
- Các tính năng chính
- Thống kê nhanh
- Truy cập nhanh các chức năng

**Cách sử dụng:**
- Click vào từng ô để truy cập tính năng tương ứng

---

### 2. 💰 Định giá nông sản

#### Tra cứu giá hiện tại

**Bước 1:** Click "Định giá" trên menu

**Bước 2:** Chọn thông tin:
- **Loại nông sản**: Cà chua, Dưa chuột, Rau muống, v.v.
- **Khu vực**: Hà Nội, TP.HCM, Đà Nẵng, v.v.
- **Số ngày dự báo**: 7, 14, hoặc 30 ngày

**Bước 3:** Click "Tra cứu"

**Kết quả hiển thị:**
- ✅ Giá hiện tại (đồng/kg)
- ✅ Xu hướng giá (Tăng/Giảm/Ổn định)
- ✅ Phân loại chất lượng
- ✅ Biểu đồ dự báo giá
- ✅ Khuyến nghị bán hàng

#### Đọc biểu đồ dự báo

- **Đường xanh**: Giá dự báo
- **Đường nét đứt**: Khoảng tin cậy (giá có thể dao động)
- **Trục ngang**: Ngày tháng
- **Trục dọc**: Giá (đồng/kg)

#### Hiểu khuyến nghị

**"Giá có xu hướng tăng"**
→ Nên giữ hàng thêm vài ngày để bán được giá tốt hơn

**"Giá có xu hướng giảm"**
→ Nên bán sớm để tránh mất giá

**"Giá ổn định"**
→ Có thể bán bất cứ lúc nào phù hợp

---

### 3. 📸 Kiểm tra chất lượng nông sản

#### Upload và kiểm tra ảnh

**Bước 1:** Click "Kiểm tra chất lượng" trên menu

**Bước 2:** Upload ảnh
- Click vào khung "Chọn ảnh"
- Chọn ảnh nông sản từ máy tính/điện thoại
- Ảnh sẽ hiển thị preview

**Bước 3:** Click "Kiểm tra chất lượng"

**Bước 4:** Đợi AI phân tích (3-5 giây)

#### Đọc kết quả

**Phân loại chất lượng:**
- 🟢 **Loại 1**: Chất lượng cao, không khuyết tật
- 🟡 **Loại 2**: Chất lượng trung bình, ít khuyết tật
- 🔴 **Loại 3**: Chất lượng thấp, nhiều khuyết tật

**Độ tin cậy:**
- Cho biết AI chắc chắn bao nhiêu % về kết quả
- Càng cao càng chính xác

**Giá đề xuất:**
- Khoảng giá phù hợp với chất lượng
- Tính theo đồng/kg

**Khuyết tật phát hiện:**
- Danh sách các vấn đề AI phát hiện
- Ví dụ: vết thâm, hư hỏng, sâu bệnh

**Khuyến nghị:**
- Lời khuyên về cách bán
- Kênh bán phù hợp
- Lưu ý bảo quản

---

## Mẹo sử dụng hiệu quả

### Khi chụp ảnh kiểm tra chất lượng

✅ **NÊN:**
- Chụp ở nơi có ánh sáng tốt
- Chụp rõ nét, không mờ
- Chụp cận cảnh sản phẩm
- Chụp nhiều góc độ khác nhau
- Nền đơn giản, không lộn xộn

❌ **KHÔNG NÊN:**
- Chụp quá tối hoặc quá sáng
- Chụp từ xa quá
- Ảnh bị mờ, lắc
- Nhiều sản phẩm khác nhau trong 1 ảnh

### Khi tra cứu giá

✅ **Lưu ý:**
- Giá có thể khác nhau giữa các vùng
- Chất lượng ảnh hưởng đến giá
- Mùa vụ ảnh hưởng đến giá
- Nên tra cứu thường xuyên để cập nhật

### Khi xem dự báo giá

✅ **Cách đọc:**
- Dự báo 7 ngày: Độ chính xác cao
- Dự báo 14 ngày: Độ chính xác trung bình
- Dự báo 30 ngày: Tham khảo xu hướng

---

## Câu hỏi thường gặp (FAQ)

### Q: Giá hiển thị có chính xác không?
**A:** Giá được tổng hợp từ nhiều nguồn và dự báo bằng AI. Nên dùng để tham khảo, giá thực tế có thể dao động.

### Q: AI kiểm tra chất lượng có chính xác không?
**A:** AI được huấn luyện trên nhiều ảnh, độ chính xác khoảng 85-90%. Nên kết hợp với kinh nghiệm thực tế.

### Q: Tại sao giá khác nhau giữa các vùng?
**A:** Do chi phí vận chuyển, cung cầu địa phương, và điều kiện thị trường khác nhau.

### Q: Dự báo giá dựa trên gì?
**A:** AI phân tích lịch sử giá, xu hướng mùa vụ, và các yếu tố thị trường.

### Q: Tôi có thể upload ảnh từ điện thoại không?
**A:** Có, hệ thống hỗ trợ upload từ mọi thiết bị có trình duyệt web.

### Q: Hệ thống có lưu ảnh của tôi không?
**A:** Ảnh chỉ được xử lý tạm thời và xóa ngay sau khi phân tích.

### Q: Tôi có thể xem lịch sử tra cứu không?
**A:** Tính năng này sẽ có trong phiên bản tiếp theo.

---

## Khắc phục sự cố

### Không tải được trang
- Kiểm tra kết nối internet
- Thử refresh trang (F5)
- Xóa cache trình duyệt

### Upload ảnh bị lỗi
- Kiểm tra kích thước ảnh (tối đa 10MB)
- Đảm bảo file là ảnh (JPG, PNG)
- Thử ảnh khác

### Không hiển thị kết quả
- Đợi thêm vài giây
- Refresh trang và thử lại
- Kiểm tra kết nối internet

### Giá không cập nhật
- Refresh trang
- Thử chọn khu vực khác
- Liên hệ hỗ trợ

---

## Liên hệ hỗ trợ

Nếu gặp vấn đề:
1. Đọc phần FAQ ở trên
2. Thử khắc phục theo hướng dẫn
3. Liên hệ qua email: support@agriai.vn
4. Gọi hotline: 1900-xxxx

---

## Cập nhật tính năng mới

Hệ thống sẽ sớm có thêm:
- 🌾 Dự báo thời điểm thu hoạch
- 📱 Ứng dụng di động
- 🔔 Cảnh báo giá qua Zalo
- 💼 Tư vấn kênh bán hàng
- 📊 Báo cáo chi tiết

---

**Chúc bạn sử dụng AgriAI hiệu quả!** 🌾

*Phiên bản: 1.0.0*  
*Cập nhật: 15/01/2024*
