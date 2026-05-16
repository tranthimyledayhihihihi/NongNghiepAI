import {
  AlertTriangle,
  ArrowDown,
  ArrowRight,
  ArrowUp,
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
import { InlineLoading, PageError } from '../components/StatusState';
import { useAuth } from '../contexts/AuthContext';
import { getApiErrorMessage } from '../services/api';
import { dashboardApi } from '../services/dashboardApi';

const formatNumber = (value, digits = 0) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return 'N/A';
  return number.toLocaleString('vi-VN', { maximumFractionDigits: digits });
};

const formatDateTime = (value) => {
  if (!value) return 'Chua co';
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

const EmptyState = ({ text = 'Chua co du lieu.' }) => (
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
  const labels = { high: 'Cao', medium: 'Trung binh', low: 'Thap' };
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${styles[level] || styles.low}`}>
      Rui ro {labels[level] || labels.low}
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
  const labels = { positive: 'Tich cuc', negative: 'Tieu cuc', neutral: 'Trung lap' };
  return (
    <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${styles[sentiment] || styles.neutral}`}>
      {labels[sentiment] || labels.neutral}
    </span>
  );
};

const MiniHourlyChart = ({ hourly = [] }) => {
  const points = hourly.slice(0, 12);
  if (!points.length) return <EmptyState text="Chua co hourly forecast." />;
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
              title={`${label}: mua ${formatNumber(value, 1)} mm, xac suat ${formatNumber(probability)}%`}
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
      const data = await dashboardApi.reset({ cropName, region });
      setSummary(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Khong tai duoc dashboard'));
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

  const forecastHigh = useMemo(() => {
    if (!forecast.length) return null;
    return forecast.reduce(
      (best, item) => (Number(item.forecast_price || item.predicted_price) > Number(best.forecast_price || best.predicted_price) ? item : best),
      forecast[0],
    );
  }, [forecast]);

  if (loading && !summary) {
    return <InlineLoading text="Dang xoa du lieu cu va lay du lieu moi tu API..." />;
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
            Dashboard van hanh nong san
          </div>
          <h1 className="mt-1 text-2xl font-bold text-slate-950">Trung tam du lieu thi truong va nong vu</h1>
          <p className="mt-1 text-sm text-slate-600">
            Tu lam moi du lieu thuc te khi mo trang, sau do doc nhanh tu DB.
          </p>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel>
          <PanelHeader icon={TrendingUp} title="Thi truong noi bat">
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
                <div className="text-xs text-emerald-700">So voi hom truoc</div>
                <div className="mt-1 flex items-center gap-1 text-lg font-bold text-emerald-800">
                  {trendIcon(featured.trend)}
                  {formatPct(featured.change_day_pct)}
                </div>
              </div>
              <div className="rounded-md bg-sky-50 px-3 py-2">
                <div className="text-xs text-sky-700">So voi tuan truoc</div>
                <div className="mt-1 text-lg font-bold text-sky-800">{formatPct(featured.change_week_pct)}</div>
              </div>
            </div>

            <div className="rounded-md border border-slate-200 px-3 py-2 text-xs text-slate-600">
              <div className="font-semibold text-slate-800">Nguon: {featured.source_name || 'Chua ro'}</div>
              <div>Cap nhat: {formatDateTime(featured.last_updated)}</div>
              {featured.source_url && (
                <a href={featured.source_url} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-emerald-700">
                  Mo nguon <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            <Link
              to="/alerts-management"
              className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-emerald-700 px-4 py-2.5 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-50"
            >
              <Bell className="h-4 w-4" />
              Dat canh bao gia
            </Link>
          </div>
        </Panel>

        <Panel>
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
                Nhiet do
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherCurrent.temperature, 1)} C</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Gauge className="h-4 w-4 text-slate-600" />
                Risk score
              </div>
              <div className="mt-2 text-2xl font-bold text-slate-950">{formatNumber(weatherRisk.risk_score)}</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Droplets className="h-4 w-4 text-sky-600" />
                Mua 24h toi
              </div>
              <div className="mt-2 text-2xl font-bold text-sky-700">{formatNumber(weatherRisk.rain_24h, 1)} mm</div>
            </div>
            <div className="rounded-md bg-slate-50 px-3 py-3">
              <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                <Wind className="h-4 w-4 text-slate-600" />
                Gio / UV
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
          <PanelHeader icon={AlertTriangle} title="Alert Center">
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
              {alerts.length} canh bao
            </span>
          </PanelHeader>
          <div className="space-y-3">
            {alerts.length ? (
              alerts.slice(0, 4).map((alert, index) => (
                <div key={`${alert.alert_type}-${index}`} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2">
                  <div className="text-sm font-semibold text-amber-900">{alert.title || alert.alert_type}</div>
                  <div className="mt-1 text-xs text-amber-800">{alert.message || alert.recommendation}</div>
                </div>
              ))
            ) : (
              <EmptyState text="Chua co canh bao tu backend." />
            )}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Panel>
          <PanelHeader icon={Sparkles} title="AI khuyen nghi">
            <DataSourceBadge data={summary?.ai_recommendation || {}} />
          </PanelHeader>
          <div className="space-y-3">
            <h3 className="text-xl font-bold text-slate-950">{summary?.ai_recommendation?.title || 'Dang tong hop'}</h3>
            <p className="text-sm leading-6 text-slate-600">{summary?.ai_recommendation?.description || 'Chua co khuyen nghi.'}</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-md bg-emerald-50 p-3">
                <div className="text-xs text-emerald-700">Do tin cay</div>
                <div className="mt-1 text-xl font-bold text-emerald-800">
                  {formatNumber(Number(summary?.ai_recommendation?.confidence || 0) * 100)}%
                </div>
              </div>
              <div className="rounded-md bg-slate-50 p-3">
                <div className="text-xs text-slate-500">Gia ky vong</div>
                <div className="mt-1 text-xl font-bold text-slate-950">{formatNumber(summary?.ai_recommendation?.expected_price)}</div>
              </div>
            </div>
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={TrendingUp} title="Du bao gia 7 ngay">
            {forecastHigh && <span className="text-xs font-medium text-slate-500">Dinh: {formatNumber(forecastHigh.forecast_price || forecastHigh.predicted_price)}</span>}
          </PanelHeader>
          <div className="space-y-2">
            {forecast.length ? (
              forecast.slice(0, 7).map((item) => (
                <div key={item.date} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{formatDate(item.date)}</div>
                    <div className="text-xs text-slate-500">{item.confidence === 'high' ? 'Tin cay cao' : 'Tin cay trung binh'}</div>
                  </div>
                  <div className="flex items-center gap-2 text-right">
                    {trendIcon(item.trend)}
                    <span className="text-sm font-bold text-slate-950">{formatNumber(item.forecast_price || item.predicted_price)} VND/kg</span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chua co du bao gia." />
            )}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <Panel className="xl:col-span-2">
          <PanelHeader icon={Globe2} title="Gia theo vung" />
          <div className="grid gap-3 md:grid-cols-2">
            {regionalPrices.length ? (
              regionalPrices.map((item) => (
                <div key={item.region} className="rounded-md border border-slate-200 px-3 py-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-semibold text-slate-950">{item.region}</div>
                      <div className="text-xs text-slate-500">{item.source_name || 'database'}</div>
                    </div>
                    <DataSourceBadge data={item} />
                  </div>
                  <div className="mt-3 text-2xl font-bold text-slate-950">
                    {formatNumber(item.price)} <span className="text-sm font-medium text-slate-500">{item.unit || 'VND/kg'}</span>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="Chua co gia theo vung." />
            )}
          </div>
        </Panel>

        <Panel>
          <PanelHeader icon={Newspaper} title="Tin thi truong" />
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
                    <div className="line-clamp-2 text-sm font-semibold text-slate-950">{item.title}</div>
                    <SentimentBadge value={item.sentiment} />
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    {item.source_name || 'RSS'} - {formatDateTime(item.published_at)}
                  </div>
                </a>
              ))
            ) : (
              <EmptyState text="Chua co tin tuc tu backend." />
            )}
          </div>
        </Panel>
      </div>

      <Panel>
        <PanelHeader icon={Globe2} title="Tham chieu thi truong quoc te">
          <DataSourceBadge data={realtimeMarket.exchange_rate || {}} />
        </PanelHeader>
        <div className="grid gap-3 md:grid-cols-3">
          {(realtimeMarket.global_references || []).length ? (
            realtimeMarket.global_references.map((item) => (
              <div key={`${item.crop_name}-${item.source_url}`} className="rounded-md border border-slate-200 px-3 py-3">
                <div className="text-sm font-semibold text-slate-950">{item.crop_name || item.crop_id}</div>
                <div className="mt-2 text-xl font-bold text-slate-950">{formatNumber(item.price)} VND/kg</div>
                <div className="mt-1 text-xs text-slate-500">{item.source_name}</div>
              </div>
            ))
          ) : (
            <EmptyState text="Chua co tham chieu quoc te." />
          )}
        </div>
      </Panel>
    </div>
  );
};

export default Dashboard;
