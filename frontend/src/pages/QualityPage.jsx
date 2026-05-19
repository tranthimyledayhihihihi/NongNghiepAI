import {
  AlertTriangle,
  BadgeCheck,
  BarChart3,
  Camera,
  CheckCircle2,
  CloudSun,
  Leaf,
  MapPin,
  PackageCheck,
  Sparkles,
  Tag,
  TrendingDown,
  Upload,
  XCircle,
} from 'lucide-react';
import { useState } from 'react';
import DataSourceBadge from '../components/DataSourceBadge';
import { getApiErrorMessage } from '../services/api';
import { qualityApi } from '../services/qualityApi';

const REGIONS = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng', 'Đắk Lắk', 'Tiền Giang'];

const GRADE = {
  grade_1: {
    label: 'Loại 1',
    sub: 'Chất lượng cao',
    badge: 'Xuất khẩu / Siêu thị',
    bg: 'from-emerald-500 to-green-600',
    border: 'border-emerald-200',
    light: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    icon: CheckCircle2,
    dot: 'bg-emerald-500',
    score: (conf) => Math.round(75 + conf * 25),
  },
  grade_2: {
    label: 'Loại 2',
    sub: 'Chất lượng trung bình',
    badge: 'Chợ đầu mối',
    bg: 'from-amber-400 to-yellow-500',
    border: 'border-amber-200',
    light: 'bg-amber-50 text-amber-800 border-amber-200',
    icon: AlertTriangle,
    dot: 'bg-amber-400',
    score: (conf) => Math.round(40 + conf * 30),
  },
  grade_3: {
    label: 'Loại 3',
    sub: 'Chất lượng thấp',
    badge: 'Chế biến / Bán nhanh',
    bg: 'from-red-400 to-rose-600',
    border: 'border-red-200',
    light: 'bg-red-50 text-red-800 border-red-200',
    icon: XCircle,
    dot: 'bg-red-400',
    score: (conf) => Math.round(10 + conf * 28),
  },
};

// ── Score ring ─────────────────────────────────────────────────────────────────
const ScoreRing = ({ score, grade }) => {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const filled = (score / 100) * circ;
  const color = grade === 'grade_1' ? '#10b981' : grade === 'grade_2' ? '#f59e0b' : '#ef4444';
  return (
    <div className="relative flex items-center justify-center w-24 h-24">
      <svg className="absolute inset-0 -rotate-90" width="96" height="96" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
        <circle
          cx="48" cy="48" r={r} fill="none"
          stroke={color} strokeWidth="8"
          strokeDasharray={`${filled} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="text-center z-10">
        <p className="text-2xl font-black text-gray-900 leading-none">{score}</p>
        <p className="text-xs text-gray-400 leading-none mt-0.5">/ 100</p>
      </div>
    </div>
  );
};

// ── Confidence bar ─────────────────────────────────────────────────────────────
const ConfBar = ({ value, color }) => (
  <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
    <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: `${(value * 100).toFixed(0)}%` }} />
  </div>
);

// ── Detail row ─────────────────────────────────────────────────────────────────
const Row = ({ icon: Icon, label, children, iconClass = 'text-gray-400' }) => (
  <div className="flex gap-3 py-3 border-b border-gray-50 last:border-0">
    <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${iconClass}`} />
    <div className="flex-1 min-w-0">
      <p className="text-xs font-medium text-gray-400 mb-0.5">{label}</p>
      {children}
    </div>
  </div>
);

// ── Main ───────────────────────────────────────────────────────────────────────
const QualityPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [region, setRegion] = useState('Đà Nẵng');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const applyFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleFileSelect = (e) => applyFile(e.target.files[0]);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    applyFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!selectedFile) { setError('Vui lòng chọn ảnh'); return; }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await qualityApi.checkWithPrice(selectedFile, '', region);
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(getApiErrorMessage(err, 'Lỗi khi kiểm tra chất lượng'));
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => { setPreview(null); setSelectedFile(null); setResult(null); setError(null); };

  const g = result ? (GRADE[result.quality_grade] ?? GRADE.grade_2) : null;
  const score = g ? g.score(result.confidence) : 0;
  const GradeIcon = g?.icon;
  const discountPct = result?.quality_multiplier != null && result.quality_multiplier < 1
    ? Math.round((1 - result.quality_multiplier) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* ── Page header ── */}
      <div className="bg-white border-b border-gray-100 px-6 py-5">
        <div className="max-w-6xl mx-auto flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-50">
            <Sparkles className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Kiểm định chất lượng nông sản</h1>
            <p className="text-sm text-gray-500">AI Gemini Vision — tự nhận diện, phân tích màu sắc & khuyết tật, định giá thị trường</p>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* ── LEFT: Upload ─────────────────────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-4">

          {/* Region */}
          <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <MapPin className="h-4 w-4 text-emerald-500" /> Khu vực thị trường
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-gray-50"
            >
              {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>

          {/* Upload zone */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div
              className={`relative min-h-[260px] flex items-center justify-center transition-colors ${dragOver ? 'bg-emerald-50' : 'bg-gray-50'}`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="w-full max-h-72 object-contain" />
              ) : (
                <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-3 p-10 w-full">
                  <div className={`p-4 rounded-2xl border-2 border-dashed transition-colors ${dragOver ? 'border-emerald-400 bg-emerald-100' : 'border-gray-300 bg-white'}`}>
                    <Upload className={`h-8 w-8 ${dragOver ? 'text-emerald-500' : 'text-gray-300'}`} />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold text-emerald-600">Kéo thả hoặc chọn ảnh</p>
                    <p className="text-xs text-gray-400 mt-1">PNG, JPG, WEBP — tối đa 10MB</p>
                  </div>
                  <input id="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleFileSelect} />
                </label>
              )}

              {preview && (
                <button
                  onClick={clearImage}
                  className="absolute top-2 right-2 bg-white/90 hover:bg-white text-gray-500 hover:text-red-500 text-xs px-2.5 py-1 rounded-full border border-gray-200 shadow-sm transition-colors"
                >
                  Xóa ảnh
                </button>
              )}
            </div>

            <div className="p-4 border-t border-gray-100">
              {error && (
                <div className="mb-3 p-3 bg-red-50 rounded-xl border border-red-200 text-sm text-red-600">{error}</div>
              )}
              <button
                onClick={handleSubmit}
                disabled={!selectedFile || loading}
                className="w-full bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white py-3 px-4 rounded-xl text-sm font-semibold disabled:from-gray-200 disabled:to-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    AI đang phân tích...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <Sparkles className="h-4 w-4" /> Phân tích chất lượng
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Tips */}
          {!result && (
            <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Để kết quả chính xác</p>
              {['Chụp rõ mặt quả, đủ ánh sáng', 'Đặt quả trên nền đơn giản', 'Ảnh ≥ 500×500 px, không mờ', 'Có thể chụp cả quả hoặc mặt cắt'].map((t) => (
                <div key={t} className="flex items-center gap-2 text-xs text-gray-600">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                  {t}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── RIGHT: Results ───────────────────────────────────────────────── */}
        <div className="lg:col-span-3">
          {!result && !loading && (
            <div className="h-full min-h-[400px] bg-white rounded-2xl border border-gray-200 shadow-sm flex flex-col items-center justify-center gap-4 text-gray-300">
              <Camera className="h-16 w-16" />
              <div className="text-center">
                <p className="text-base font-semibold text-gray-400">Chưa có kết quả phân tích</p>
                <p className="text-sm mt-1">Tải ảnh nông sản để AI đánh giá chất lượng và định giá</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="min-h-[400px] bg-white rounded-2xl border border-gray-200 shadow-sm flex flex-col items-center justify-center gap-4">
              <div className="relative">
                <div className="h-16 w-16 rounded-full border-4 border-emerald-100 border-t-emerald-500 animate-spin" />
                <Sparkles className="absolute inset-0 m-auto h-6 w-6 text-emerald-500" />
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold text-gray-700">AI đang phân tích hình ảnh</p>
                <p className="text-xs text-gray-400 mt-1">Nhận diện loại quả · Đánh giá màu sắc · Phát hiện khuyết tật</p>
              </div>
            </div>
          )}

          {result && g && (
            <div className="space-y-4">

              {/* ── Non-produce warning ── */}
              {result.is_produce === false && (
                <div className="flex items-center gap-3 p-4 bg-orange-50 border border-orange-200 rounded-2xl text-sm text-orange-700">
                  <AlertTriangle className="h-5 w-5 shrink-0" />
                  <span>Ảnh không chứa nông sản — vui lòng tải ảnh quả/rau/củ để phân tích</span>
                </div>
              )}

              {/* ── Hero card: Grade + Score ── */}
              <div className={`rounded-2xl bg-gradient-to-br ${g.bg} p-5 text-white shadow-md`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <DataSourceBadge data={result} className="bg-white/90" />
                      {Number.isFinite(result.confidence) && (
                        <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-semibold">
                          Độ tin cậy {(result.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    {result.detected_crop && (
                      <div className="inline-flex items-center gap-1.5 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-semibold mb-3">
                        <BadgeCheck className="h-3.5 w-3.5" />
                        AI nhận diện: <span className="capitalize ml-0.5">{result.detected_crop}</span>
                      </div>
                    )}
                    <p className="text-white/80 text-sm font-medium">Phân loại chất lượng</p>
                    <p className="text-3xl font-black mt-0.5">{g.label}</p>
                    <p className="text-white/80 text-sm mt-0.5">{g.sub}</p>
                    <div className="mt-3 inline-flex items-center gap-1.5 bg-white/20 px-3 py-1 rounded-full text-xs font-medium">
                      <PackageCheck className="h-3.5 w-3.5" /> {g.badge}
                    </div>
                  </div>
                  <div className="shrink-0 bg-white/15 rounded-2xl p-3">
                    <ScoreRing score={score} grade={result.quality_grade} />
                    <p className="text-center text-xs text-white/70 mt-1">Điểm chất lượng</p>
                  </div>
                </div>

                {/* Confidence */}
                <div className="mt-4 bg-white/15 rounded-xl p-3">
                  <div className="flex justify-between text-xs text-white/80 mb-1.5">
                    <span>Độ tin cậy AI</span>
                    <span className="font-bold">{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                    <div className="h-full bg-white rounded-full transition-all duration-700" style={{ width: `${(result.confidence * 100).toFixed(0)}%` }} />
                  </div>
                </div>
              </div>

              {/* ── Analysis cards grid ── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

                {/* Visual analysis */}
                <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 rounded-lg bg-purple-50">
                      <Camera className="h-4 w-4 text-purple-500" />
                    </div>
                    <span className="text-sm font-bold text-gray-800">Phân tích hình ảnh</span>
                  </div>
                  {result.color_assessment && (
                    <Row icon={Leaf} label="Màu sắc & tình trạng" iconClass="text-green-500">
                      <p className="text-sm text-gray-700">{result.color_assessment}</p>
                    </Row>
                  )}
                  {result.defects?.length > 0 ? (
                    <Row icon={AlertTriangle} label="Khuyết tật phát hiện" iconClass="text-red-400">
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {result.defects.map((d) => (
                          <span key={d} className="px-2.5 py-1 bg-red-50 text-red-600 text-xs rounded-full border border-red-100 font-medium">
                            {d}
                          </span>
                        ))}
                      </div>
                    </Row>
                  ) : (
                    <Row icon={CheckCircle2} label="Khuyết tật" iconClass="text-emerald-500">
                      <p className="text-sm text-emerald-600 font-medium">Không phát hiện khuyết tật</p>
                    </Row>
                  )}
                </div>

                {/* Price */}
                <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 rounded-lg bg-blue-50">
                      <BarChart3 className="h-4 w-4 text-blue-500" />
                    </div>
                    <span className="text-sm font-bold text-gray-800">Định giá thị trường</span>
                  </div>
                  <Row icon={MapPin} label={`Khu vực ${result.region}`} iconClass="text-blue-400">
                    <p className="text-xl font-black text-gray-900">
                      {result.suggested_price_range.min.toLocaleString('vi-VN')}
                      <span className="text-base font-medium text-gray-400 mx-1">–</span>
                      {result.suggested_price_range.max.toLocaleString('vi-VN')}
                      <span className="text-sm font-medium text-gray-500 ml-1">đ/kg</span>
                    </p>
                  </Row>
                  {discountPct > 0 && (
                    <Row icon={TrendingDown} label="Hệ số chất lượng" iconClass="text-orange-400">
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-1 bg-orange-50 text-orange-700 border border-orange-200 text-xs rounded-full font-semibold">
                          Giảm {discountPct}% do chất lượng
                        </span>
                      </div>
                    </Row>
                  )}
                  <Row icon={Tag} label="Nguồn giá" iconClass="text-gray-300">
                    <p className="text-xs text-gray-500">
                      {result.price_source === 'market_db' ? '✓ Giá thị trường thực tế' : '~ Ước tính'}
                      {result.weather_summary ? ` · ${result.weather_summary}` : ''}
                    </p>
                  </Row>
                </div>
              </div>

              {/* ── Reasoning ── */}
              {result.reasoning && (
                <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 rounded-lg bg-indigo-50">
                      <Sparkles className="h-4 w-4 text-indigo-500" />
                    </div>
                    <span className="text-sm font-bold text-gray-800">Lý do phân loại</span>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">{result.reasoning}</p>
                </div>
              )}

              {/* ── Recommendations ── */}
              {result.recommendations?.length > 0 && (
                <div className={`rounded-2xl border p-4 shadow-sm ${g.light}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 rounded-lg bg-white/60">
                      <CloudSun className="h-4 w-4" />
                    </div>
                    <span className="text-sm font-bold">Khuyến nghị xử lý & bán hàng</span>
                  </div>
                  <div className="space-y-2">
                    {result.recommendations.map((r, i) => (
                      <div key={r} className="flex items-start gap-2.5">
                        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/70 text-xs font-bold">
                          {i + 1}
                        </span>
                        <p className="text-sm leading-relaxed">{r}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Weather impact ── */}
              {result.weather_explanation && (
                <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="p-1.5 rounded-lg bg-sky-50">
                      <CloudSun className="h-4 w-4 text-sky-500" />
                    </div>
                    <span className="text-sm font-bold text-gray-800">Ảnh hưởng thời tiết đến giá</span>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">{result.weather_explanation}</p>
                  {result.price_change_pct != null && result.price_change_pct !== 0 && (
                    <div className={`mt-2 inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full ${result.price_change_pct > 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                      {result.price_change_pct > 0 ? '+' : ''}{result.price_change_pct.toFixed(1)}% so với giá cơ sở
                    </div>
                  )}
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityPage;
