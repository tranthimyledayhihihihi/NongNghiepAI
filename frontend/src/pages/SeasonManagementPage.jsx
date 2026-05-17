import {
  Calendar,
  CheckCircle,
  Clock,
  Edit,
  Leaf,
  MapPin,
  Package,
  Plus,
  Search,
  Trash2,
  TrendingUp,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { EmptyState, InlineLoading, PageError } from '../components/StatusState';
import { getApiErrorMessage } from '../services/api';
import { harvestApi } from '../services/harvestApi';

const fallbackImages = [
  'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&h=400&fit=crop',
  'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=600&h=400&fit=crop',
  'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600&h=400&fit=crop',
  'https://images.unsplash.com/photo-1526318472351-c75fcf070305?w=600&h=400&fit=crop',
];

const formatDate = (value) => {
  if (!value) return '-';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString('vi-VN');
};

const daysBetween = (from, to) => {
  const start = new Date(from);
  const end = new Date(to);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 0;
  return Math.ceil((end - start) / 86400000);
};

const deriveSeason = (schedule, index) => {
  const totalDays = Math.max(daysBetween(schedule.planting_date, schedule.expected_harvest_date), 1);
  const elapsedDays = Math.max(daysBetween(schedule.planting_date, new Date()), 0);
  const daysRemaining = Math.max(daysBetween(new Date(), schedule.expected_harvest_date), 0);
  const completed = Boolean(schedule.actual_harvest_date);
  const harvesting = !completed && daysRemaining <= 14;
  const status = completed ? 'completed' : harvesting ? 'harvesting' : 'growing';

  return {
    id: schedule.schedule_id,
    cropName: schedule.crop_name || 'Nông sản',
    cropImage: schedule.crop_image || fallbackImages[index % fallbackImages.length],
    region: schedule.region || '-',
    areaSize: Number(schedule.area_size || 0),
    unit: schedule.unit || 'hectare',
    plantingDate: schedule.planting_date,
    expectedHarvestDate: schedule.expected_harvest_date,
    actualHarvestDate: schedule.actual_harvest_date,
    estimatedYield: Number(schedule.estimated_yield_kg || 0),
    actualYield: Number(schedule.actual_yield_kg || 0),
    fertilizer: schedule.fertilizer_used || '-',
    pesticide: schedule.pesticide_used || '-',
    notes: schedule.notes || '',
    status,
    statusText: completed ? 'Đã thu hoạch' : harvesting ? 'Sắp thu hoạch' : 'Đang trồng',
    statusColor: completed
      ? 'bg-gray-100 text-gray-700'
      : harvesting
        ? 'bg-amber-100 text-amber-700'
        : 'bg-green-100 text-green-700',
    progress: completed ? 100 : Math.min(Math.round((elapsedDays / totalDays) * 100), 99),
    daysRemaining,
  };
};

const initialForm = {
  crop_name: '',
  region: '',
  planting_date: '',
  expected_harvest_date: '',
  area_size: '',
  estimated_yield_kg: '',
  notes: '',
};

const SeasonManagementPage = () => {
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState(initialForm);
  const [seasons, setSeasons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const loadSeasons = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await harvestApi.getMySchedules(100);
      setSeasons((data.schedules || []).map(deriveSeason));
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tải danh sách mùa vụ'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSeasons();
  }, []);

  const filteredSeasons = useMemo(
    () =>
      seasons.filter((season) => {
        const matchesStatus = filterStatus === 'all' || season.status === filterStatus;
        const query = searchQuery.trim().toLowerCase();
        const matchesSearch =
          !query ||
          season.cropName.toLowerCase().includes(query) ||
          season.region.toLowerCase().includes(query);
        return matchesStatus && matchesSearch;
      }),
    [filterStatus, searchQuery, seasons]
  );

  const stats = useMemo(
    () => ({
      total: seasons.length,
      growing: seasons.filter((item) => item.status === 'growing').length,
      harvesting: seasons.filter((item) => item.status === 'harvesting').length,
      completed: seasons.filter((item) => item.status === 'completed').length,
      totalArea: seasons.reduce((sum, item) => sum + item.areaSize, 0),
      totalYield: seasons.reduce((sum, item) => sum + (item.actualYield || item.estimatedYield), 0),
    }),
    [seasons]
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await harvestApi.createSchedule({
        ...formData,
        expected_harvest_date: formData.expected_harvest_date || null,
        area_size: formData.area_size ? Number(formData.area_size) : null,
        estimated_yield_kg: formData.estimated_yield_kg ? Number(formData.estimated_yield_kg) : null,
      });
      setFormData(initialForm);
      setShowAddModal(false);
      await loadSeasons();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tạo mùa vụ'));
    } finally {
      setSaving(false);
    }
  };

  const getStatusIcon = (status) => {
    if (status === 'completed') return <CheckCircle className="h-5 w-5" />;
    if (status === 'harvesting') return <Clock className="h-5 w-5" />;
    return <Leaf className="h-5 w-5" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-green-700">HarvestSchedule API</p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Quản lý mùa vụ</h1>
          <p className="mt-2 text-gray-600">Dữ liệu được lấy từ backend theo tài khoản đang đăng nhập.</p>
        </div>
        <button
          type="button"
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800"
        >
          <Plus className="h-5 w-5" />
          Thêm mùa vụ
        </button>
      </div>

      {error && <PageError message={error} onRetry={loadSeasons} />}
      {loading && <InlineLoading text="Đang tải mùa vụ từ backend..." />}

      {!loading && (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[
              ['Đang trồng', stats.growing, Leaf, 'text-green-700 bg-green-50'],
              ['Sắp thu hoạch', stats.harvesting, Clock, 'text-amber-700 bg-amber-50'],
              ['Tổng diện tích', `${stats.totalArea.toFixed(1)} ha`, Package, 'text-blue-700 bg-blue-50'],
              ['Tổng sản lượng', `${(stats.totalYield / 1000).toFixed(1)}t`, TrendingUp, 'text-purple-700 bg-purple-50'],
            ].map(([label, value, Icon, color]) => (
              <div key={label} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
                <div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-lg ${color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="text-sm text-gray-600">{label}</div>
                <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
              </div>
            ))}
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="relative w-full lg:max-w-md">
                <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Tìm theo cây trồng hoặc khu vực..."
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  ['all', `Tất cả (${stats.total})`],
                  ['growing', `Đang trồng (${stats.growing})`],
                  ['harvesting', `Sắp thu hoạch (${stats.harvesting})`],
                  ['completed', `Hoàn thành (${stats.completed})`],
                ].map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setFilterStatus(value)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                      filterStatus === value ? 'bg-green-700 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {filteredSeasons.length ? (
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {filteredSeasons.map((season) => (
                <article key={season.id} className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
                  <div className="relative h-44">
                    <img src={season.cropImage} alt={season.cropName} className="h-full w-full object-cover" />
                    <div className={`absolute left-3 top-3 inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-bold ${season.statusColor}`}>
                      {getStatusIcon(season.status)}
                      {season.statusText}
                    </div>
                  </div>

                  <div className="space-y-4 p-5">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{season.cropName}</h2>
                      <p className="mt-1 flex items-center gap-2 text-sm text-gray-600">
                        <MapPin className="h-4 w-4" />
                        {season.region}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-gray-500">Ngày gieo</div>
                        <div className="font-semibold text-gray-900">{formatDate(season.plantingDate)}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Thu hoạch dự kiến</div>
                        <div className="font-semibold text-gray-900">{formatDate(season.expectedHarvestDate)}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Diện tích</div>
                        <div className="font-semibold text-gray-900">{season.areaSize || '-'} {season.unit}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Sản lượng</div>
                        <div className="font-semibold text-gray-900">{season.actualYield || season.estimatedYield || '-'} kg</div>
                      </div>
                    </div>

                    {season.status !== 'completed' && (
                      <div>
                        <div className="mb-2 flex justify-between text-sm">
                          <span className="text-gray-600">Tiến độ</span>
                          <span className="font-semibold text-gray-900">{season.progress}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-gray-200">
                          <div
                            className={`h-2 rounded-full ${season.status === 'harvesting' ? 'bg-amber-500' : 'bg-green-600'}`}
                            style={{ width: `${season.progress}%` }}
                          />
                        </div>
                        <p className="mt-2 text-xs text-gray-500">Còn {season.daysRemaining} ngày đến thu hoạch</p>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <button type="button" className="flex-1 rounded-lg bg-green-700 px-4 py-2 text-sm font-semibold text-white hover:bg-green-800">
                        Chi tiết
                      </button>
                      <button type="button" className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-50" aria-label="Sửa">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button type="button" className="rounded-lg border border-red-200 p-2 text-red-600 hover:bg-red-50" aria-label="Xóa">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState
              title="Chưa có mùa vụ"
              description="Tạo mùa vụ mới để trang này hiển thị dữ liệu từ HarvestSchedule."
              action={
                <button
                  type="button"
                  onClick={() => setShowAddModal(true)}
                  className="rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800"
                >
                  Thêm mùa vụ
                </button>
              }
            />
          )}
        </>
      )}

      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form onSubmit={handleSubmit} className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Thêm mùa vụ</h2>
              <button type="button" onClick={() => setShowAddModal(false)} className="rounded-lg p-2 text-gray-500 hover:bg-gray-100">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {[
                ['crop_name', 'Tên cây trồng', 'text', true],
                ['region', 'Khu vực', 'text', true],
                ['planting_date', 'Ngày gieo', 'date', true],
                ['expected_harvest_date', 'Ngày thu hoạch dự kiến', 'date', false],
                ['area_size', 'Diện tích (ha)', 'number', false],
                ['estimated_yield_kg', 'Sản lượng dự kiến (kg)', 'number', false],
              ].map(([key, label, type, required]) => (
                <label key={key} className="block">
                  <span className="mb-2 block text-sm font-medium text-gray-700">{label}</span>
                  <input
                    type={type}
                    required={required}
                    min={type === 'number' ? '0' : undefined}
                    step={type === 'number' ? '0.1' : undefined}
                    value={formData[key]}
                    onChange={(event) => setFormData((current) => ({ ...current, [key]: event.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                  />
                </label>
              ))}
              <label className="block md:col-span-2">
                <span className="mb-2 block text-sm font-medium text-gray-700">Ghi chú</span>
                <textarea
                  value={formData.notes}
                  onChange={(event) => setFormData((current) => ({ ...current, notes: event.target.value }))}
                  rows={3}
                  className="w-full rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                />
              </label>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button type="button" onClick={() => setShowAddModal(false)} className="rounded-lg border border-gray-300 px-5 py-3 font-medium text-gray-700 hover:bg-gray-50">
                Hủy
              </button>
              <button type="submit" disabled={saving} className="rounded-lg bg-green-700 px-5 py-3 font-semibold text-white hover:bg-green-800 disabled:opacity-60">
                {saving ? 'Đang lưu...' : 'Lưu mùa vụ'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default SeasonManagementPage;
