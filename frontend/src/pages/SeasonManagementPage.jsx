import {
  Calendar,
  CheckCircle,
  ChevronRight,
  Clock,
  Edit,
  Leaf,
  MapPin,
  MoreVertical,
  Package,
  Plus,
  Search,
  Trash2,
  TrendingUp,
  XCircle
} from 'lucide-react';
import { useState } from 'react';

const SeasonManagementPage = () => {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'growing', 'harvesting', 'completed'
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // Season Data (from HarvestSchedule table)
  const seasons = [
    {
      id: 1,
      cropName: 'Lúa OM 5451',
      cropImage: 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&h=400&fit=crop',
      region: 'An Giang',
      areaSize: 2.5,
      unit: 'hecta',
      plantingDate: '2024-08-15',
      expectedHarvestDate: '2024-11-20',
      actualHarvestDate: null,
      estimatedYield: 12500,
      actualYield: null,
      status: 'growing',
      statusText: 'Đang trồng',
      statusColor: 'bg-green-100 text-green-700',
      progress: 65,
      daysRemaining: 28,
      fertilizer: 'NPK 16-16-8',
      pesticide: 'Không sử dụng',
      notes: 'Thời tiết thuận lợi, cây phát triển tốt'
    },
    {
      id: 2,
      cropName: 'Cà phê Robusta',
      cropImage: 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=400&fit=crop',
      region: 'Đắk Lắk',
      areaSize: 3.2,
      unit: 'hecta',
      plantingDate: '2024-09-01',
      expectedHarvestDate: '2024-12-15',
      actualHarvestDate: null,
      estimatedYield: 8500,
      actualYield: null,
      status: 'harvesting',
      statusText: 'Sắp thu hoạch',
      statusColor: 'bg-yellow-100 text-yellow-700',
      progress: 92,
      daysRemaining: 7,
      fertilizer: 'Phân hữu cơ',
      pesticide: 'Thuốc trừ sâu sinh học',
      notes: 'Chuẩn bị nhân lực thu hoạch'
    },
    {
      id: 3,
      cropName: 'Hồ tiêu',
      cropImage: 'https://images.unsplash.com/photo-1592419044706-39796d40f98c?w=600&h=400&fit=crop',
      region: 'Bà Rịa - Vũng Tàu',
      areaSize: 1.8,
      unit: 'hecta',
      plantingDate: '2024-06-10',
      expectedHarvestDate: '2024-10-15',
      actualHarvestDate: '2024-10-18',
      estimatedYield: 4200,
      actualYield: 4500,
      status: 'completed',
      statusText: 'Đã thu hoạch',
      statusColor: 'bg-gray-100 text-gray-700',
      progress: 100,
      daysRemaining: 0,
      fertilizer: 'NPK 20-20-15',
      pesticide: 'Thuốc trừ nấm',
      notes: 'Thu hoạch thành công, sản lượng vượt dự kiến'
    },
    {
      id: 4,
      cropName: 'Sầu riêng Monthong',
      cropImage: 'https://images.unsplash.com/photo-1583575117096-2a19f9d8f6f5?w=600&h=400&fit=crop',
      region: 'Tiền Giang',
      areaSize: 2.0,
      unit: 'hecta',
      plantingDate: '2024-07-20',
      expectedHarvestDate: '2024-11-30',
      actualHarvestDate: null,
      estimatedYield: 15000,
      actualYield: null,
      status: 'growing',
      statusText: 'Đang trồng',
      statusColor: 'bg-green-100 text-green-700',
      progress: 45,
      daysRemaining: 42,
      fertilizer: 'Phân bón lá',
      pesticide: 'Không sử dụng',
      notes: 'Cần theo dõi sâu đục thân'
    },
    {
      id: 5,
      cropName: 'Ngô lai',
      cropImage: 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600&h=400&fit=crop',
      region: 'Đồng Nai',
      areaSize: 1.5,
      unit: 'hecta',
      plantingDate: '2024-05-01',
      expectedHarvestDate: '2024-08-15',
      actualHarvestDate: '2024-08-12',
      estimatedYield: 6000,
      actualYield: 5800,
      status: 'completed',
      statusText: 'Đã thu hoạch',
      statusColor: 'bg-gray-100 text-gray-700',
      progress: 100,
      daysRemaining: 0,
      fertilizer: 'Urê',
      pesticide: 'Thuốc trừ sâu',
      notes: 'Hoàn thành đúng kế hoạch'
    },
    {
      id: 6,
      cropName: 'Thanh long ruột đỏ',
      cropImage: 'https://images.unsplash.com/photo-1526318472351-c75fcf070305?w=600&h=400&fit=crop',
      region: 'Bình Thuận',
      areaSize: 2.2,
      unit: 'hecta',
      plantingDate: '2024-08-01',
      expectedHarvestDate: '2024-11-10',
      actualHarvestDate: null,
      estimatedYield: 18000,
      actualYield: null,
      status: 'harvesting',
      statusText: 'Sắp thu hoạch',
      statusColor: 'bg-yellow-100 text-yellow-700',
      progress: 88,
      daysRemaining: 12,
      fertilizer: 'NPK 15-15-15',
      pesticide: 'Thuốc trừ bệnh',
      notes: 'Chất lượng quả tốt, giá thị trường ổn định'
    }
  ];

  // Filter seasons
  const filteredSeasons = seasons.filter(season => {
    const matchesStatus = filterStatus === 'all' || season.status === filterStatus;
    const matchesSearch = season.cropName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      season.region.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  // Statistics
  const stats = {
    total: seasons.length,
    growing: seasons.filter(s => s.status === 'growing').length,
    harvesting: seasons.filter(s => s.status === 'harvesting').length,
    completed: seasons.filter(s => s.status === 'completed').length,
    totalArea: seasons.reduce((sum, s) => sum + s.areaSize, 0),
    totalYield: seasons.reduce((sum, s) => sum + (s.actualYield || s.estimatedYield), 0)
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'growing':
        return <Leaf className="w-5 h-5" />;
      case 'harvesting':
        return <Clock className="w-5 h-5" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5" />;
      default:
        return <XCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Quản lý Mùa vụ
          </h1>
          <p className="text-gray-600">
            Theo dõi và quản lý tất cả mùa vụ canh tác của bạn
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-6 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium"
        >
          <Plus className="w-5 h-5" />
          <span>Thêm Mùa vụ</span>
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl border border-green-200 p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-sm text-gray-600">Đang trồng</div>
              <div className="text-2xl font-bold text-gray-900">{stats.growing}</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl border border-yellow-200 p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-12 h-12 bg-yellow-600 rounded-xl flex items-center justify-center">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-sm text-gray-600">Sắp thu hoạch</div>
              <div className="text-2xl font-bold text-gray-900">{stats.harvesting}</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl border border-blue-200 p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <Package className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-sm text-gray-600">Tổng diện tích</div>
              <div className="text-2xl font-bold text-gray-900">{stats.totalArea.toFixed(1)} ha</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl border border-purple-200 p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-sm text-gray-600">Tổng sản lượng</div>
              <div className="text-2xl font-bold text-gray-900">{(stats.totalYield / 1000).toFixed(1)}t</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Tìm kiếm theo tên cây trồng hoặc khu vực..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${filterStatus === 'all'
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              Tất cả ({stats.total})
            </button>
            <button
              onClick={() => setFilterStatus('growing')}
              className={`px-4 py-2 rounded-lg font-medium transition ${filterStatus === 'growing'
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              Đang trồng ({stats.growing})
            </button>
            <button
              onClick={() => setFilterStatus('harvesting')}
              className={`px-4 py-2 rounded-lg font-medium transition ${filterStatus === 'harvesting'
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              Sắp thu hoạch ({stats.harvesting})
            </button>
            <button
              onClick={() => setFilterStatus('completed')}
              className={`px-4 py-2 rounded-lg font-medium transition ${filterStatus === 'completed'
                ? 'bg-green-700 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
            >
              Đã hoàn thành ({stats.completed})
            </button>
          </div>
        </div>
      </div>

      {/* Seasons Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSeasons.map((season) => (
          <div
            key={season.id}
            className="bg-white rounded-2xl shadow-sm border-2 border-gray-200 overflow-hidden hover:shadow-lg hover:border-green-500 transition"
          >
            {/* Image */}
            <div className="relative h-48">
              <img
                src={season.cropImage}
                alt={season.cropName}
                className="w-full h-full object-cover"
              />
              <div className={`absolute top-3 left-3 ${season.statusColor} px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1`}>
                {getStatusIcon(season.status)}
                <span>{season.statusText}</span>
              </div>
              <button className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full flex items-center justify-center hover:bg-gray-100 transition">
                <MoreVertical className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {season.cropName}
              </h3>

              {/* Info Grid */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>Khu vực</span>
                  </div>
                  <span className="font-medium text-gray-900">{season.region}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Package className="w-4 h-4" />
                    <span>Diện tích</span>
                  </div>
                  <span className="font-medium text-gray-900">{season.areaSize} {season.unit}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>Ngày gieo</span>
                  </div>
                  <span className="font-medium text-gray-900">
                    {new Date(season.plantingDate).toLocaleDateString('vi-VN')}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>Sản lượng</span>
                  </div>
                  <span className="font-medium text-gray-900">
                    {season.actualYield || season.estimatedYield} kg
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              {season.status !== 'completed' && (
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Tiến độ</span>
                    <span className="font-bold text-gray-900">{season.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${season.status === 'growing' ? 'bg-green-500' : 'bg-yellow-500'
                        }`}
                      style={{ width: `${season.progress}%` }}
                    ></div>
                  </div>
                  {season.daysRemaining > 0 && (
                    <p className="text-xs text-gray-500 mt-2">
                      Còn {season.daysRemaining} ngày đến thu hoạch
                    </p>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition">
                  <span className="text-sm font-medium">Chi tiết</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
                <button className="w-10 h-10 border border-gray-300 rounded-lg flex items-center justify-center hover:bg-gray-50 transition">
                  <Edit className="w-4 h-4 text-gray-600" />
                </button>
                <button className="w-10 h-10 border border-red-300 rounded-lg flex items-center justify-center hover:bg-red-50 transition">
                  <Trash2 className="w-4 h-4 text-red-600" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredSeasons.length === 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Leaf className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Không tìm thấy mùa vụ
          </h3>
          <p className="text-gray-600 mb-6">
            Thử thay đổi bộ lọc hoặc tìm kiếm với từ khóa khác
          </p>
          <button
            onClick={() => {
              setFilterStatus('all');
              setSearchQuery('');
            }}
            className="px-6 py-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition font-medium"
          >
            Xóa bộ lọc
          </button>
        </div>
      )}
    </div>
  );
};

export default SeasonManagementPage;
