import { AlertCircle, Globe, ShoppingCart, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import DataSourceBadge from '../components/DataSourceBadge';
import { getApiErrorMessage } from '../services/api';
import { marketApi } from '../services/marketApi';
import { marketNewsApi } from '../services/marketNewsApi';

const fallbackChannels = [
  { id: 'wholesale', name: 'Chợ đầu mối', commission: '5-10%' },
  { id: 'retail', name: 'Chợ bán lẻ', commission: '0%' },
  { id: 'supermarket', name: 'Siêu thị/cửa hàng sạch', commission: '10-15%' },
];

const channelIcons = [ShoppingCart, TrendingUp, Globe];

const MarketPage = () => {
  const [channels, setChannels] = useState(fallbackChannels);
  const [channelSource, setChannelSource] = useState({ is_mock: true, source: 'fallback' });
  const [formData, setFormData] = useState({
    cropName: 'ca chua',
    region: 'Ha Noi',
    quantity: 1000,
    qualityGrade: 'grade_1',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [news, setNews] = useState([]);
  const [marketPrice, setMarketPrice] = useState(null);
  const [trend, setTrend] = useState(null);
  const [opportunities, setOpportunities] = useState(null);
  const [risks, setRisks] = useState(null);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const [intelligenceError, setIntelligenceError] = useState(null);

  useEffect(() => {
    const loadChannels = async () => {
      try {
        const data = await marketApi.getChannels();
        if (data.channels?.length) {
          setChannels(data.channels);
          setChannelSource(data);
        }
      } catch {
        setChannels(fallbackChannels);
        setChannelSource({ is_mock: true, source: 'fallback' });
      }
    };
    loadChannels();
  }, []);

  useEffect(() => {
    let active = true;
    const loadIntelligence = async () => {
      setIntelligenceLoading(true);
      setIntelligenceError(null);
      try {
        const results = await Promise.allSettled([
          marketApi.getMarketNews({ limit: 4, crop: formData.cropName, region: formData.region }),
          marketApi.getMarketPrices({ crop: formData.cropName, region: formData.region }),
          marketApi.getMarketTrends(formData.cropName, formData.region),
          marketApi.getMarketOpportunities({ crop: formData.cropName, region: formData.region }),
          marketApi.getMarketRisks({ crop: formData.cropName, region: formData.region }),
        ]);
        const [newsData, priceData, trendData, opportunityData, riskData] = results.map((item) => (
          item.status === 'fulfilled' ? item.value : null
        ));
        if (results.every((item) => item.status === 'rejected')) {
          throw results[0].reason;
        }
        const newsItems = newsData?.news || [];
        const enrichedResults = await Promise.allSettled(newsItems.map(async (item) => {
          try {
            const analysis = await marketApi.analyzeMarketNews({
              title: item.title,
              summary: item.summary,
              crop: formData.cropName,
              region: formData.region,
            });
            return {
              ...item,
              ...analysis,
              affected_crops: analysis.affected_crops?.length ? analysis.affected_crops : [formData.cropName],
              affected_regions: analysis.affected_regions?.length ? analysis.affected_regions : [formData.region],
            };
          } catch {
            return {
              ...item,
              affected_crops: [formData.cropName],
              affected_regions: [formData.region],
              impact: item.impact || item.sentiment || 'neutral',
              impact_score: item.impact_score ?? 0.5,
              price_effect: item.price_effect || 'stable',
              source: item.source || 'cached',
              source_name: item.source_name || 'Market news cache',
              confidence: item.confidence ?? 0.5,
            };
          }
        }));
        const enrichedNews = enrichedResults.map((item, index) => (
          item.status === 'fulfilled' ? item.value : newsItems[index]
        )).filter(Boolean);
        if (!active) return;
        setNews(enrichedNews);
        setMarketPrice(priceData);
        setTrend(trendData);
        setOpportunities(opportunityData);
        setRisks(riskData);
        const failed = results.filter((item) => item.status === 'rejected');
        setIntelligenceError(failed.length ? 'Mot so khoi market phan hoi cham, giao dien dang hien thi phan du lieu con lai.' : null);
      } catch (err) {
        if (!active) return;
        try {
          const legacyNews = await marketNewsApi.getLegacyLatest(4);
          if (!active) return;
          setNews((legacyNews.news || []).map((item) => ({
            ...item,
            source: 'legacy',
            source_name: item.source_name || 'Legacy /api/market-news',
            confidence: item.confidence ?? 0.45,
            affected_crops: [formData.cropName],
            affected_regions: [formData.region],
            impact: item.impact || item.sentiment || 'neutral',
            impact_score: item.impact_score ?? 0.5,
            price_effect: item.price_effect || 'stable',
          })));
          setIntelligenceError('Endpoint moi loi, dang hien thi tin legacy/cache.');
        } catch {
          setNews([]);
          setIntelligenceError(getApiErrorMessage(err, 'Khong tai duoc market intelligence'));
        }
        setMarketPrice(null);
        setTrend(null);
        setOpportunities(null);
        setRisks(null);
      } finally {
        if (active) setIntelligenceLoading(false);
      }
    };
    loadIntelligence();
    return () => {
      active = false;
    };
  }, [formData.cropName, formData.region]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await marketApi.suggestMarket(
        formData.cropName,
        formData.region,
        formData.quantity,
        formData.qualityGrade
      );
      setResult(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Không thể gợi ý kênh bán hàng'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-gray-900">Tư vấn kênh bán hàng</h1>
          <DataSourceBadge data={channelSource} />
        </div>
        <p className="mt-2 text-gray-600">
          So sánh kênh bán và gợi ý kênh tối ưu từ API backend.
        </p>
      </div>

      {intelligenceLoading && (
        <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          Dang tai market intelligence tu endpoint moi...
        </div>
      )}
      {intelligenceError && (
        <div className="mb-4 rounded-lg border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {intelligenceError}
        </div>
      )}

      <section className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-gray-700">Gia thi truong</h2>
            {marketPrice && <DataSourceBadge data={marketPrice} />}
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {marketPrice?.current_price ? `${Number(marketPrice.current_price).toLocaleString('vi-VN')} VND/kg` : 'N/A'}
          </p>
          <p className="mt-2 text-sm text-gray-600">{marketPrice?.crop_name || formData.cropName} · {marketPrice?.region || formData.region}</p>
          {marketPrice?.recommendation && <p className="mt-2 text-sm text-green-700">Recommendation: {marketPrice.recommendation}</p>}
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-gray-700">Xu huong AI</h2>
            {trend && <DataSourceBadge data={trend} />}
          </div>
          <p className="text-2xl font-bold text-gray-900">{trend?.trend || 'stable'}</p>
          <p className="mt-2 text-sm text-gray-600">{trend?.evidence?.[0] || 'Dang tong hop du lieu thi truong.'}</p>
          {trend?.recommendation && <p className="mt-2 text-sm text-green-700">Recommendation: {trend.recommendation}</p>}
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-gray-700">Co hoi & rui ro</h2>
            <DataSourceBadge data={opportunities || risks || { source: 'mock', source_name: 'Market intelligence fallback' }} />
          </div>
          <p className="text-sm font-semibold text-green-800">{opportunities?.opportunities?.[0]?.title || 'Batch selling opportunity'}</p>
          <p className="mt-2 text-sm text-gray-600">{risks?.risks?.[0]?.recommendation || 'Theo doi bien dong gia va tao canh bao khi can.'}</p>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {channels.map((channel, index) => {
          const Icon = channelIcons[index % channelIcons.length];
          const channelId = channel.id || channel.channel_code;
          const channelName = channel.name || channel.channel_name;
          const commission =
            channel.commission ||
            (Number.isFinite(channel.commission_rate) ? `${Math.round(channel.commission_rate * 100)}%` : 'N/A');
          return (
            <div
              key={channelId || channelName}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center mb-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-semibold text-gray-900">{channelName}</h3>
                  <p className="text-sm text-gray-600">{channelId}</p>
                </div>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-700">Phí hoa hồng:</span>
                <span className="ml-2 text-sm text-gray-900">{commission}</span>
              </div>
            </div>
          );
        })}
      </div>

      {true && (
        <section className="mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Market News</h2>
            <DataSourceBadge data={news[0] || { source: intelligenceError ? 'legacy' : 'realtime_api', source_name: intelligenceError ? 'Legacy /api/market-news' : 'RSS market news cache', confidence: intelligenceError ? 0.45 : 0.7 }} />
          </div>
          {news.length ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {news.map((item) => (
              <a
                key={item.source_url || item.title}
                href={item.source_url || '#'}
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-gray-200 p-4 hover:border-green-300 hover:bg-green-50"
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-semibold text-gray-900">{item.title}</p>
                  <DataSourceBadge data={item} />
                </div>
                <p className="mt-2 line-clamp-2 text-sm text-gray-600">{item.summary || item.ai_summary}</p>
                <div className="mt-3 grid gap-2 text-xs text-gray-600">
                  <p><span className="font-semibold">AI news summary:</span> {item.ai_summary || item.recommendation || item.summary || 'Dang tong hop.'}</p>
                  <p><span className="font-semibold">affected_crops:</span> {(item.affected_crops || []).join(', ') || formData.cropName}</p>
                  <p><span className="font-semibold">affected_regions:</span> {(item.affected_regions || []).join(', ') || formData.region}</p>
                  <p><span className="font-semibold">impact:</span> {item.impact || 'neutral'} · score {item.impact_score ?? 'N/A'} · price_effect {item.price_effect || 'stable'}</p>
                  <p><span className="font-semibold">updated:</span> {item.updated_at || item.published_at || 'N/A'}</p>
                </div>
              </a>
            ))}
          </div>
          ) : (
            <div className="rounded-lg border border-dashed border-gray-300 p-5 text-center text-sm text-gray-600">
              Chua co market news phu hop.
            </div>
          )}
        </section>
      )}

      <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Opportunities</h2>
            <DataSourceBadge data={opportunities || { source: 'mock', source_name: 'Market opportunities fallback' }} />
          </div>
          <div className="space-y-3">
            {(opportunities?.opportunities || []).map((item) => (
              <div key={`${item.title}-${item.region}`} className="rounded-lg border border-green-100 bg-green-50 p-3 text-sm text-green-900">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{item.title}</span>
                  <DataSourceBadge data={item} />
                </div>
                <p className="mt-1">{item.reason || item.recommendation || 'Theo doi co hoi ban theo dot.'}</p>
                <p className="mt-1 text-xs">confidence: {item.confidence ?? opportunities?.confidence ?? 'N/A'}</p>
              </div>
            ))}
            {!opportunities?.opportunities?.length && <p className="text-sm text-gray-600">Chua co opportunity tu endpoint moi.</p>}
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-gray-900">Risks</h2>
            <DataSourceBadge data={risks || { source: 'mock', source_name: 'Market risks fallback' }} />
          </div>
          <div className="space-y-3">
            {(risks?.risks || []).map((item) => (
              <div key={`${item.title}-${item.region}`} className="rounded-lg border border-amber-100 bg-amber-50 p-3 text-sm text-amber-900">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{item.title}</span>
                  <DataSourceBadge data={item} />
                </div>
                <p className="mt-1">severity: {item.severity || 'medium'}</p>
                <p className="mt-1">recommendation: {item.recommendation || 'Tao canh bao gia va tranh ban tat ca cung luc.'}</p>
              </div>
            ))}
            {!risks?.risks?.length && <p className="text-sm text-gray-600">Chua co risk tu endpoint moi.</p>}
          </div>
        </div>
      </section>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Công cụ gợi ý kênh bán</h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nông sản
            </label>
            <select
              value={formData.cropName}
              onChange={(event) => setFormData({ ...formData, cropName: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="ca chua">Cà chua</option>
              <option value="dua chuot">Dưa chuột</option>
              <option value="rau muong">Rau muống</option>
              <option value="lua">Lúa</option>
              <option value="ot">Ớt</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Khu vực
            </label>
            <select
              value={formData.region}
              onChange={(event) => setFormData({ ...formData, region: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="Ha Noi">Hà Nội</option>
              <option value="TP.HCM">TP.HCM</option>
              <option value="Da Nang">Đà Nẵng</option>
              <option value="Can Tho">Cần Thơ</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Số lượng (kg)
            </label>
            <input
              type="number"
              min="1"
              value={formData.quantity}
              onChange={(event) => setFormData({ ...formData, quantity: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chất lượng
            </label>
            <select
              value={formData.qualityGrade}
              onChange={(event) => setFormData({ ...formData, qualityGrade: event.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="grade_1">Loại 1</option>
              <option value="grade_2">Loại 2</option>
              <option value="grade_3">Loại 3</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300"
            >
              {loading ? 'Đang gợi ý...' : 'Gợi ý'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-md bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-6 space-y-4">
            <div className="rounded-lg bg-green-50 border border-green-200 p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <p className="text-sm text-green-700">Kênh đề xuất</p>
                <DataSourceBadge data={result} />
              </div>
              <p className="text-2xl font-bold text-green-900">{result.recommended_channel}</p>
              <p className="mt-2 text-sm text-green-800">{result.reason}</p>
              {result.warning && <p className="mt-2 text-sm text-yellow-700">{result.warning}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.profit_comparison?.map((channel, index) => (
                <div
                  key={channel.channel}
                  className={`p-4 rounded-lg border-2 ${
                    index === 0 ? 'border-green-500 bg-green-50' : 'border-gray-200'
                  }`}
                >
                  <p className="font-medium text-gray-900">
                    {channel.channel_name}
                    {index === 0 && (
                      <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">
                        Tốt nhất
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Giá ước tính: {channel.estimated_price.toLocaleString()} VND/kg
                  </p>
                  <p className="text-lg font-bold text-gray-900 mt-1">
                    {channel.estimated_total_revenue.toLocaleString()} VND
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketPage;
