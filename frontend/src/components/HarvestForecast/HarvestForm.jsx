
const HarvestForm = ({ formData, setFormData, onSubmit, loading }) => {
  const crops = ['Cà chua', 'Dưa chuột', 'Rau muống', 'Cải xanh', 'Ớt'];
  const regions = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng'];

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Loại cây trồng
        </label>
        <select
          value={formData.crop}
          onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
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
          Khu vực
        </label>
        <select
          value={formData.region}
          onChange={(e) => setFormData({ ...formData, region: e.target.value })}
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {regions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ngày xuống giống
        </label>
        <input
          type="date"
          value={formData.plantingDate}
          onChange={(e) =>
            setFormData({ ...formData, plantingDate: e.target.value })
          }
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Đang dự báo...' : 'Dự báo thu hoạch'}
      </button>
    </form>
  );
};

export default HarvestForm;
