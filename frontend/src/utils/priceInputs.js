export const CROP_SUGGESTIONS = [
  'Cà phê',
  'Hồ tiêu',
  'Lúa',
  'Gạo',
  'Sầu riêng',
  'Thanh long',
  'Xoài',
  'Chuối',
  'Cà chua',
  'Rau cải',
  'Ngô',
  'Đậu nành',
  'Điều',
  'Cao su',
];

export const REGION_SUGGESTIONS = [
  'Đắk Lắk',
  'Lâm Đồng',
  'Gia Lai',
  'Đồng Nai',
  'Bình Phước',
  'Tiền Giang',
  'Long An',
  'An Giang',
  'Cần Thơ',
  'Đồng Tháp',
  'Sóc Trăng',
  'Bến Tre',
  'Hà Nội',
  'TP. Hồ Chí Minh',
  'Đà Nẵng',
];

const removeVietnameseTone = (value) => {
  const text = String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  return text.replace(/đ/g, 'd').replace(/Đ/g, 'D');
};

export const normalizePriceInput = (value) => {
  const trimmed = String(value ?? '').trim();
  if (!trimmed) return '';
  return trimmed.replace(/\s+/g, ' ');
};

export const buildPriceQuery = ({ cropName, region }) => ({
  crop_name: normalizePriceInput(cropName),
  region: normalizePriceInput(region),
});

export const normalizePriceKey = (value) => removeVietnameseTone(normalizePriceInput(value)).toLowerCase();

export const getSuggestionsByPrefix = (value, suggestions) => {
  const normalized = normalizePriceKey(value);
  if (!normalized) return suggestions;
  return suggestions.filter((item) => normalizePriceKey(item).includes(normalized));
};
