# 📅 Quản Lý Mùa Vụ - Season Management Page

## 🎯 Tổng Quan

**Trang Quản lý Mùa vụ** là giao diện mới được thêm vào để quản lý tất cả các mùa vụ canh tác của nông dân, dựa trên bảng **`HarvestSchedule`** trong database.

**Route:** `/season-management`  
**Component:** `SeasonManagementPage.jsx`  
**Database Table:** `HarvestSchedule`

---

## ✨ Tính Năng Chính

### **1. Thống Kê Tổng Quan (4 Cards)**
- 🌱 **Đang trồng** - Số mùa vụ đang trong giai đoạn sinh trưởng
- ⏰ **Sắp thu hoạch** - Số mùa vụ sắp đến thời điểm thu hoạch
- 📦 **Tổng diện tích** - Tổng diện tích canh tác (hecta)
- 📈 **Tổng sản lượng** - Tổng sản lượng ước tính/thực tế (tấn)

### **2. Bộ Lọc & Tìm Kiếm**
- **Tìm kiếm:** Theo tên cây trồng hoặc khu vực
- **Bộ lọc trạng thái:**
  - Tất cả
  - Đang trồng (growing)
  - Sắp thu hoạch (harvesting)
  - Đã hoàn thành (completed)

### **3. Danh Sách Mùa Vụ (Grid View)**
Mỗi card mùa vụ hiển thị:
- **Ảnh đại diện** cây trồng
- **Badge trạng thái** (Đang trồng / Sắp thu hoạch / Đã thu hoạch)
- **Tên cây trồng** (VD: Lúa OM 5451, Cà phê Robusta)
- **Thông tin chi tiết:**
  - 📍 Khu vực (VD: An Giang, Đắk Lắk)
  - 📦 Diện tích (VD: 2.5 hecta)
  - 📅 Ngày gieo trồng
  - 📈 Sản lượng (ước tính hoặc thực tế)
- **Progress bar** (cho mùa vụ đang diễn ra)
- **Số ngày còn lại** đến thu hoạch
- **Actions:**
  - Chi tiết (xem đầy đủ)
  - Chỉnh sửa
  - Xóa

### **4. Dữ Liệu Mẫu (6 Mùa Vụ)**
1. **Lúa OM 5451** - An Giang (Đang trồng, 65%, còn 28 ngày)
2. **Cà phê Robusta** - Đắk Lắk (Sắp thu hoạch, 92%, còn 7 ngày)
3. **Hồ tiêu** - Bà Rịa - Vũng Tàu (Đã thu hoạch, 4500kg)
4. **Sầu riêng Monthong** - Tiền Giang (Đang trồng, 45%, còn 42 ngày)
5. **Ngô lai** - Đồng Nai (Đã thu hoạch, 5800kg)
6. **Thanh long ruột đỏ** - Bình Thuận (Sắp thu hoạch, 88%, còn 12 ngày)

---

## 🗄️ Mapping với Database

### **Bảng HarvestSchedule**
```sql
CREATE TABLE HarvestSchedule (
    ScheduleID INT PRIMARY KEY,
    UserID INT,
    CropID INT,
    PlantingDate DATE,
    AreaSize DECIMAL(10,2),
    Region NVARCHAR(100),
    ExpectedHarvestDate DATE,
    ActualHarvestDate DATE,
    EstimatedYieldKg INT,
    ActualYieldKg INT,
    FertilizerUsed NVARCHAR(200),
    PesticideUsed NVARCHAR(200),
    Status NVARCHAR(50),
    Notes NVARCHAR(MAX),
    CreatedAt DATETIME,
    UpdatedAt DATETIME
);
```

### **Mapping Fields**
| UI Field | Database Column | Type |
|----------|----------------|------|
| Tên cây trồng | CropID → CropTypes.CropName | String |
| Khu vực | Region | String |
| Diện tích | AreaSize | Decimal |
| Ngày gieo | PlantingDate | Date |
| Ngày thu hoạch dự kiến | ExpectedHarvestDate | Date |
| Ngày thu hoạch thực tế | ActualHarvestDate | Date |
| Sản lượng ước tính | EstimatedYieldKg | Integer |
| Sản lượng thực tế | ActualYieldKg | Integer |
| Trạng thái | Status | String |
| Phân bón | FertilizerUsed | String |
| Thuốc BVTV | PesticideUsed | String |
| Ghi chú | Notes | Text |

### **Status Values**
- `growing` → "Đang trồng"
- `harvesting` → "Sắp thu hoạch"
- `completed` → "Đã thu hoạch"
- `failed` → "Thất mùa"

---

## 🎨 Design

### **Colors**
- **Đang trồng:** Green (`bg-green-100 text-green-700`)
- **Sắp thu hoạch:** Yellow (`bg-yellow-100 text-yellow-700`)
- **Đã hoàn thành:** Gray (`bg-gray-100 text-gray-700`)

### **Icons (Lucide React)**
- 🌱 `Leaf` - Đang trồng
- ⏰ `Clock` - Sắp thu hoạch
- ✅ `CheckCircle` - Đã hoàn thành
- 📍 `MapPin` - Khu vực
- 📦 `Package` - Diện tích/Sản lượng
- 📅 `Calendar` - Ngày tháng
- 📈 `TrendingUp` - Sản lượng
- ✏️ `Edit` - Chỉnh sửa
- 🗑️ `Trash2` - Xóa
- ➕ `Plus` - Thêm mới

### **Layout**
- **Grid:** 3 columns trên desktop, 2 columns trên tablet, 1 column trên mobile
- **Card:** Rounded-2xl, shadow-sm, border-2
- **Image:** Height 48 (192px)
- **Progress bar:** Height 2 (8px)

---

## 🔄 Tích Hợp API (Tương Lai)

### **GET /api/harvest/schedules**
Lấy danh sách tất cả mùa vụ của user
```javascript
const response = await api.get('/api/harvest/schedules', {
  params: {
    user_id: userId,
    status: filterStatus, // 'all', 'growing', 'harvesting', 'completed'
    search: searchQuery
  }
});
```

### **POST /api/harvest/schedules**
Thêm mùa vụ mới
```javascript
const response = await api.post('/api/harvest/schedules', {
  crop_id: cropId,
  planting_date: '2024-08-15',
  area_size: 2.5,
  region: 'An Giang',
  fertilizer_used: 'NPK 16-16-8',
  pesticide_used: 'Không sử dụng',
  notes: 'Thời tiết thuận lợi'
});
```

### **PUT /api/harvest/schedules/:id**
Cập nhật mùa vụ
```javascript
const response = await api.put(`/api/harvest/schedules/${scheduleId}`, {
  actual_harvest_date: '2024-11-18',
  actual_yield_kg: 12800,
  status: 'completed',
  notes: 'Thu hoạch thành công'
});
```

### **DELETE /api/harvest/schedules/:id**
Xóa mùa vụ
```javascript
const response = await api.delete(`/api/harvest/schedules/${scheduleId}`);
```

---

## 📱 Responsive Design

### **Desktop (> 1024px)**
- Grid: 3 columns
- Sidebar: Visible
- Full features

### **Tablet (768px - 1024px)**
- Grid: 2 columns
- Sidebar: Collapsible
- Compact stats

### **Mobile (< 768px)**
- Grid: 1 column
- Sidebar: Hidden (hamburger menu)
- Stacked layout

---

## 🚀 Cách Sử Dụng

### **1. Xem Danh Sách Mùa Vụ**
- Truy cập `/season-management`
- Xem tất cả mùa vụ trong grid view
- Xem thống kê tổng quan ở trên cùng

### **2. Lọc Mùa Vụ**
- Click vào nút bộ lọc: "Tất cả", "Đang trồng", "Sắp thu hoạch", "Đã hoàn thành"
- Hoặc tìm kiếm theo tên cây trồng/khu vực

### **3. Xem Chi Tiết**
- Click nút "Chi tiết" trên card mùa vụ
- Xem đầy đủ thông tin: Phân bón, Thuốc BVTV, Ghi chú

### **4. Thêm Mùa Vụ Mới**
- Click nút "Thêm Mùa vụ" ở góc trên bên phải
- Điền form: Cây trồng, Khu vực, Diện tích, Ngày gieo
- Submit để lưu

### **5. Chỉnh Sửa/Xóa**
- Click icon ✏️ để chỉnh sửa
- Click icon 🗑️ để xóa (có confirm)

---

## 🎯 Use Cases

### **Use Case 1: Nông dân theo dõi nhiều mùa vụ**
Ông An có 3 vườn:
- Lúa OM 5451 (2.5 ha) - Đang trồng
- Cà phê Robusta (3.2 ha) - Sắp thu hoạch
- Hồ tiêu (1.8 ha) - Đã thu hoạch

→ Ông An vào trang Quản lý Mùa vụ để xem tổng quan và lên kế hoạch

### **Use Case 2: Chuẩn bị thu hoạch**
Bà Mai có mùa vụ Thanh long sắp thu hoạch (còn 12 ngày):
- Xem progress bar: 88%
- Xem sản lượng ước tính: 18,000 kg
- Chuẩn bị nhân lực và phương tiện

### **Use Case 3: Phân tích lịch sử**
Ông Bình muốn xem lại mùa vụ Ngô đã thu hoạch:
- Filter: "Đã hoàn thành"
- Xem sản lượng thực tế: 5,800 kg
- So sánh với ước tính: 6,000 kg
- Rút kinh nghiệm cho mùa sau

---

## 🔗 Liên Kết Với Các Trang Khác

### **1. HarvestForecastPage**
- Từ Quản lý Mùa vụ → Click "Dự báo thu hoạch"
- Chọn mùa vụ cụ thể để dự báo chi tiết

### **2. ProfilePage**
- Từ Profile → "Trang trại của tôi" → "Quản lý mùa vụ"
- Xem mùa vụ theo từng vườn

### **3. NewDashboard**
- Dashboard hiển thị "Ngày thu hoạch tiếp theo"
- Click để đến Quản lý Mùa vụ

### **4. ReportsPage**
- Báo cáo sản lượng theo mùa vụ
- Link đến chi tiết mùa vụ

---

## 📊 Thống Kê & Insights

### **Tính Toán Tự Động**
- **Progress:** `(Ngày hiện tại - Ngày gieo) / (Ngày thu hoạch - Ngày gieo) * 100`
- **Ngày còn lại:** `Ngày thu hoạch - Ngày hiện tại`
- **Tổng diện tích:** `SUM(AreaSize)`
- **Tổng sản lượng:** `SUM(ActualYieldKg OR EstimatedYieldKg)`

### **Insights AI (Tương Lai)**
- Dự báo sản lượng dựa trên thời tiết
- Khuyến nghị thời điểm thu hoạch tối ưu
- Cảnh báo rủi ro (sâu bệnh, thời tiết xấu)
- So sánh với mùa vụ trước

---

## ✅ Checklist Hoàn Thành

- [x] UI Design hoàn chỉnh
- [x] 6 mùa vụ mock data
- [x] Bộ lọc & tìm kiếm
- [x] Thống kê tổng quan
- [x] Progress bar
- [x] Responsive design
- [x] Icons & colors
- [x] Empty state
- [x] Route `/season-management`
- [x] Thêm vào Sidebar
- [x] Documentation

---

## 🔜 Tính Năng Tương Lai

### **Phase 2 - API Integration**
- [ ] Kết nối với backend API
- [ ] CRUD operations (Create, Read, Update, Delete)
- [ ] Real-time updates
- [ ] Pagination

### **Phase 3 - Advanced Features**
- [ ] Calendar view (lịch mùa vụ)
- [ ] Gantt chart (timeline)
- [ ] Export PDF/Excel
- [ ] Notifications (nhắc nhở thu hoạch)
- [ ] Weather integration
- [ ] AI recommendations

### **Phase 4 - Analytics**
- [ ] Biểu đồ sản lượng theo thời gian
- [ ] So sánh mùa vụ
- [ ] ROI calculation
- [ ] Cost tracking

---

## 📝 Notes

- Trang này dựa trên bảng `HarvestSchedule` trong database
- Mock data có 6 mùa vụ mẫu
- Sẵn sàng để tích hợp API backend
- Design system nhất quán với các trang khác
- Responsive trên mọi thiết bị

---

**Tạo bởi:** Kiro AI Assistant  
**Ngày:** 2026-05-05  
**Version:** 1.0

**🎉 Trang Quản lý Mùa vụ đã sẵn sàng!**
