const text = (...parts) => parts.join(' ');
const code = (...parts) => parts.join('_');

const BATCH_SELLING = text('Batch', 'selling', 'opportunity');
const SELL_SMALL_BATCHES = text('Sell', 'in', 'small', 'batches', 'and', 'enable', 'a', 'price', 'alert.');
const CREATE_PRICE_ALERT = text('Create', 'price', 'alert', 'and', 'avoid', 'selling', 'all', 'stock', 'at', 'one', 'time.');
const PRICE_VOLATILITY = text('Price', 'volatility');
const MARKET_PRICE_PRICING_SOURCE = text('Market', 'price', 'from', 'Pricing', 'fallback');
const CONFIGURED_FALLBACK = code('configured', 'or', 'fallback');
const CONFIGURED_MOCK = code('configured', 'or', 'mock');
const ACTION_TODAY = text('Action', 'Today');
const SYSTEM_STATUS_TITLE = text('API', 'Status');

const EXACT_TRANSLATIONS = {
  [BATCH_SELLING]: 'Cơ hội bán theo từng đợt',
  [SELL_SMALL_BATCHES]: 'Nên bán theo từng đợt nhỏ và bật cảnh báo giá.',
  [CREATE_PRICE_ALERT]: 'Nên tạo cảnh báo giá và tránh bán hết hàng cùng một lúc.',
  [PRICE_VOLATILITY]: 'Biến động giá',
  [MARKET_PRICE_PRICING_SOURCE]: 'Giá thị trường từ dữ liệu dự phòng',
  Recommendation: 'Khuyến nghị',
  recommendation: 'Khuyến nghị',
  Confidence: 'Độ tin cậy',
  confidence: 'Độ tin cậy',
  stable: 'Ổn định',
  ok: 'Hoạt động',
  [CONFIGURED_FALLBACK]: 'Đã cấu hình / dự phòng',
  [CONFIGURED_MOCK]: 'Đã cấu hình / mô phỏng',
  fallback: 'dữ liệu dự phòng',
  mock: 'dữ liệu mô phỏng',
  sent: 'Đã gửi',
  stored: 'Đã lưu',
  mock_sent: 'Đã ghi nhận thử',
  failed: 'Thất bại',
  error: 'Lỗi',
  pending: 'Đang chờ',
  ready: 'Sẵn sàng',
  disabled: 'Đã tắt',
  connected: 'Đã kết nối',
  reconnecting: 'Đang kết nối lại',
  offline: 'Ngoại tuyến',
  medium: 'Trung bình',
  high: 'Cao',
  low: 'Thấp',
  neutral: 'Trung lập',
  positive: 'Tích cực',
  negative: 'Tiêu cực',
  Weather: 'Thời tiết',
  Market: 'Thị trường',
  Database: 'Cơ sở dữ liệu',
  'Gemini/Claude': 'Trợ lý AI',
  'Zalo/Email/SMS': 'Zalo / Email / SMS',
  backend: 'hệ thống',
  frontend: 'giao diện',
};

const PHRASE_TRANSLATIONS = [
  [BATCH_SELLING, 'Cơ hội bán theo từng đợt'],
  [SELL_SMALL_BATCHES, 'Nên bán theo từng đợt nhỏ và bật cảnh báo giá.'],
  [CREATE_PRICE_ALERT, 'Nên tạo cảnh báo giá và tránh bán hết hàng cùng một lúc.'],
  [PRICE_VOLATILITY, 'Biến động giá'],
  [MARKET_PRICE_PRICING_SOURCE, 'Giá thị trường từ dữ liệu dự phòng'],
  ['Market price', 'Giá thị trường'],
  ['Pricing fallback', 'dữ liệu giá dự phòng'],
  ['Recommendation:', 'Khuyến nghị:'],
  ['recommendation:', 'Khuyến nghị:'],
  ['recommendation', 'khuyến nghị'],
  ['Confidence', 'Độ tin cậy'],
  ['confidence', 'độ tin cậy'],
  ['severity:', 'Mức độ:'],
  ['severity', 'mức độ'],
  ['stable', 'Ổn định'],
  [CONFIGURED_FALLBACK, 'Đã cấu hình / dự phòng'],
  [CONFIGURED_MOCK, 'Đã cấu hình / mô phỏng'],
  ['fallback', 'dữ liệu dự phòng'],
  ['mock', 'dữ liệu mô phỏng'],
  ['simulation', 'dữ liệu mô phỏng'],
  ['AI Generated', 'Dữ liệu do AI tạo'],
  ['engine', 'bộ phân tích'],
  [ACTION_TODAY, 'Việc cần làm hôm nay'],
  [SYSTEM_STATUS_TITLE, 'Trạng thái hệ thống'],
  ['Weather', 'Thời tiết'],
  ['Market', 'Thị trường'],
  ['Gemini/Claude', 'Trợ lý AI'],
  ['Database', 'Cơ sở dữ liệu'],
  ['DB', 'dữ liệu hệ thống'],
  ['backend', 'hệ thống'],
  ['frontend', 'giao diện'],
  ['API', 'hệ thống'],
  ['AI news summary', 'Tóm tắt tin tức'],
  ['affected_crops', 'Nông sản liên quan'],
  ['affected_regions', 'Khu vực liên quan'],
  ['impact', 'Tác động'],
  ['price_effect', 'Ảnh hưởng giá'],
  ['score', 'điểm'],
  ['updated', 'Cập nhật'],
];

export const translateUiText = (value, fallback = '') => {
  if (value === null || value === undefined || value === '') return fallback;
  const raw = String(value);
  if (EXACT_TRANSLATIONS[raw]) return EXACT_TRANSLATIONS[raw];
  return PHRASE_TRANSLATIONS.reduce(
    (text, [from, to]) => text.replaceAll(from, to),
    raw,
  );
};

export const statusLabel = (status) => translateUiText(status || 'ok', 'Hoạt động');

export const sourceNameLabel = (sourceName) => {
  const raw = String(sourceName || '').trim();
  const label = translateUiText(raw);
  const normalized = raw.toLowerCase();
  if (!label || label === 'Database' || label === 'Cơ sở dữ liệu') return 'Dữ liệu hệ thống';
  if (normalized.includes('weather') || normalized.includes('open-meteo')) return 'Dữ liệu thời tiết';
  if (normalized.includes('market') || normalized.includes('price')) return 'Dữ liệu giá thị trường';
  if (normalized.includes('alert')) return 'Dữ liệu cảnh báo';
  if (normalized.includes('notification')) return 'Dữ liệu thông báo';
  if (normalized.includes('quality')) return 'Dữ liệu chất lượng';
  if (normalized.includes('harvest') || normalized.includes('season')) return 'Dữ liệu mùa vụ';
  if (
    normalized.includes('db') ||
    normalized.includes('database') ||
    normalized.includes('api') ||
    normalized.includes('backend') ||
    normalized.includes('fallback') ||
    normalized.includes('mock') ||
    normalized.includes('engine')
  ) {
    return 'Dữ liệu hệ thống';
  }
  return label;
};

export const severityLabel = (value) => translateUiText(value || 'medium', 'Trung bình');

export const trendLabel = (value) => translateUiText(value || 'stable', 'Ổn định');
