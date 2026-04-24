import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const QualityResult = ({ result }) => {
  if (!result) {
    return (
      <div className="text-center text-gray-500 py-12">
        <AlertTriangle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p>Chưa có kết quả phân tích</p>
        <p className="text-sm mt-2">Upload ảnh để bắt đầu</p>
      </div>
    );
  }

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

  const getGradeIcon = (grade) => {
    switch (grade) {
      case 'grade_1':
        return <CheckCircle className="h-8 w-8" />;
      case 'grade_2':
        return <AlertTriangle className="h-8 w-8" />;
      case 'grade_3':
        return <XCircle className="h-8 w-8" />;
      default:
        return null;
    }
  };

  return (
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
          {getGradeIcon(result.quality_grade)}
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
            Khuyết tật phát hiện ({result.defects.length})
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
  );
};

export default QualityResult;
