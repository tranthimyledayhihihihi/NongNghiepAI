import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Bell,
  CloudRain,
  Droplets,
  Gauge,
  Globe2,
  MapPin,
  Newspaper,
  Sparkles,
  Sprout,
  ThermometerSun,
  TrendingUp,
  Wind,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { InlineLoading, PageError } from '../components/StatusState';
import { useAuth } from '../contexts/AuthContext';
import { getApiErrorMessage, settledValue } from '../services/api';
import { dashboardApi } from '../services/dashboardApi';
import { seasonApi } from '../services/seasonApi';
import { weatherApi } from '../services/weatherApi';
import { statusLabel, translateUiText } from '../utils/vietnameseText';

const formatNumber = (value, digits = 0) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return 'N/A';
  return number.toLocaleString('vi-VN', { maximumFractionDigits: digits });
};

const formatDate = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
};

const formatPct = (value) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return '+0.0%';
  return `${number >= 0 ? '+' : ''}${number.toFixed(1)}%`;
};

const REGION_LABELS = {
  'Ha Noi': 'Hà Nội',
  'Da Nang': 'Đà Nẵng',
  'Can Tho': 'Cần Thơ',
  'Lam Dong': 'Lâm Đồng',
  'Dak Lak': 'Đắk Lắk',
  'Hai Phong': 'Hải Phòng',
};

const displayRegion = (value) => REGION_LABELS[value] || value;

const STATUS_NAME_LABELS = {
  Weather: 'Thời tiết',
  Market: 'Thị trường',
  'Gemini/Claude': 'Trợ lý AI',
  Database: 'Cơ sở dữ liệu',
  'Zalo/Email/SMS': 'Zalo / Email / SMS',
};

const statusNameLabel = (name) => STATUS_NAME_LABELS[name] || translateUiText(name);

const trendIcon = (trend) => {
  if (trend === 'up' || trend === 'increasing') return <ArrowUp className="h-4 w-4 text-emerald-600" />;
  if (trend === 'down' || trend === 'decreasing') return <ArrowDown className="h-4 w-4 text-rose-600" />;
  return <ArrowRight className="h-4 w-4 text-slate-500" />;
};

const Panel = ({ children, className = '' }) => (
  <section className={`rounded-lg border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
    {children}
  </section>
);

const PanelHeader = ({ icon: Icon, title, children }) => (
  <div className="mb-4 flex items-start justify-between gap-3">
    <div className="flex min-w-0 items-center gap-2">
      {Icon && <Icon className="h-5 w-5 shrink-0 text-emerald-700" />}
      <h2 className="truncate text-base font-semibold text-slate-950">{title}</h2>
    </div>
    {children}
  </div>
);

const EmptyState = ({ text = 'Chưa có dữ liệu.' }) => (
  <div className="rounded-md border border-dashed border-slate-200 px-3 py-4 text-center text-sm text-slate-500">
    {text}
  </div>
);

const RiskBadge = ({ level }) => {
  const styles = {
    high: 'border-rose-200 bg-rose-50 text-rose-700',
    medium: 'border-amber-200 bg-amber-50 text-amber-700',
    low: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  };
  const labels = { high: 'Cao', medium: 'Trung bình', low: 'Thấp' };
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${styles[level] || styles.low}`}>
      Rủi ro {labels[level] || labels.low}
    </span>
  );
};

const SentimentBadge = ({ value }) => {
  const sentiment = (value || 'neutral').toLowerCase();
  const styles = {
    positive: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    negative: 'bg-rose-50 text-rose-700 border-rose-200',
    neutral: 'bg-slate-50 text-slate-700 border-slate-200',
  };
  const labels = { positive: 'Tích cực', negative: 'Tiêu cực', neutral: 'Trung lập' };
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${styles[sentiment] || styles.neutral}`}>
      {labels[sentiment] || labels.neutral}
    </span>
  );
};

const MiniHourlyChart = ({ hourly = [] }) => {
  const points = hourly.slice(0, 12);
  if (!points.length) return <EmptyState text="Chưa có dự báo theo giờ." />;
  const maxRain = Math.max(...points.map((item) => Number(item.rainfall || item.rain_probability || 0)), 1);
  return (
    <div className="flex h-28 items-end gap-2">
      {points.map((item, index) => {
        const value = Number(item.rainfall || 0);
        const probability = Number(item.rain_probability || 0);
        const height = Math.max(12, Math.round(((value || probability / 10) / maxRain) * 92));
        const label = item.time ? item.time.slice(11, 16) : `${index + 1}h`;
        return (
          <div key={`${label}-${index}`} className="flex min-w-0 flex-1 flex-col items-center gap-1">
            <div
              className="w-full rounded-t bg-sky-500"
              style={{ height }}
              title={`${label}: mưa ${formatNumber(value, 1)} mm, xác suất ${formatNumber(probability)}%`}
            />
            <span className="text-[10px] text-slate-500">{label}</span>
          </div>
        );
      })}
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const region = user?.region || 'Ha Noi';
  const cropName = 'lua';
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const loadedKeyRef = useRef(null);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await Promise.allSettled([
        dashboardApi.getDashboardFullData(region, { cropName }),
        weatherApi.getCurrentWeather(region),
        seasonApi.getSeasonSummary(),
      ]);
      const dashboardData = settledValue(results[0], null);
      const freshWeather = settledValue(results[1], null);
      const seasonSummary = settledValue(results[2], null);
      if (!dashboardData) {
        throw results[0].reason;
      }
      if (dashboardData.errors?.length) {
        setError(dashboardData.errors.map((item) => item.message).join(' | '));
      }
      const { overview, realtimeStatus, aiInsights, riskSummary, actionToday } = dashboardData;

      const mergedWeatherRisk = {
        ...(overview?.weather_risk || {}),
        ...(riskSummary || {}),
      };
      if (freshWeather) {
        mergedWeatherRisk.current = {
          ...(mergedWeatherRisk.current || {}),
          ...freshWeather,
        };
      }

      setSummary({
        ...overview,
        active_seasons: seasonSummary?.active_seasons ?? overview?.active_seasons,
        season_summary: seasonSummary,
        ai_recommendation: aiInsights || overview?.ai_recommendation,
        weather_risk: mergedWeatherRisk,
        realtime_status: realtimeStatus,
        action_today: actionToday,
      });
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không tải được bảng điều khiển'));
    } finally {
      setLoading(false);
    }
  }, [cropName, region]);

  useEffect(() => {
    const loadKey = `${region}:${cropName}`;
    if (loadedKeyRef.current === loadKey) return undefined;
    loadedKeyRef.current = loadKey;
    loadDashboard();
    return undefined;
  }, [cropName, loadDashboard, region]);

  const featured = summary?.featured_crop || {};
  const weatherRisk = summary?.weather_risk || {};
  const weatherCurrent = weatherRisk.current || summary?.weather?.current || {};
  const forecast = summary?.forecast || [];
  const regionalPrices = summary?.regional_prices || [];
  const news = summary?.news || [];
  const realtimeMarket = summary?.realtime_market || {};
  const alerts = summary?.alert_center || [];
  const apiStatus = summary?.realtime_status?.api_status || [];
  const actionToday = summary?.action_today || {};
  const activeSeasonCount = Number(summary?.season_summary?.active_seasons ?? summary?.active_seasons ?? 0);

  const forecastHigh = useMemo(() => {
    if (!forecast.length) return null;
    return forecast.reduce(
      (best, item) => (Number(item.forecast_price || item.predicted_price) > Number(best.forecast_price || best.predicted_price) ? item : best),
      forecast[0],
    );
  }, [forecast]);

  if (loading && !summary) {
    return <InlineLoading text="Đang tải dữ liệu tổng quan..." />;
  }

  if (error && !summary) {
    return <PageError message={error} onRetry={loadDashboard} />;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-medium text-emerald-700">
            <Sprout className="h-4 w-4" />
            Dashboard vận hành nông sản
          </div>
          <h1 className="mt-1 text-2xl font-bold text-slate-950">Trung tâm dữ liệu thị trường và nông vụ</h1>
          <p className="mt-1 text-sm text-slate-600">
            Tự làm mới dữ liệu thực tế khi mở trang, sau đó đọc nhanh từ hệ thống.
          </p>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {error}
        </div>
      )}

      <Panel>
        <PanelHeader icon={Gauge} title="Trạng thái hệ thống" />
        <div className="grid gap-3 md:grid-cols-5">
          {apiStatus.length ? (
            apiStatus.map((item) => (
              <div key={item.name} className="rounded-md border border-slate-200 bg-slate-50 px-3 py-3">
                <div className="text-sm font-semibold text-slate-950">{statusNameLabel(item.name)}</div>
                <div className="mt-2">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                      ['ok', 'Hoạt động'].includes(item.status) ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {statusLabel(item.status)}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <EmptyState text="Chưa có trạng thái hệ thống." />
          )}
        </div>
        {actionToday.actions?.length > 0 && (
          <div className="mt-4 rounded-md border border-indigo-100 bg-indigo-50 p-4">
            <div className="mb-2 text-sm font-semibold text-indigo-950">Việc cần làm hôm nay</div>
            <div className="grid gap-2 md:grid-cols-3">
              {actionToday.actions.slice(0, 3).map((item) => (
                <div key={item} className="rounded-md bg-white/80 px-3 py-2 text-sm leading-6 text-indigo-900">
                  {translateUiText(item)}
                </div>
              ))}
            </div>
          </div>
        )}
      </Panel>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Link to="/season-management" className="block focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2">
          <Panel className="h-full transition hover:border-emerald-300 hover:shadow-md">
            <PanelHeader icon={Sprout} title="Tình trạng mùa vụ" />
            <div className="text-3xl font-bold text-slate-950">{formatNumber(activeSeasonCount)}</div>
            <p className="mt-2 text-sm text-slate-600">Mùa vụ đang theo dõi</p>
            <p className="mt-3 rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
              {activeSeasonCount > 0
                ? 'Khuyến nghị: kiểm tra lịch thu hoạch và rủi ro thời tiết trước khi chốt ngày cắt.'
                : 'Chưa có mùa vụ nào đang theo dõi'}
            </p>
            <span className="mt-4 inline-flex items-center gap-2 rounded-md border border-emerald-700 px-4 py-2 text-sm font-semibold text-emerald-800">
              {activeSeasonCount > 0 ? 'Quản lý' : 'Thêm mùa vụ đầu tiên'}
              <ArrowRight className="h-4 w-4" />
            </span>
          </Panel>
        </Link>

        <Panel>
          <PanelHeader icon={Gauge} title="Tổng quan chất lượng" />
          <div className="text-3xl font-bold text-slate-950">{formatNumber(summary?.quality_checks)}</div>
          <p className="mt-2 text-sm text-slate-600">Lần kiểm định chất lượng</p>
          <p className="mt-3 rounded-md bg-sky-50 px-3 py-2 text-sm text-sky-800">
            Khuyến nghị: ưu tiên lô hàng có độ tin cậy cao khi đưa vào định giá và chọn kênh bán.
          </p>
        </Panel>

        <Panel>
          <PanelHeader icon={AlertTriangle} title="Tổng quan rủi ro">
            <RiskBadge level={weatherRisk.risk_level} />
          </PanelHeader>
          <div className="text-3xl font-bold text-slate-950">{formatNumber(weatherRisk.risk_score)}</div>
          <p className="mt-2 text-sm text-slate-600">Điểm rủi ro cho {displayRegion(weatherRisk.region || region)}</p>
          <div className="mt-3 space-y-2">
            {(weatherRisk.alerts || []).slice(0, 2).map((item, index) => (
              <div key={`${item.title || item.alert_type || 'risk'}-${index}`} className="rounded-md border border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                <div className="flex items-center justify-between gap-2">
                  <span>{item.title || item.message || item.alert_type}</span>
                </div>
              </div>
            ))}
            {!(weatherRisk.alerts || []).length && <EmptyState text="Chưa có cảnh báo rủi ro." />}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel>
          <PanelHeader icon={TrendingUp} title="Giá thị trường" />

          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <MapPin className="h-4 w-4" />
                {displayRegion(featured.location || region)}
              </div>
              <h2 className="mt-1 text-2xl font-bold text-slate-950">{featured.display_name || featured.name || cropName}</h2>
              <div className="mt-3 flex items-end gap-2">
                <span className="text-4xl font-bold text-slate-950">{formatNumber(featured.price)}</span>
                <span className="pb-1 text-sm font-medium text-slate-500">{featured.unit || 'VND/kg'}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md bg-emerald-50 px-3 py-2">
                <div className="text-xs text-emerald-700">So với hôm trước</div>
                <div className="mt-1 flex items-center gap-1 text-lg font-bold text-emerald-800">
                  {trendIcon(featured.trend)}
                  {formatPct(featured.change_day_pct)}
                </div>
              </div>
              <div className="rounded-md bg-sky-50 px-3 py-2">
                <div className="text-xs text-sky-700">So với tuần trước</div>
                <div className="mt-1 text-lg font-bold text-sky-800">{formatPct(featured.change_week_pct)}</div>
              </div>
            </div>

            <Link
              to="/alerts"
              className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-emerald-700 px-4 py-2.5 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-50"
            >
              <Bell className="h-4 w-4" />
              Đặt cảnh báo giá
            </Link>
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={CloudRain} title="Thời tiết hiện tại">
            <RiskBadge level={weatherRisk.risk_level} />
          </PanelHeader>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <ThermometerSun className="h-4 w-4 text-orange-600" />
                Nhiệt độ
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherCurrent.temperature, 1)} C</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Gauge className="h-4 w-4 text-slate-600" />
                Điểm rủi ro
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherRisk.risk_score)}</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Droplets className="h-4 w-4 text-sky-600" />
                Mưa 24h tới
              </div>
              <div className="mt-2 text-2xl font-bold text-sky-700">{formatNumber(weatherRisk.rain_24h, 1)} mm</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Wind className="h-4 w-4 text-slate-600" />
                Gió / UV
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">
                {formatNumber(weatherCurrent.wind_speed, 1)} / {formatNumber(weatherCurrent.uv_index, 1)}
              </div>
            </div>
          </div>

          <div className="mt-5">
            <MiniHourlyChart hourly={weatherRisk.hourly_forecast || []} />
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={AlertTriangle} title="Trung tâm cảnh báo">
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              {alerts.length} cảnh báo
            </span>
          </PanelHeader>
          <div className="space-y-3">
            {alerts.length ? (
              alerts.slice(0, 4).map((alert, index) => (
                <div key={`${alert.alert_type}-${index}`} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2">
                  <div className="text-sm font-semibold text-amber-900">{translateUiText(alert.title || alert.alert_type)}</div>
                  <div className="mt-1 text-xs text-amber-800">{translateUiText(alert.message || alert.recommendation)}</div>
                </div>
              ))
            ) : (
              <EmptyState text="Chưa có cảnh báo từ hệ thống." />
            )}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Panel>
          <PanelHeader icon={Sparkles} title="Gợi ý hôm nay" />
          <div className="space-y-3">
            <h3 className="text-xl font-bold text-slate-950">{translateUiText(summary?.ai_recommendation?.title || 'Đang tổng hợp')}</h3>
            <p className="text-sm leading-6 text-slate-600">{translateUiText(summary?.ai_recommendation?.description || 'Chưa có khuyến nghị.')}</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md bg-emerald-50 p-3">
                <div className="text-xs text-emerald-700">Độ tin cậy</div>
                <div className="mt-1 text-xl font-bold text-emerald-800">
                  {formatNumber(Number(summary?.ai_recommendation?.confidence || 0) * 100)}%
                </div>
              </div>
              <div className="rounded-md bg-slate-50 p-3">
                <div className="text-xs text-slate-500">Giá kỳ vọng</div>
                <div className="mt-1 text-xl font-bold text-slate-950">{formatNumber(summary?.ai_recommendation?.expected_price)}</div>
              </div>
            </div>
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={TrendingUp} title="Dự báo giá 7 ngày">
            {forecastHigh && <span className="text-xs font-medium text-slate-500">Đỉnh: {formatNumber(forecastHigh.forecast_price || forecastHigh.predicted_price)}</span>}
          </PanelHeader>
          <div className="space-y-2">
            {forecast.length ? (
              forecast.slice(0, 7).map((item) => (
                <div key={item.date} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{formatDate(item.date)}</div>
                    <div className="text-xs text-slate-500">{item.confidence === 'high' ? 'Tin cậy cao' : 'Tin cậy trung bình'}</div>
                  </div>
                  <div className="flex items-center gap-2 text-right">
                    {trendIcon(item.trend)}
                    <span className="text-sm font-bold text-slate-950">{formatNumber(item.forecast_price || item.predicted_price)} VND/kg</span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chưa có dự báo giá." />
            )}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader icon={Globe2} title="Giá theo vùng" />
          <div className="grid gap-3 md:grid-cols-2">
            {regionalPrices.length ? (
              regionalPrices.map((item) => (
                <div key={item.region} className="rounded-md border border-slate-200 px-3 py-3">
                  <div className="font-semibold text-slate-950">{displayRegion(item.region)}</div>
                  <div className="mt-3 text-2xl font-bold text-slate-950">
                    {formatNumber(item.price)} <span className="text-sm font-medium text-slate-500">{item.unit || 'VND/kg'}</span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chưa có giá theo vùng." />
            )}
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={Newspaper} title="Tin thị trường" />
          <div className="space-y-3">
            {news.length ? (
              news.slice(0, 6).map((item) => (
                <a
                  key={item.news_id || item.source_url || item.title}
                  href={item.source_url || '#'}
                  target="_blank"
                  rel="noreferrer"
                  className="block rounded-md border border-slate-200 px-3 py-2 transition hover:border-emerald-200 hover:bg-emerald-50"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="line-clamp-2 text-sm font-semibold text-slate-950">{translateUiText(item.title)}</div>
                    <SentimentBadge value={item.sentiment} />
                  </div>
                </a>
              ))
            ) : (
              <EmptyState text="Chưa có tin tức từ hệ thống." />
            )}
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelHeader icon={Globe2} title="Tham chiếu thị trường quốc tế" />
        <div className="grid gap-3 md:grid-cols-3">
          {(realtimeMarket.global_references || []).length ? (
            realtimeMarket.global_references.map((item) => (
              <div key={`${item.crop_name}-${item.source_url}`} className="rounded-md border border-slate-200 px-3 py-3">
                <div className="text-sm font-semibold text-slate-950">{item.crop_name || item.crop_id}</div>
                <div className="mt-2 text-xl font-bold text-slate-950">{formatNumber(item.price)} VND/kg</div>
              </div>
            ))
          ) : (
            <EmptyState text="Chưa có tham chiếu quốc tế." />
          )}
        </div>
      </Panel>
    </div>
  );
};

export default Dashboard;
