import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  BarChart3,
  Bell,
  CloudRain,
  Droplets,
  ExternalLink,
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
import DataSourceBadge from '../components/DataSourceBadge';
import { InlineLoading } from '../components/StatusState';
import { useAuth } from '../contexts/AuthContext';
import { getApiErrorMessage } from '../services/api';
import { dashboardApi } from '../services/dashboardApi';

const formatNumber = (value, digits = 0) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return 'N/A';
  return number.toLocaleString('vi-VN', { maximumFractionDigits: digits });
};

const formatDateTime = (value) => {
  if (!value) return 'Chưa có';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
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

const settledValue = (result) => (result?.status === 'fulfilled' ? result.value : null);

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

const WidgetError = ({ message }) => (
  <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
    {message}
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
  if (!points.length) return <EmptyState text="Chưa có hourly forecast." />;
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
  const [data, setData] = useState({});
  const [widgetErrors, setWidgetErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const loadedKeyRef = useRef(null);

  const loadDashboard = useCallback(async () => {
    const requests = {
      summary: dashboardApi.reset({ cropName, region }),
    };

    const keys = Object.keys(requests);
    const results = await Promise.allSettled(Object.values(requests));
    const nextData = {};
    const nextErrors = {};

    keys.forEach((key, index) => {
      const result = results[index];
      if (result.status === 'fulfilled') {
        nextData[key] = settledValue(result);
      } else {
        nextErrors[key] = getApiErrorMessage(result.reason, 'Không tải được dữ liệu widget');
      }
    });

    setData((prev) => ({ ...prev, ...nextData }));
    setWidgetErrors(nextErrors);
    setLoading(false);
  },
    [cropName, region],
  );

  useEffect(() => {
    let active = true;
    const loadKey = `${region}:${cropName}`;
    if (loadedKeyRef.current === loadKey) return undefined;
    loadedKeyRef.current = loadKey;
    setLoading(true);
    loadDashboard().finally(() => {
      if (active) setLoading(false);
    });
    return () => {
      active = false;
    };
  }, [loadDashboard]);

  const summary = data.summary || {};
  const featured = summary.featured_crop || {};
  const weatherRisk = summary.weather_risk || {};
  const agricultureWeather = {};
  const weatherCurrent = weatherRisk.current || agricultureWeather.current || summary.weather?.current || {};
  const forecast = summary.forecast || [];
  const regionalPrices = summary.regional_prices || [];
  const news = data.news?.news?.length ? data.news.news : summary.news || [];
  const realtimeMarket = summary.realtime_market || {};
  const alerts = summary.alert_center || [];

  const forecastHigh = useMemo(() => {
    if (!forecast.length) return null;
    return forecast.reduce((best, item) => (Number(item.forecast_price || item.predicted_price) > Number(best.forecast_price || best.predicted_price) ? item : best), forecast[0]);
  }, [forecast]);

  if (loading && !summary.featured_crop) {
    return <InlineLoading text="Đang xóa dữ liệu cũ và lấy dữ liệu mới từ API..." />;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-medium text-emerald-700">
            <Sprout className="h-4 w-4" />
            Dashboard vận hành nông sản
          </div>
          <h1 className="mt-1 truncate text-2xl font-bold text-slate-950">Trung tâm dữ liệu thị trường và nông vụ</h1>
          <p className="mt-1 text-sm text-slate-600">
            Tự làm mới dữ liệu thực tế khi mở trang, sau đó đọc nhanh từ DB.
          </p>
        </div>
      </div>

      {Object.keys(widgetErrors).length > 0 && (
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(widgetErrors).map(([key, message]) => (
            <WidgetError key={key} message={`${key}: ${message}`} />
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel className="xl:col-span-1">
          <PanelHeader icon={TrendingUp} title="Thị trường nổi bật">
            <DataSourceBadge data={featured} />
          </PanelHeader>

          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <MapPin className="h-4 w-4" />
                {featured.location || region}
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

            <div className="rounded-md border border-slate-200 px-3 py-2 text-xs text-slate-600">
              <div className="font-semibold text-slate-800">Nguồn: {featured.source_name || 'Chưa rõ'}</div>
              <div>Cập nhật: {formatDateTime(featured.last_updated)}</div>
              {featured.source_url && (
                <a href={featured.source_url} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-emerald-700">
                  Mở nguồn <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            <Link
              to="/alerts-management"
              className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-emerald-700 px-4 py-2.5 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-50"
            >
              <Bell className="h-4 w-4" />
              Đặt cảnh báo giá
            </Link>
          </div>
        </Panel>

        <Panel className="xl:col-span-1">
          <PanelHeader icon={CloudRain} title="Weather Intelligence">
            <div className="flex items-center gap-2">
              <RiskBadge level={weatherRisk.risk_level} />
              <DataSourceBadge data={weatherRisk} />
            </div>
          </PanelHeader>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <ThermometerSun className="h-4 w-4 text-orange-600" />
                Nhiệt độ
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherCurrent.temperature, 1)}°C</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Gauge className="h-4 w-4 text-rose-600" />
                Risk score
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherRisk.risk_score)}</div>
            </div>
            <div className="rounded-md bg-blue-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-blue-700">
                <Droplets className="h-4 w-4" />
                Mưa 24h tới
              </div>
              <div className="mt-2 text-xl font-bold text-blue-900">{formatNumber(weatherRisk.rain_24h_mm, 1)} mm</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Wind className="h-4 w-4 text-slate-600" />
                Gió / UV
              </div>
              <div className="mt-2 text-xl font-bold text-slate-950">
                {formatNumber(weatherRisk.wind_speed || weatherCurrent.wind_speed, 1)} / {formatNumber(weatherRisk.uv_index || weatherCurrent.uv_index, 1)}
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-md border border-slate-200 px-3 py-3">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-semibold text-slate-900">Không khí và phơi/sấy</div>
              <DataSourceBadge data={weatherRisk.air_quality || {}} />
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
              <div>
                <div className="text-xs text-slate-500">AQI</div>
                <div className="font-bold text-slate-950">{formatNumber(weatherRisk.air_quality?.aqi)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">PM2.5</div>
                <div className="font-bold text-slate-950">{formatNumber(weatherRisk.air_quality?.pm25, 1)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Sấy/phơi</div>
                <div className="font-bold text-slate-950">{weatherRisk.drying_risk?.level || 'N/A'}</div>
              </div>
            </div>
            <p className="mt-2 text-xs text-slate-600">{weatherRisk.drying_risk?.recommendation || weatherRisk.air_quality?.recommendation}</p>
          </div>
        </Panel>

        <Panel className="xl:col-span-1">
          <PanelHeader icon={AlertTriangle} title="Alert Center">
            <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
              {formatNumber(alerts.length)} cảnh báo
            </span>
          </PanelHeader>

          <div className="space-y-3">
            {alerts.length ? (
              alerts.slice(0, 5).map((alert, index) => (
                <div key={`${alert.title}-${index}`} className="rounded-md border border-slate-200 px-3 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold text-slate-950">{alert.title}</div>
                      <p className="mt-1 line-clamp-2 text-xs text-slate-600">{alert.message}</p>
                    </div>
                    <RiskBadge level={alert.severity === 'high' ? 'high' : alert.severity === 'low' ? 'low' : 'medium'} />
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-2 text-[11px] text-slate-500">
                    <span className="truncate">{alert.source_name || 'Dashboard rules'}</span>
                    <span>{formatDateTime(alert.last_updated)}</span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chưa có cảnh báo từ backend." />
            )}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader icon={BarChart3} title="Dự báo giá 7 ngày">
            <DataSourceBadge data={summary.price_trend || { source_name: 'Forecast' }} />
          </PanelHeader>

          {forecast.length ? (
            <div className="space-y-3">
              <div className="grid gap-3 md:grid-cols-7">
                {forecast.slice(0, 7).map((item) => (
                  <div key={item.date} className="rounded-md border border-slate-200 px-3 py-3">
                    <div className="text-xs font-medium text-slate-500">{formatDate(item.date)}</div>
                    <div className="mt-2 text-lg font-bold text-slate-950">{formatNumber(item.forecast_price || item.predicted_price)}</div>
                    <div className="mt-1 text-[11px] text-slate-500">{formatNumber(item.lower_bound)} - {formatNumber(item.upper_bound)}</div>
                    <div className="mt-2 flex items-center justify-between">
                      {trendIcon(item.trend)}
                      <span className="text-[11px] font-semibold uppercase text-slate-500">{item.confidence_label || item.confidence}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex flex-col gap-3 rounded-md bg-slate-50 px-3 py-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="text-sm font-semibold text-slate-900">Ngày giá tốt nhất</div>
                  <div className="text-sm text-slate-600">
                    {forecastHigh ? `${formatDate(forecastHigh.date)} - ${formatNumber(forecastHigh.forecast_price || forecastHigh.predicted_price)} VND/kg` : 'Chưa đủ dữ liệu'}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {(summary.price_trend?.reason_codes || forecast[0]?.reason_codes || []).map((reason) => (
                    <span key={reason} className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200">
                      {reason}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <EmptyState text="Chưa có dự báo giá." />
          )}
        </Panel>

        <Panel>
          <PanelHeader icon={Sparkles} title="Khuyến nghị AI">
            <DataSourceBadge data={summary.ai_recommendation || { source_name: 'AI rules' }} />
          </PanelHeader>
          {summary.ai_recommendation ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-xl font-bold text-slate-950">{summary.ai_recommendation.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{summary.ai_recommendation.description}</p>
              </div>
              <div className="rounded-md bg-emerald-50 px-3 py-3">
                <div className="text-xs font-medium uppercase text-emerald-700">Confidence</div>
                <div className="mt-1 text-2xl font-bold text-emerald-900">{formatNumber(Number(summary.ai_recommendation.confidence) * 100)}%</div>
                <div className="text-xs text-emerald-700">{summary.ai_recommendation.period}</div>
              </div>
              <div className="flex flex-wrap gap-2">
                {(summary.ai_recommendation.reason_codes || []).slice(0, 5).map((reason) => (
                  <span key={reason} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                    {reason}
                  </span>
                ))}
              </div>
              <Link to="/pricing" className="inline-flex w-full items-center justify-center rounded-md bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800">
                Xem định giá chi tiết
              </Link>
            </div>
          ) : (
            <EmptyState text="Chưa có khuyến nghị." />
          )}
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader icon={MapPin} title="So sánh vùng miền">
            <DataSourceBadge data={{ source_name: 'Regional prices', cache_status: summary.cache_status || 'from_db' }} />
          </PanelHeader>

          {regionalPrices.length ? (
            <div className="grid gap-3 md:grid-cols-2">
              {regionalPrices.map((item) => (
                <div
                  key={item.region}
                  className="rounded-md border border-slate-200 px-3 py-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold text-slate-950">{item.region_label || item.region}</div>
                      <div className="mt-1 text-xs text-slate-500">{item.source_name}</div>
                    </div>
                    <DataSourceBadge data={item} />
                  </div>
                  <div className="mt-3 flex items-end justify-between gap-3">
                    <div>
                      <div className="text-xl font-bold text-slate-950">{formatNumber(item.price)}</div>
                      <div className="text-xs text-slate-500">{item.unit || 'VND/kg'}</div>
                    </div>
                    <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-emerald-600" style={{ width: `${Math.max(6, item.price_index || 0)}%` }} />
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-slate-500">So với trung bình: {formatPct(item.delta_vs_average_pct)}</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="Chưa có dữ liệu vùng miền." />
          )}
        </Panel>

        <Panel>
          <PanelHeader icon={CloudRain} title="Mưa 12 giờ tới">
            <DataSourceBadge data={weatherRisk} />
          </PanelHeader>
          <MiniHourlyChart hourly={weatherRisk.hourly_forecast || agricultureWeather.hourly_forecast || []} />
          <div className="mt-4 rounded-md bg-slate-50 px-3 py-3 text-xs text-slate-600">
            <div className="font-semibold text-slate-800">Khung mưa đáng chú ý</div>
            <div className="mt-1">{weatherRisk.rain_window_24h || 'Chưa thấy khung mưa rủi ro trong 24h.'}</div>
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel>
          <PanelHeader icon={Globe2} title="Global reference">
            <DataSourceBadge data={{ source_name: 'Stooq / ER API', cache_status: 'fresh' }} />
          </PanelHeader>
          <div className="space-y-3">
            {realtimeMarket.exchange_rate && (
              <div className="rounded-md bg-slate-50 px-3 py-3">
                <div className="text-xs font-medium text-slate-500">USD/VND</div>
                <div className="mt-1 text-2xl font-bold text-slate-950">{formatNumber(realtimeMarket.exchange_rate.rate)}</div>
              </div>
            )}
            {(realtimeMarket.futures_reference || []).length ? (
              realtimeMarket.futures_reference.slice(0, 5).map((item) => (
                <div key={`${item.crop_name}-${item.source_name}`} className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3 last:border-0 last:pb-0">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold text-slate-900">{item.display_name || item.crop_name}</div>
                    <div className="truncate text-xs text-slate-500">{item.source_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-slate-950">{formatNumber(item.price)}</div>
                    <div className="text-xs text-slate-500">{item.unit}</div>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chưa có Stooq futures trong DB cache." />
            )}
          </div>
        </Panel>

        <Panel className="xl:col-span-2">
          <PanelHeader icon={Newspaper} title="Tin tức thị trường RSS" />

          {news.length ? (
            <div className="grid gap-3 md:grid-cols-2">
              {news.slice(0, 6).map((item, index) => (
                <article key={item.news_id || item.source_url || index} className="rounded-md border border-slate-200 px-3 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="line-clamp-2 text-sm font-semibold text-slate-950">{item.title}</h3>
                    <SentimentBadge value={item.sentiment} />
                  </div>
                  <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-600">{item.summary}</p>
                  <div className="mt-3 flex items-center justify-between gap-2 text-[11px] text-slate-500">
                    <span className="truncate">{item.source_name || 'RSS'}</span>
                    <span>{formatDateTime(item.published_at)}</span>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState text="Chưa có tin tức RSS." />
          )}
        </Panel>
      </div>
    </div>
  );
};

export default Dashboard;
