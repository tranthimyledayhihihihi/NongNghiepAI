import { AlertTriangle, Camera, CheckCircle, Upload, XCircle } from 'lucide-react';
import { useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { qualityApi } from '../services/qualityApi';

const crops = ['ca chua', 'dua chuot', 'rau muong', 'cai xanh', 'ot', 'lua'];
const regions = ['Ha Noi', 'TP.HCM', 'Da Nang', 'Can Tho', 'Hai Phong'];

const gradeLabels = {
  grade_1: 'Loai 1 - Chat luong cao',
  grade_2: 'Loai 2 - Chat luong trung binh',
  grade_3: 'Loai 3 - Chat luong thap',
};

const QualityPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [cropName, setCropName] = useState('ca chua');
  const [region, setRegion] = useState('Ha Noi');
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
      setError('Vui long chon anh');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await qualityApi.checkQuality(selectedFile, cropName, region);
      setResult(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Loi khi kiem tra chat luong'));
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

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'grade_1':
        return 'text-green-600 bg-green-50';
      case 'grade_2':
        return 'text-yellow-700 bg-yellow-50';
      case 'grade_3':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Kiem tra chat luong nong san
        </h1>
        <p className="mt-2 text-gray-600">
          Upload anh de frontend goi API /api/quality/check cua backend.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Upload anh</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Loai nong san
              </label>
              <select
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {crops.map((crop) => (
                  <option key={crop} value={crop}>
                    {crop}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Khu vuc
              </label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {regions.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            {preview ? (
              <div className="space-y-4">
                <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded" />
                <button onClick={clearImage} className="text-sm text-red-600 hover:text-red-700">
                  Xoa anh
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
                    <span>Chon anh</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </label>
                  <p className="text-xs text-gray-500 mt-2">PNG, JPG, JPEG toi da 10MB</p>
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
            {loading ? 'Dang phan tich...' : 'Kiem tra chat luong'}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Ket qua phan tich</h2>

          {result ? (
            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${getGradeColor(result.quality_grade)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Phan loai</p>
                    <p className="text-xl font-bold mt-1">
                      {gradeLabels[result.quality_grade] || result.quality_grade}
                    </p>
                  </div>
                  {result.quality_grade === 'grade_1' && <CheckCircle className="h-8 w-8" />}
                  {result.quality_grade === 'grade_2' && <AlertTriangle className="h-8 w-8" />}
                  {result.quality_grade === 'grade_3' && <XCircle className="h-8 w-8" />}
                </div>
                <p className="text-sm mt-2">
                  Do tin cay: {(result.confidence * 100).toFixed(1)}%
                </p>
              </div>

              <div className="border rounded-lg p-4">
                <p className="text-sm font-medium text-gray-700">Gia de xuat</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {result.suggested_price_range.min.toLocaleString()} -{' '}
                  {result.suggested_price_range.max.toLocaleString()} d/kg
                </p>
              </div>

              {result.defects?.length > 0 && (
                <div className="border rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Khuyet tat phat hien</p>
                  <ul className="list-disc list-inside space-y-1">
                    {result.defects.map((defect) => (
                      <li key={defect} className="text-sm text-gray-600">
                        {defect}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.recommendations?.length > 0 && (
                <div className="border rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Khuyen nghi</p>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec) => (
                      <li key={rec} className="text-sm text-gray-600">
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
              <p className="mt-4">Chua co ket qua phan tich</p>
              <p className="text-sm mt-2">Upload anh de goi API backend</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityPage;
