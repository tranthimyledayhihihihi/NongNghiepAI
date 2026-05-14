import {
  AlertTriangle,
  Camera,
  CheckCircle,
  FileImage,
  Image as ImageIcon,
  Sparkles,
  Upload,
  XCircle,
} from 'lucide-react';
import { useRef, useState } from 'react';
import { getApiErrorMessage } from '../services/api';
import { qualityApi } from '../services/qualityApi';

const gradeMeta = {
  grade_1: {
    label: 'Hang A',
    description: 'Chat luong cao',
    icon: CheckCircle,
    color: 'from-green-700 to-green-900',
  },
  grade_2: {
    label: 'Hang B',
    description: 'Chat luong trung binh',
    icon: AlertTriangle,
    color: 'from-yellow-600 to-yellow-800',
  },
  grade_3: {
    label: 'Hang C',
    description: 'Can xu ly hoac che bien',
    icon: XCircle,
    color: 'from-red-700 to-red-900',
  },
};

const QualityCheckPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [cropName, setCropName] = useState('ca chua');
  const [region, setRegion] = useState('Ha Noi');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const analyzeFile = async (file) => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await qualityApi.checkQuality(file, cropName, region);
      setAnalysisResult(result);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Khong the phan tich anh'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const loadFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setSelectedFile(file);
    setSelectedImage(URL.createObjectURL(file));
    analyzeFile(file);
  };

  const handleFileSelect = (event) => {
    loadFile(event.target.files[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    loadFile(event.dataTransfer.files[0]);
  };

  const handleReset = () => {
    setSelectedImage(null);
    setSelectedFile(null);
    setAnalysisResult(null);
    setError(null);
    setIsAnalyzing(false);
  };

  const meta = gradeMeta[analysisResult?.quality_grade] || gradeMeta.grade_1;
  const ResultIcon = meta.icon;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Kiem Tra Chat Luong</h1>
        <p className="text-gray-600">
          Tai anh nong san len va phan tich bang API backend /api/quality/check.
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <ImageIcon className="w-6 h-6 text-green-700" />
              <h2 className="text-xl font-bold text-gray-900">Hinh Anh Dau Vao</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Loai nong san
                </label>
                <select
                  value={cropName}
                  onChange={(event) => setCropName(event.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="ca chua">Ca chua</option>
                  <option value="dua chuot">Dua chuot</option>
                  <option value="rau muong">Rau muong</option>
                  <option value="lua">Lua</option>
                  <option value="ot">Ot</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Khu vuc
                </label>
                <select
                  value={region}
                  onChange={(event) => setRegion(event.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="Ha Noi">Ha Noi</option>
                  <option value="TP.HCM">TP.HCM</option>
                  <option value="Da Nang">Da Nang</option>
                  <option value="Can Tho">Can Tho</option>
                </select>
              </div>
            </div>

            {!selectedImage ? (
              <div
                onDragOver={(event) => event.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center hover:border-green-500 hover:bg-green-50 transition cursor-pointer"
              >
                <div className="flex flex-col items-center space-y-4">
                  <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                    <Upload className="w-10 h-10 text-green-700" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">
                      Keo tha anh vao day
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      hoac nhan de chon tu thiet bi
                    </p>
                    <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center space-x-1">
                        <FileImage className="w-4 h-4" />
                        <span>PNG</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <FileImage className="w-4 h-4" />
                        <span>JPG</span>
                      </span>
                    </div>
                  </div>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-2xl overflow-hidden bg-gray-100">
                  <img src={selectedImage} alt="Selected crop" className="w-full h-96 object-cover" />
                  {isAnalyzing && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      <div className="text-center text-white">
                        <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                        <p className="font-medium">Dang phan tich...</p>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleReset}
                    className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl hover:border-red-500 hover:text-red-500 transition font-medium"
                  >
                    Tai Anh Khac
                  </button>
                  <button
                    onClick={() => analyzeFile(selectedFile)}
                    disabled={isAnalyzing}
                    className="flex-1 px-6 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium disabled:bg-gray-300"
                  >
                    Phan Tich Lai
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700">
              {error}
            </div>
          )}

          {analysisResult ? (
            <div className={`bg-gradient-to-br ${meta.color} rounded-2xl p-6 text-white`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5" />
                  <span className="text-sm font-medium">KET QUA TU API</span>
                </div>
                <ResultIcon className="w-6 h-6" />
              </div>

              <div className="mb-6">
                <div className="text-sm opacity-80 mb-2">Phan loai san pham</div>
                <div className="text-4xl font-bold mb-2">{meta.label}</div>
                <div className="text-sm opacity-90">{meta.description}</div>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-between p-3 bg-black/15 rounded-xl">
                  <span className="text-sm">Loi phat hien</span>
                  <span className="font-bold">
                    {analysisResult.defects?.length ? analysisResult.defects.length : 0}
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-black/15 rounded-xl">
                  <span className="text-sm">Do tin cay</span>
                  <span className="font-bold">
                    {(analysisResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="border-t border-white/25 pt-4">
                <div className="text-sm opacity-80 mb-2">Gia tri uoc tinh</div>
                <div className="text-3xl font-bold">
                  {analysisResult.suggested_price.toLocaleString()} VND/kg
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-300 p-8 text-center">
              <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <Camera className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">Cho Phan Tich</h3>
              <p className="text-sm text-gray-600">
                Tai anh len de frontend goi backend va hien thi ket qua.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityCheckPage;
