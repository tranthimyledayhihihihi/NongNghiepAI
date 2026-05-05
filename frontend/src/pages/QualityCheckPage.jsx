import {
  Camera,
  CheckCircle,
  Download,
  FileImage,
  Image as ImageIcon,
  Sparkles,
  TrendingUp,
  Upload
} from 'lucide-react';
import { useRef, useState } from 'react';

const QualityCheckPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const fileInputRef = useRef(null);

  // Previous quality checks
  const previousChecks = [
    {
      id: 1,
      image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop',
      name: 'Cà phê Robusta',
      date: '24 thg 8, 2023',
      grade: 'HẠNG A',
      gradeColor: 'bg-green-500'
    },
    {
      id: 2,
      image: 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&h=300&fit=crop',
      name: 'Ớt hiểm đỏ',
      date: '22 thg 8, 2023',
      grade: 'HẠNG B',
      gradeColor: 'bg-yellow-500'
    },
    {
      id: 3,
      image: 'https://images.unsplash.com/photo-1596040033229-a0b3b7e5e8e8?w=400&h=300&fit=crop',
      name: 'Tiêu đen',
      date: '19 thg 8, 2023',
      grade: 'HẠNG A',
      gradeColor: 'bg-green-500'
    },
    {
      id: 4,
      image: 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400&h=300&fit=crop',
      name: 'Xoài Hòa Lộc',
      date: '15 thg 8, 2023',
      grade: 'HẠNG A',
      gradeColor: 'bg-green-500'
    }
  ];

  // Mock analysis result
  const mockResult = {
    grade: 'A',
    gradeName: 'Hạng A',
    gradeDescription: 'Xuất Khẩu Cao Cấp',
    confidence: 98.4,
    defects: 'Không có',
    price: 420000,
    priceUnit: 'VNĐ/kg',
    aiSystem: 'Hệ thống AI Sẵn Sàng',
    processingTime: '2 phút trước'
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        handleAnalyze();
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
        handleAnalyze();
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate API call
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisResult(mockResult);
    }, 2000);
  };

  const handleReset = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
    setIsAnalyzing(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Kiểm Tra Chất Lượng
        </h1>
        <p className="text-gray-600">
          Tải ảnh nông sản để phân giải cao để AI phát hiện lỗi và phân loại ngay lập tức.
        </p>
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Upload Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Upload Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <ImageIcon className="w-6 h-6 text-green-700" />
              <h2 className="text-xl font-bold text-gray-900">
                Hình Ảnh Đầu Vào
              </h2>
            </div>

            {!selectedImage ? (
              /* Upload Area */
              <div
                onDragOver={handleDragOver}
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
                      Kéo & thả ảnh thu hoạch vào đây
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      hoặc nhấn để chọn từ thiết bị
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
                      <span>TỐI ĐA 25MB</span>
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
              /* Image Preview */
              <div className="space-y-4">
                <div className="relative rounded-2xl overflow-hidden bg-gray-100">
                  <img
                    src={selectedImage}
                    alt="Selected crop"
                    className="w-full h-96 object-cover"
                  />
                  {isAnalyzing && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                      <div className="text-center text-white">
                        <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <p className="font-medium">Đang phân tích...</p>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleReset}
                    className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl hover:border-red-500 hover:text-red-500 transition font-medium"
                  >
                    Tải Ảnh Khác
                  </button>
                  {!analysisResult && !isAnalyzing && (
                    <button
                      onClick={handleAnalyze}
                      className="flex-1 px-6 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium"
                    >
                      Phân Tích Ngay
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Previous Checks */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                Các Lần Kiểm Tra Trước
              </h2>
              <button className="text-green-700 font-medium hover:text-green-800 text-sm">
                Xem tất cả →
              </button>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {previousChecks.map((check) => (
                <div
                  key={check.id}
                  className="group relative rounded-xl overflow-hidden cursor-pointer hover:shadow-lg transition"
                >
                  <div className="relative h-40">
                    <img
                      src={check.image}
                      alt={check.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-60"></div>
                    <div className={`absolute top-3 right-3 ${check.gradeColor} text-white px-3 py-1 rounded-full text-xs font-bold`}>
                      {check.grade}
                    </div>
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-3 text-white">
                    <div className="font-bold text-sm mb-1">{check.name}</div>
                    <div className="text-xs opacity-90">{check.date}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Analysis Result */}
        <div className="lg:col-span-1 space-y-6">
          {analysisResult ? (
            <>
              {/* Result Card */}
              <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-2xl p-6 text-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-5 h-5" />
                    <span className="text-sm font-medium">KẾT QUẢ PHÂN TÍCH</span>
                  </div>
                  <span className="text-xs bg-green-600 px-2 py-1 rounded-full">
                    {analysisResult.processingTime}
                  </span>
                </div>

                <div className="mb-6">
                  <div className="text-sm text-green-200 mb-2">Phân Loại Sản Phẩm</div>
                  <div className="text-4xl font-bold mb-2">
                    {analysisResult.gradeName}
                  </div>
                  <div className="text-green-100 text-sm">
                    {analysisResult.gradeDescription}
                  </div>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="flex items-center justify-between p-3 bg-green-800 rounded-xl">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5" />
                      <span className="text-sm">Lỗi Phát Hiện</span>
                    </div>
                    <span className="font-bold">{analysisResult.defects}</span>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-green-800 rounded-xl">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-5 h-5" />
                      <span className="text-sm">Độ Tin Cậy</span>
                    </div>
                    <span className="font-bold">{analysisResult.confidence}%</span>
                  </div>
                </div>

                <div className="border-t border-green-600 pt-4 mb-6">
                  <div className="text-sm text-green-200 mb-2">Giá Trị Ước Tính</div>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-3xl font-bold">
                      đ{analysisResult.price.toLocaleString()}
                    </span>
                    <span className="text-green-200">/{analysisResult.priceUnit.split('/')[1]}</span>
                  </div>
                </div>

                <button className="w-full bg-white text-green-800 py-3 rounded-xl font-bold hover:bg-green-50 transition flex items-center justify-center space-x-2">
                  <Download className="w-5 h-5" />
                  <span>Xuất Báo Cáo</span>
                </button>
              </div>

              {/* AI System Info */}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Sparkles className="w-5 h-5 text-green-700" />
                  <h3 className="font-bold text-gray-900">
                    {analysisResult.aiSystem}
                  </h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Model YOLOv8 được huấn luyện trên 50,000+ mẫu nông sản Việt Nam với độ chính xác 98.4%.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Độ chính xác</span>
                    <span className="font-bold text-gray-900">98.4%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '98.4%' }}></div>
                  </div>
                </div>
              </div>

              {/* Quality Standards */}
              <div className="bg-blue-50 rounded-2xl border border-blue-200 p-6">
                <h3 className="font-bold text-gray-900 mb-4">
                  Tiêu Chuẩn Phân Loại
                </h3>
                <div className="space-y-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs font-bold">A</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm">Hạng A</div>
                      <div className="text-xs text-gray-600">Xuất khẩu cao cấp, không lỗi</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs font-bold">B</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm">Hạng B</div>
                      <div className="text-xs text-gray-600">Thị trường nội địa, lỗi nhỏ</div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-white text-xs font-bold">C</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm">Hạng C</div>
                      <div className="text-xs text-gray-600">Chế biến, nhiều lỗi</div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            /* Placeholder when no result */
            <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-300 p-8 text-center">
              <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <Camera className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="font-bold text-gray-900 mb-2">
                Chờ Phân Tích
              </h3>
              <p className="text-sm text-gray-600">
                Tải lên hình ảnh nông sản để bắt đầu kiểm tra chất lượng bằng AI
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QualityCheckPage;
