import { AlertTriangle, Camera, CheckCircle, Upload, XCircle } from 'lucide-react';
import { useState } from 'react';
import { qualityApi } from '../services/qualityApi';

const QualityPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
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
      const data = await qualityApi.checkQuality(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi kiểm tra chất lượng');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'grade_1':
        return 'text-green-600 bg-green-50';
      case 'grade_2':
        return 'text-yellow-600 bg-yellow-50';
      case 'grade_3':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getGradeName = (grade) => {
    switch (grade) {
      case 'grade_1':
        return 'Loại 1 - Chất lượng cao';
      case 'grade_2':
        return 'Loại 2 - Chất lượng trung bình';
      case 'grade_3':
        return 'Loại 3 - Chất lượng thấp';
      default:
        return grade;
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Kiểm tra chất lượng nông sản
        </h1>
        <p className="mt-2 text-gray-600">
          Upload ảnh nông sản để AI phân tích và đánh giá chất lượng
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Upload ảnh</h2>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            {preview ? (
              <div className="space-y-4">
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-64 mx-auto rounded"
                />
                <button
                  onClick={() => {
                    setPreview(null);
                    setSelectedFile(null);
                    setResult(null);
                  }}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Xóa ảnh
                </button>
              </div>
            ) : (
              <div>
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500"
                  >
                    <span>Chọn ảnh</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </label>
                  <p className="text-xs text-gray-500 mt-2">
                    PNG, JPG, JPEG tối đa 10MB
                  </p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!selectedFile || loading}
            className="mt-4 w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Đang phân tích...' : 'Kiểm tra chất lượng'}
          </button>
        </div>

        {/* Result Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Kết quả phân tích</h2>

          {result ? (
            <div className="space-y-4">
              {/* Quality Grade */}
              <div className={`p-4 rounded-lg ${getGradeColor(result.quality_grade)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Phân loại</p>
                    <p className="text-xl font-bold mt-1">
                      {getGradeName(result.quality_grade)}
                    </p>
                  </div>
                  {result.quality_grade === 'grade_1' && (
                    <CheckCircle className="h-8 w-8" />
                  )}
                  {result.quality_grade === 'grade_2' && (
                    <AlertTriangle className="h-8 w-8" />
                  )}
                  {result.quality_grade === 'grade_3' && (
                    <XCircle className="h-8 w-8" />
                  )}
                </div>
                <p className="text-sm mt-2">
                  Độ tin cậy: {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>

              {/* Price Range */}
              <div className="border rounded-lg p-4">
                <p className="text-sm font-medium text-gray-700">Giá đề xuất</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {result.suggested_price_range.min.toLocaleString()} -{' '}
                  {result.suggested_price_range.max.toLocaleString()} đ/kg
                </p>
              </div>

              {/* Defects */}
              {result.defects && result.defects.length > 0 && (
                <div className="border rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Khuyết tật phát hiện
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    {result.defects.map((defect, index) => (
                      <li key={index} className="text-sm text-gray-600">
                        {defect}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="border rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Khuyến nghị
                  </p>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="text-primary-600 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              <Camera className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4">Chưa có kết quả phân tích</p>
              <p className="text-sm mt-2">Upload ảnh để bắt đầu</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityPage;
