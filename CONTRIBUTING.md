# Contributing to AgriAI

Cảm ơn bạn đã quan tâm đến việc đóng góp cho AgriAI! 🌾

## Quy trình đóng góp

### 1. Fork repository
Fork repository về tài khoản GitHub của bạn.

### 2. Clone về máy local
```bash
git clone https://github.com/your-username/agri-ai.git
cd agri-ai
```

### 3. Tạo branch mới
```bash
git checkout -b feature/your-feature-name
# hoặc
git checkout -b fix/your-bug-fix
```

### 4. Thực hiện thay đổi
- Viết code rõ ràng, dễ hiểu
- Tuân thủ coding style hiện tại
- Thêm comments khi cần thiết
- Viết tests cho code mới

### 5. Commit changes
```bash
git add .
git commit -m "feat: add new feature"
# hoặc
git commit -m "fix: resolve bug in pricing"
```

#### Commit Message Convention
- `feat:` - Tính năng mới
- `fix:` - Sửa bug
- `docs:` - Cập nhật documentation
- `style:` - Format code, không thay đổi logic
- `refactor:` - Refactor code
- `test:` - Thêm hoặc sửa tests
- `chore:` - Cập nhật build, dependencies

### 6. Push lên GitHub
```bash
git push origin feature/your-feature-name
```

### 7. Tạo Pull Request
- Mở Pull Request từ branch của bạn về `main`
- Mô tả rõ ràng những thay đổi
- Link đến issue liên quan (nếu có)

## Coding Standards

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Maximum line length: 100 characters

```python
def calculate_price(crop_name: str, region: str) -> float:
    """
    Calculate price for given crop and region.
    
    Args:
        crop_name: Name of the crop
        region: Region name
        
    Returns:
        Calculated price in VND
    """
    pass
```

### JavaScript/React (Frontend)
- Use ES6+ features
- Functional components with hooks
- PropTypes or TypeScript for type checking
- Meaningful variable names

```javascript
const PriceCard = ({ price, trend }) => {
  return (
    <div className="price-card">
      <h3>{price}</h3>
      <span>{trend}</span>
    </div>
  );
};
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Báo cáo Bug

Khi báo cáo bug, vui lòng bao gồm:
- Mô tả chi tiết bug
- Các bước để reproduce
- Expected behavior vs Actual behavior
- Screenshots (nếu có)
- Environment (OS, browser, versions)

## Đề xuất tính năng

Khi đề xuất tính năng mới:
- Mô tả rõ ràng tính năng
- Giải thích tại sao cần tính năng này
- Đề xuất cách implement (nếu có)

## Code Review

Tất cả Pull Requests sẽ được review trước khi merge:
- Code quality
- Test coverage
- Documentation
- Performance impact

## Questions?

Nếu có câu hỏi, hãy:
- Mở issue trên GitHub
- Hoặc liên hệ qua email

Cảm ơn bạn đã đóng góp! 🙏
