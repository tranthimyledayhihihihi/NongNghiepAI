import {
  AlertTriangle,
  Bot,
  CalendarDays,
  CheckCircle2,
  Clock,
  CloudRain,
  CloudSun,
  Droplets,
  Loader2,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Sprout,
  Sun,
  Thermometer,
  Umbrella,
  Wind,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import DataSourceBadge from '../components/DataSourceBadge';
import { getApiErrorMessage } from '../services/api';
import { weatherApi } from '../services/weatherApi';

const regions = ['Ha Noi', 'TP.HCM', 'Da Nang', 'Can Tho', 'Lam Dong', 'Hai Phong'];
const crops = ['Lúa', 'Cà phê', 'Rau màu', 'Hồ tiêu', 'Cây ăn trái'];
const stages = ['Cây con', 'Sinh trưởng', 'Ra hoa', 'Làm đòng', 'Đậu trái', 'Thu hoạch'];

const severityStyles = {
  high: 'border-red-200 bg-red-50 text-red-800',
  medium: 'border-amber-200 bg-amber-50 text-amber-800',
  low: 'border-sky-200 bg-sky-50 text-sky-800',
};

const priorityStyles = {
  high: 'border-red-200 bg-red-50 text-red-800',
  medium: 'border-amber-200 bg-amber-50 text-amber-800',
  low: 'border-emerald-200 bg-emerald-50 text-emerald-800',
};

const formatNumber = (value, suffix = '', digits = 1) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/A';
  return `${Number(value).toFixed(digits)}${suffix}`;
};

const formatDate = (value) => {
  if (!value) return 'N/A';
  return new Date(value).toLocaleDateString('vi-VN', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
  });
};

const formatTime = (value) => {
  if (!value) return 'N/A';
  return new Date(value).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

const WeatherMetric = ({ icon: Icon, label, value, detail, tone = 'slate' }) => {
  const tones = {
    slate: 'bg-slate-50 text-slate-700 border-slate-200',
    sky: 'bg-sky-50 text-sky-700 border-sky-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rose: 'bg-rose-50 text-rose-700 border-rose-200',
  };

  return (
    <div className={`rounded-lg border p-4 ${tones[tone]}`}>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-600">{label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-950">{value}</p>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/80">
          <Icon className="h-5 w-5" />
        </span>
      </div>
      {detail && <p className="mt-3 text-sm leading-6 text-slate-600">{detail}</p>}
    </div>
  );
};

const ForecastPage = () => {
  const [region, setRegion] = useState('Ha Noi');
  const [cropName, setCropName] = useState('Lúa');
  const [growthStage, setGrowthStage] = useState('Làm đòng');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchWeather = useCallback(async ({ forceRefresh = false } = {}) => {
    setLoading(true);
    setError('');
    try {
      const payload = {
        region,
        cropName,
        growthStage,
        days: 7,
        includeHourly: true,
      };
      const result = forceRefresh
        ? await weatherApi.refreshAgricultureWeather(payload)
        : await weatherApi.getAgricultureWeather(payload);
      setData(result);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể tải dữ liệu thời tiết nông vụ'));
    } finally {
      setLoading(false);
    }
  }, [cropName, growthStage, region]);

  useEffect(() => {
    fetchWeather({ forceRefresh: true });
  }, [fetchWeather]);

  const current = data?.current;
  const topActions = useMemo(
    () => (data?.activity_recommendations || []).filter((item) => item.action_type !== 'crop_stage'),
    [data]
  );

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchWeather({ forceRefresh: true });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
            <CloudSun className="h-4 w-4" />
            Thời tiết nông vụ thông minh
          </div>
          <h1 className="mt-3 text-3xl font-bold text-slate-950">Dự báo thời tiết canh tác</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Theo dõi realtime, dự báo 7 ngày, cảnh báo rủi ro và khuyến nghị tưới, phun thuốc, bón phân, thu hoạch theo cây trồng.
          </p>
        </div>
        {current && (
          <div className="flex flex-wrap items-center gap-2">
            <DataSourceBadge data={current} />
            <span className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600">
              <Clock className="h-4 w-4" />
              {current.checked_at ? new Date(current.checked_at).toLocaleString('vi-VN') : 'Chưa rõ thời gian'}
            </span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="grid gap-4 md:grid-cols-4">
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Khu vực</span>
            <select
              value={region}
              onChange={(event) => setRegion(event.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100"
            >
              {regions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Cây trồng</span>
            <select
              value={cropName}
              onChange={(event) => setCropName(event.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100"
            >
              {crops.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Giai đoạn</span>
            <select
              value={growthStage}
              onChange={(event) => setGrowthStage(event.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-100"
            >
              {stages.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Cập nhật
            </button>
          </div>
        </div>
      </form>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {loading && !data && (
        <div className="flex min-h-[320px] items-center justify-center rounded-lg border border-slate-200 bg-white">
          <div className="text-center text-slate-600">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-700" />
            <p className="mt-3 text-sm font-medium">Đang tải dữ liệu thời tiết...</p>
          </div>
        </div>
      )}

      {data && current && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <WeatherMetric
              icon={Thermometer}
              label="Nhiệt độ"
              value={formatNumber(current.temperature, '°C')}
              detail={`${formatNumber(current.temp_min, '°C')} - ${formatNumber(current.temp_max, '°C')}`}
              tone="rose"
            />
            <WeatherMetric
              icon={Droplets}
              label="Độ ẩm"
              value={formatNumber(current.humidity, '%', 0)}
              detail="Theo dõi nấm bệnh khi vượt 85%"
              tone="sky"
            />
            <WeatherMetric
              icon={CloudRain}
              label="Mưa hiện tại"
              value={formatNumber(current.rainfall, ' mm')}
              detail="Ảnh hưởng tưới tiêu và phun thuốc"
              tone="emerald"
            />
            <WeatherMetric
              icon={Wind}
              label="Gió"
              value={formatNumber(current.wind_speed, ' km/h')}
              detail="Không phun thuốc khi vượt 25 km/h"
              tone="slate"
            />
            <WeatherMetric
              icon={Sun}
              label="UV"
              value={formatNumber(current.uv_index, '', 1)}
              detail="Che cây non khi UV cao"
              tone="amber"
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-3">
            <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm xl:col-span-2">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-950">Khuyến nghị AI/rule</h2>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-700">{data.ai_recommendation.summary}</p>
              <p className="mt-2 text-sm leading-6 text-slate-700">{data.ai_recommendation.risk_explanation}</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {data.ai_recommendation.action_plan.map((item) => (
                  <div key={item} className="rounded-lg border border-indigo-100 bg-indigo-50 p-3 text-sm leading-6 text-indigo-900">
                    {item}
                  </div>
                ))}
              </div>
              {data.ai_recommendation.crop_note && (
                <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm leading-6 text-emerald-800">
                  {data.ai_recommendation.crop_note}
                </div>
              )}
            </section>

            <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-emerald-700" />
                <h2 className="text-lg font-bold text-slate-950">Nguồn & xử lý</h2>
              </div>
              <div className="mt-4 space-y-3">
                {(data.data_flow || []).map((item, index) => (
                  <div key={item} className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-700">
                      {index + 1}
                    </span>
                    <p className="text-sm leading-6 text-slate-600">{item}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-700">
                {data.ai_recommendation.data_note}
              </div>
            </section>
          </div>

          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-600" />
                <h2 className="text-lg font-bold text-slate-950">Cảnh báo thời tiết nông nghiệp</h2>
              </div>
              <span className="rounded-lg border border-slate-200 px-3 py-1 text-sm font-semibold text-slate-600">
                {data.alerts.length} cảnh báo
              </span>
            </div>
            {data.alerts.length === 0 ? (
              <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-800">
                <CheckCircle2 className="h-5 w-5" />
                Chưa có cảnh báo lớn trong 7 ngày tới.
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {data.alerts.map((alert) => (
                  <article
                    key={`${alert.alert_type}-${alert.forecast_date}-${alert.title}`}
                    className={`rounded-lg border p-4 ${severityStyles[alert.severity] || severityStyles.medium}`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-bold">{alert.title}</h3>
                      <span className="rounded-full bg-white/80 px-2 py-1 text-xs font-semibold">
                        {alert.severity}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-6">{alert.message}</p>
                    <p className="mt-2 text-sm font-medium leading-6">{alert.recommendation}</p>
                    <p className="mt-3 text-xs font-semibold">{formatDate(alert.forecast_date)}</p>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Sprout className="h-5 w-5 text-emerald-700" />
              <h2 className="text-lg font-bold text-slate-950">Gợi ý lịch canh tác theo thời tiết</h2>
            </div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
              {topActions.map((item) => (
                <article
                  key={item.action_type}
                  className={`rounded-lg border p-4 ${priorityStyles[item.priority] || priorityStyles.medium}`}
                >
                  <h3 className="font-bold">{item.action}</h3>
                  <p className="mt-2 text-xl font-bold text-slate-950">{item.decision}</p>
                  <p className="mt-2 text-sm leading-6">{item.reason}</p>
                  {item.timing && <p className="mt-3 text-xs font-semibold uppercase">{item.timing}</p>}
                </article>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-sky-700" />
              <h2 className="text-lg font-bold text-slate-950">Dự báo 7 ngày</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
                  <tr>
                    <th className="px-3 py-3">Ngày</th>
                    <th className="px-3 py-3">Nhiệt độ</th>
                    <th className="px-3 py-3">Mưa</th>
                    <th className="px-3 py-3">Độ ẩm</th>
                    <th className="px-3 py-3">Gió</th>
                    <th className="px-3 py-3">Khuyến nghị</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.forecast.map((item) => (
                    <tr key={item.date} className="align-top">
                      <td className="px-3 py-3 font-semibold text-slate-900">
                        {item.day_label || formatDate(item.date)}
                        <span className="block text-xs font-normal text-slate-500">{formatDate(item.date)}</span>
                      </td>
                      <td className="px-3 py-3 text-slate-700">
                        {formatNumber(item.temp_min, '°C')} - {formatNumber(item.temp_max, '°C')}
                      </td>
                      <td className="px-3 py-3 text-slate-700">
                        {formatNumber(item.rainfall, ' mm')}
                        <span className="block text-xs text-slate-500">{formatNumber(item.rain_probability, '%', 0)}</span>
                      </td>
                      <td className="px-3 py-3 text-slate-700">{formatNumber(item.humidity, '%', 0)}</td>
                      <td className="px-3 py-3 text-slate-700">{formatNumber(item.wind_speed, ' km/h')}</td>
                      <td className="max-w-sm px-3 py-3 text-slate-700">{item.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <div className="grid gap-6 xl:grid-cols-3">
            <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm xl:col-span-2">
              <div className="mb-4 flex items-center gap-2">
                <Clock className="h-5 w-5 text-slate-700" />
                <h2 className="text-lg font-bold text-slate-950">24 giờ tới</h2>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {(data.hourly_forecast || []).slice(0, 8).map((item) => (
                  <article key={item.forecast_at || item.time} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <div className="flex items-center justify-between">
                      <p className="font-bold text-slate-900">{formatTime(item.forecast_at || item.time)}</p>
                      <Umbrella className="h-4 w-4 text-sky-700" />
                    </div>
                    <p className="mt-2 text-sm text-slate-600">{formatNumber(item.temperature, '°C')}</p>
                    <p className="text-sm text-slate-600">{formatNumber(item.rain_probability, '%', 0)} mưa</p>
                    <p className="mt-2 text-xs leading-5 text-slate-500">{item.recommendation}</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-700" />
                <h2 className="text-lg font-bold text-slate-950">Ý nghĩa nông nghiệp</h2>
              </div>
              <div className="space-y-3">
                {(current.agriculture_insights || []).map((item) => (
                  <div key={item.metric} className="rounded-lg border border-slate-200 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="font-semibold text-slate-900">{item.metric}</h3>
                      <span className="text-sm font-bold text-slate-700">{item.value}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{item.meaning}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </>
      )}
    </div>
  );
};

export default ForecastPage;
