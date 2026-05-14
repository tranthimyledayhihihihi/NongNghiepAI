import { AlertTriangle, Camera, CheckCircle, Upload, XCircle } from 'lucide-react';
import { useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { qualityApi } from '../services/qualityApi';

const regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng', 'Đắk Lắk', 'Tiền Giang'];

const gradeConfig = {
  grade_1: {
    label: 'Loại 1 — Chất lượng cao',
    color: 'text-green-700 bg-green-50 border-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-600',
  },
  grade_2: {
    label: 'Loại 2 — Chất lượng trung bình',
    color: 'text-yellow-700 bg-yellow-50 border-yellow-200',
    icon: AlertTriangle,
    iconColor: 'text-yellow-600',
  },
  grade_3: {
    label: 'Loại 3 — Chất lượng thấp',
    color: 'text-red-700 bg-red-50 border-red-200',
    icon: XCircle,
    iconColor: 'text-red-600',
  },
};

const QualityPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [region, setRegion] = useState('Đà Nẵng');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Vui lòng chọn ảnh');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await qualityApi.checkQuality(selectedFile, '', region);
      setResult(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Lỗi khi kiểm tra chất lượng'));
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setPreview(null);
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  const grade = result ? (gradeConfig[result.quality_grade] ?? gradeConfig.grade_2) : null;
  const GradeIcon = grade?.icon;

  return (
    <div className="px-4 py-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Kiểm định chất lượng nông sản</h1>
        <p className="mt-1 text-gray-500 text-sm">
          Chụp hoặc tải ảnh nông sản — AI tự nhận diện loại quả và đánh giá chất lượng
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ── Upload panel ── */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Tải ảnh lên</h2>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Khu vực (để tính giá)</label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {regions.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-xl min-h-48 flex items-center justify-center overflow-hidden">
            {preview ? (
              <div className="w-full">
                <img src={preview} alt="Preview" className="w-full max-h-72 object-contain rounded-xl" />
                <div className="text-center py-2">
                  <button onClick={clearImage} className="text-sm text-red-500 hover:text-red-600">
                    Xóa ảnh
                  </button>
                </div>
              </div>
            ) : (
              <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-3 p-8 w-full h-full">
                <Upload className="h-10 w-10 text-gray-300" />
                <span className="text-sm font-medium text-green-600 hover:text-green-700">Chọn ảnh</span>
                <span className="text-xs text-gray-400">PNG, JPG, WEBP tối đa 10MB</span>
                <input id="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleFileSelect} />
              </label>
            )}
          </div>

          {error && (
            <div className="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!selectedFile || loading}
            className="mt-4 w-full bg-green-600 text-white py-2.5 px-4 rounded-lg text-sm font-medium hover:bg-green-700 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Đang phân tích...
              </span>
            ) : 'Kiểm tra chất lượng'}
          </button>
        </div>

        {/* ── Result panel ── */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Kết quả phân tích</h2>

          {result ? (
            <div className="space-y-4">
              {/* Non-produce warning */}
              {result.is_produce === false && (
                <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-700">
                  ⚠️ Ảnh không chứa nông sản — vui lòng tải ảnh quả/rau/củ
                </div>
              )}

              {/* Detected crop */}
              {result.detected_crop && (
                <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                  <span className="text-2xl">🔍</span>
                  <div>
                    <p className="text-xs text-blue-500 font-medium">AI nhận diện</p>
                    <p className="text-base font-bold text-blue-800 capitalize">{result.detected_crop}</p>
                  </div>
                </div>
              )}

              {/* Grade badge */}
              <div className={`flex items-center justify-between p-4 rounded-xl border ${grade.color}`}>
                <div>
                  <p className="text-xs font-medium opacity-70">Phân loại</p>
                  <p className="text-lg font-bold mt-0.5">{grade.label}</p>
                  <p className="text-sm mt-1">Độ tin cậy: {(result.confidence * 100).toFixed(1)}%</p>
                </div>
                {GradeIcon && <GradeIcon className={`h-9 w-9 ${grade.iconColor}`} />}
              </div>

              {/* Color assessment */}
              {result.color_assessment && (
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <p className="text-xs font-medium text-gray-500 mb-1">Màu sắc & tình trạng</p>
                  <p className="text-sm text-gray-800">{result.color_assessment}</p>
                </div>
              )}

              {/* Price */}
              <div className="p-4 border border-gray-200 rounded-xl">
                <p className="text-xs font-medium text-gray-500 mb-1">Giá đề xuất tại {result.region}</p>
                <p className="text-xl font-bold text-gray-900">
                  {result.suggested_price_range.min.toLocaleString('vi-VN')} —{' '}
                  {result.suggested_price_range.max.toLocaleString('vi-VN')} đ/kg
                </p>
                {result.weather_summary && (
                  <p className="text-xs text-gray-400 mt-1">{result.weather_summary}</p>
                )}
              </div>

              {/* Defects */}
              {result.defects?.length > 0 && (
                <div className="p-3 border border-gray-200 rounded-lg">
                  <p className="text-xs font-medium text-gray-500 mb-2">Khuyết tật phát hiện</p>
                  <div className="flex flex-wrap gap-2">
                    {result.defects.map((d) => (
                      <span key={d} className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-full border border-red-100">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Reasoning */}
              {result.reasoning && (
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <p className="text-xs font-medium text-gray-500 mb-1">Lý do phân loại</p>
                  <p className="text-sm text-gray-700">{result.reasoning}</p>
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations?.length > 0 && (
                <div className="p-3 border border-green-100 bg-green-50 rounded-lg">
                  <p className="text-xs font-medium text-green-700 mb-1">Khuyến nghị</p>
                  {result.recommendations.map((r) => (
                    <p key={r} className="text-sm text-green-800">{r}</p>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <Camera className="h-12 w-12 text-gray-200" />
              <p className="mt-4 text-sm">Chưa có kết quả</p>
              <p className="text-xs mt-1">Tải ảnh nông sản để AI phân tích</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityPage;
