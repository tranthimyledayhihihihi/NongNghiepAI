import {
  Bot,
  Clock,
  Database,
  Image as ImageIcon,
  Leaf,
  Menu,
  MoreVertical,
  Paperclip,
  Plus,
  RefreshCw,
  Send,
  Sparkles,
  Trash2,
  User,
  X,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import DataSourceBadge from '../components/DataSourceBadge';
import { useAuth } from '../contexts/AuthContext';
import { aiApi } from '../services/aiApi';

const initialMessages = [
  {
    id: 1,
    type: 'bot',
    content:
      'Chào bạn, tôi là AgriBot AI. Tôi đã nhận được ảnh ruộng lúa của bạn. Để phân tích chính xác hơn, bạn có thể gửi thêm ảnh cận cảnh mặt dưới của lá bị vàng.',
    timestamp: '10:45',
  },
  {
    id: 2,
    type: 'user',
    content: 'Đây là ảnh tôi vừa chụp sáng nay ở ruộng lúa 40 ngày tuổi. Vàng lá lan khá nhanh.',
    timestamp: '10:43',
    image: 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=900&q=80',
  },
  {
    id: 3,
    type: 'bot',
    content: 'Phân tích chẩn đoán ban đầu:',
    timestamp: '10:43',
    analysis: {
      diagnosis: 'Nghi ngờ bệnh đạo ôn lúa',
      details: [
        'Mức độ quan sát: trung bình đến nặng',
        'Điều kiện thuận lợi: độ ẩm cao và nhiệt độ 25-28°C',
        'Cần kiểm tra thêm mặt dưới lá và mật độ vết bệnh trên ruộng',
      ],
      recommendations: [
        'Phun hoạt chất phù hợp theo khuyến cáo địa phương nếu bệnh lan nhanh',
        'Giảm tưới đọng nước và tăng thông thoáng ruộng',
        'Bổ sung kali để tăng sức chống chịu',
        'Theo dõi sát trong 7-10 ngày tới',
      ],
    },
  },
];

const starterMessages = [
  {
    id: 'welcome',
    type: 'bot',
    content: 'Chao ban, toi la AgriBot AI. Hay hoi ve gia, thoi tiet, tin thi truong, canh bao hoac lich thu hoach de toi lay context tu backend.',
    timestamp: initialMessages[0]?.timestamp || new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    source: {
      source: 'database',
      source_name: 'AI context service',
      confidence: 0.7,
    },
  },
];

function formatHistoryTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const now = new Date();
  const diffDays = Math.floor((now - d) / 86400000);
  if (diffDays === 0) return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  if (diffDays === 1) return 'Hôm qua';
  if (diffDays < 7) return `${diffDays} ngày trước`;
  return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

const quickSuggestions = [
  'Thời tiết và cảnh báo bão tuần này tại Đà Nẵng',
  'Giá sầu riêng tại Đắk Lắk hôm nay',
  'Cách xử lý đất phèn ĐBSCL',
  'Xâm nhập mặn tháng này ảnh hưởng cây trồng thế nào',
  'Sâu cuốn lá lúa: cách nhận biết và xử lý',
  'Kỹ thuật trồng cà phê vụ mới',
  'Xu hướng giá hồ tiêu tháng này',
  'Lịch bón phân cho lúa hè thu',
];

const capabilities = [
  {
    icon: Clock,
    title: 'Giá & Thị trường',
    description: 'Giá nông sản theo vùng, xu hướng 7 ngày, so sánh toàn quốc.',
  },
  {
    icon: Sparkles,
    title: 'Thời tiết & Cảnh báo',
    description: 'Dự báo thời tiết, cảnh báo bão lũ, khuyến cáo canh tác theo thời tiết.',
  },
  {
    icon: Leaf,
    title: 'Đất & Kỹ thuật',
    description: 'Cải tạo đất phèn, đất mặn, sâu bệnh, kỹ thuật trồng trọt.',
  },
];


const MessageAvatar = ({ type }) => (
  <div
    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
      type === 'bot' ? 'bg-green-700' : 'bg-gray-700'
    }`}
  >
    {type === 'bot' ? <Bot className="h-5 w-5 text-white" /> : <User className="h-5 w-5 text-white" />}
  </div>
);

const AIChatPage = () => {
  const { isAuthenticated } = useAuth();
  const [messages, setMessages] = useState(starterMessages);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const [activeHistoryId, setActiveHistoryId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmClear, setConfirmClear] = useState(false);

  const loadHistory = useCallback(async () => {
    if (!isAuthenticated) return;
    setHistoryLoading(true);
    try {
      const data = await aiApi.getHistory(20);
      setChatHistory(data.history || []);
    } catch {
      // silent — history is non-critical
    } finally {
      setHistoryLoading(false);
    }
  }, [isAuthenticated]);

  const loadConversation = useCallback((item) => {
    const ts = item.created_at
      ? new Date(item.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
      : '';
    setMessages([
      {
        id: `hist-user-${item.id}`,
        type: 'user',
        content: item.user_message,
        timestamp: ts,
      },
      {
        id: `hist-bot-${item.id}`,
        type: 'bot',
        content: item.ai_response,
        timestamp: ts,
      },
    ]);
    setActiveHistoryId(item.id);
    setHistoryOpen(false);
  }, []);

  const deleteMessage = useCallback(async (id, e) => {
    e.stopPropagation();
    setDeletingId(id);
    try {
      await aiApi.deleteMessage(id);
      setChatHistory((prev) => prev.filter((item) => item.id !== id));
      if (activeHistoryId === id) { setMessages(starterMessages); setActiveHistoryId(null); }
    } catch { /* silent */ }
    finally { setDeletingId(null); }
  }, [activeHistoryId]);

  const clearAllHistory = useCallback(async () => {
    setConfirmClear(false);
    try {
      await aiApi.clearHistory();
      setChatHistory([]);
      setMessages(starterMessages);
      setActiveHistoryId(null);
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const todayLabel = useMemo(
    () => new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: 'long', year: 'numeric' }),
    []
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const extractAiReply = (data = {}) => {
    const candidates = [
      data?.reply,
      data?.response,
      data?.data?.reply,
      data?.data?.response,
      data?.answer,
      data?.data?.answer,
      data?.message,
      data?.data?.message,
    ];
    return candidates.find((value) => typeof value === 'string' && value.trim())?.trim();
  };

  const getFriendlyAiError = (error) => {
    const status = error?.response?.status;
    const message = error?.message || '';
    if (status === 504 || error?.isTimeout) {
      return 'AI phan hoi qua lau. Vui long thu lai sau it phut.';
    }
    if (message.includes('GOOGLE_API_KEY') || error?.response?.data?.error === 'missing_google_api_key') {
      return 'Backend chua cau hinh GOOGLE_API_KEY nen chua the goi Gemini.';
    }
    return message || 'AI Chat dang tam thoi bi gian doan. Vui long thu lai sau.';
  };

  const createBotResponse = (data = null) => ({
    id: crypto.randomUUID(),
    type: 'bot',
    content: extractAiReply(data) ||
      'Tôi đã nhận được thông tin. Bạn nên bổ sung khu vực canh tác, tuổi cây, ảnh cận cảnh và lịch bón phân gần nhất để tôi phân tích chính xác hơn.',
    timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    source: data ? {
      source: data.source,
      source_name: data.source_name || data.provider,
      is_mock: data.is_mock,
      fallback_used: data.fallback_used || data.is_mock,
      timeout: data.timeout,
      error: data.error,
      confidence: data.confidence,
      fetched_at: data.fetched_at,
    } : null,
    analysis: data?.reasons?.length || data?.recommendations?.length ? {
      diagnosis: data.intent || 'AI farming assistant',
      details: data.reasons || [],
      recommendations: data.recommendations || [],
    } : null,
  });

  const handleSendMessage = async () => {
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage || isTyping) return;

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        type: 'user',
        content: trimmedMessage,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const data = await aiApi.chat({
        question: trimmedMessage,
        crop: 'ca chua',
        region: 'Ha Noi',
        context: 'Nguoi dung dang chat tu trang AI Chat cua frontend NongNghiepAI.',
        userId: 1,
        sessionId: 'frontend-session',
      });
      setMessages((current) => [...current, createBotResponse(data)]);
      loadHistory();
    } catch (error) {
      setMessages((current) => [...current, createBotResponse({
        reply: getFriendlyAiError(error),
        source: 'error',
        source_name: 'AI Chat error',
        is_mock: false,
        fallback_used: true,
        timeout: error?.isTimeout || error?.response?.status === 504,
        error: error?.message,
        confidence: 0,
      })]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);
    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        type: 'user',
        content: `Đã gửi ảnh: ${file.name}`,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        image: imageUrl,
      },
    ]);
    setIsTyping(true);
    window.setTimeout(() => {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          type: 'bot',
          content: 'Tôi đã nhận ảnh. Khi BE xử lý ảnh sẵn sàng, ảnh này sẽ được gửi sang API kiểm định chất lượng.',
          timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
      setIsTyping(false);
    }, 700);
    event.target.value = '';
  };

  const HistoryList = () => (
    <>
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-bold text-gray-900">Lịch sử chat</h2>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={loadHistory}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            title="Tải lại"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          {isAuthenticated && chatHistory.length > 0 && (
            <button
              type="button"
              onClick={() => setConfirmClear(true)}
              className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500"
              title="Xóa tất cả lịch sử"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Storage info badge */}
      {isAuthenticated && (
        <div className="mb-3 flex items-center gap-1.5 rounded-lg bg-gray-50 px-2.5 py-2 text-xs text-gray-500 border border-gray-100">
          <Database className="h-3.5 w-3.5 shrink-0 text-gray-400" />
          <span>Lưu trong <strong>SQL Server</strong> · bảng <code className="bg-gray-200 px-1 rounded text-gray-600">AIConversations</code></span>
        </div>
      )}

      {/* Confirm clear dialog */}
      {confirmClear && (
        <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3">
          <p className="text-xs font-semibold text-red-700 mb-2">Xóa toàn bộ lịch sử chat?</p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={clearAllHistory}
              className="flex-1 rounded-lg bg-red-600 py-1.5 text-xs font-semibold text-white hover:bg-red-700"
            >
              Xóa tất cả
            </button>
            <button
              type="button"
              onClick={() => setConfirmClear(false)}
              className="flex-1 rounded-lg border border-gray-300 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-100"
            >
              Hủy
            </button>
          </div>
        </div>
      )}

      {/* List */}
      <div className="space-y-1.5">
        {historyLoading && (
          <div className="py-6 text-center text-sm text-gray-400">Đang tải lịch sử...</div>
        )}
        {!historyLoading && !isAuthenticated && (
          <div className="rounded-lg bg-gray-50 px-3 py-4 text-center text-xs text-gray-500">
            Đăng nhập để xem lịch sử hội thoại của bạn.
          </div>
        )}
        {!historyLoading && isAuthenticated && chatHistory.length === 0 && (
          <div className="rounded-lg bg-gray-50 px-3 py-4 text-center text-xs text-gray-500">
            Chưa có lịch sử. Hãy bắt đầu hỏi AgriBot!
          </div>
        )}
        {!historyLoading && chatHistory.map((item) => {
          const isActive = activeHistoryId === item.id;
          const isDeleting = deletingId === item.id;
          const topicColors = {
            weather: 'text-sky-600 bg-sky-50',
            price: 'text-emerald-700 bg-emerald-50',
            pest: 'text-orange-600 bg-orange-50',
            cultivation: 'text-green-700 bg-green-50',
            soil_salinity: 'text-blue-600 bg-blue-50',
            soil_acidity: 'text-yellow-700 bg-yellow-50',
          };
          const topicLabel = {
            weather: '🌤 Thời tiết', price: '💰 Giá', pest: '🐛 Sâu bệnh',
            cultivation: '🌱 Canh tác', soil_salinity: '🌊 Đất mặn', soil_acidity: '⚗ Đất phèn',
          };
          return (
            <div
              key={item.id}
              className={`group relative rounded-xl border transition ${
                isActive ? 'border-green-200 bg-green-50' : 'border-transparent hover:border-gray-200 hover:bg-gray-50'
              } ${isDeleting ? 'opacity-40' : ''}`}
            >
              <button
                type="button"
                onClick={() => loadConversation(item)}
                className="w-full p-3 text-left"
              >
                <div className="flex items-start gap-2.5">
                  <div className={`mt-0.5 rounded-lg p-1.5 ${isActive ? 'bg-green-700 text-white' : 'bg-green-100 text-green-700'}`}>
                    <Leaf className="h-3.5 w-3.5" />
                  </div>
                  <div className="min-w-0 flex-1 pr-6">
                    <div className={`truncate text-sm font-semibold ${isActive ? 'text-green-800' : 'text-gray-900'}`}>
                      {item.user_message.length > 48 ? `${item.user_message.slice(0, 48)}…` : item.user_message}
                    </div>
                    {item.ai_response && (
                      <div className="mt-0.5 truncate text-xs text-gray-400">
                        {item.ai_response.replace(/[#*`]/g, '').slice(0, 65)}…
                      </div>
                    )}
                    <div className="mt-1.5 flex items-center gap-2">
                      {item.topic && topicLabel[item.topic] && (
                        <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${topicColors[item.topic] || 'bg-gray-100 text-gray-600'}`}>
                          {topicLabel[item.topic]}
                        </span>
                      )}
                      <span className="text-xs text-gray-400">{formatHistoryTime(item.created_at)}</span>
                    </div>
                  </div>
                </div>
              </button>
              {/* Delete button */}
              <button
                type="button"
                onClick={(e) => deleteMessage(item.id, e)}
                disabled={isDeleting}
                className="absolute right-2 top-2 rounded-lg p-1.5 text-gray-300 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                title="Xóa tin nhắn này"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          );
        })}
      </div>

      <button
        type="button"
        onClick={() => { setMessages(starterMessages); setActiveHistoryId(null); setHistoryOpen(false); }}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-green-700 py-2.5 text-sm font-semibold text-white hover:bg-green-800"
      >
        <Plus className="h-4 w-4" />
        Cuộc hội thoại mới
      </button>
    </>
  );

  return (
    <div className="flex min-h-[calc(100vh-8rem)] gap-6">
      {historyOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-gray-900/50"
            onClick={() => setHistoryOpen(false)}
            aria-label="Đóng lịch sử"
          />
          <aside className="relative h-full w-80 max-w-[86vw] overflow-y-auto bg-white p-4 shadow-xl">
            <button
              type="button"
              onClick={() => setHistoryOpen(false)}
              className="absolute right-3 top-3 rounded-lg p-2 text-gray-500 hover:bg-gray-100"
              aria-label="Đóng lịch sử"
            >
              <X className="h-5 w-5" />
            </button>
            <div className="pt-8">
              <HistoryList />
            </div>
          </aside>
        </div>
      )}

      <aside className="hidden w-72 shrink-0 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4 shadow-sm lg:block">
        <HistoryList />
      </aside>

      <section className="flex min-w-0 flex-1 flex-col rounded-lg border border-gray-200 bg-white shadow-sm">
        <header className="flex items-center justify-between border-b border-gray-200 p-4 md:p-5">
          <div className="flex min-w-0 items-center gap-3">
            <button
              type="button"
              onClick={() => setHistoryOpen(true)}
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 lg:hidden"
              aria-label="Mở lịch sử"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-green-700">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="truncate font-bold text-gray-900">AgriBot AI</h1>
              <div className="flex items-center gap-2 text-sm text-green-700">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                <span className="truncate">Trực tuyến 24/7</span>
              </div>
            </div>
          </div>

          <button type="button" className="rounded-lg p-2 text-gray-600 hover:bg-gray-100" aria-label="Làm mới">
            <RefreshCw className="h-5 w-5" />
          </button>
        </header>

        <div className="flex-1 space-y-5 overflow-y-auto bg-gray-50 p-4 md:p-6">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <Bot className="h-7 w-7 text-green-700" />
            </div>
            <p className="text-sm font-semibold uppercase tracking-wide text-gray-500">{todayLabel}</p>
            <h2 className="mt-2 text-lg font-bold text-gray-900">Tư vấn nông nghiệp theo ngữ cảnh</h2>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              Hỏi về kỹ thuật canh tác, sâu bệnh, giá thị trường hoặc gửi ảnh để chuẩn bị phân tích chất lượng.
            </p>
          </div>

          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`flex max-w-[min(42rem,100%)] items-start gap-3 ${
                  message.type === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <MessageAvatar type={message.type} />
                <div className={message.type === 'user' ? 'text-right' : 'text-left'}>
                  <div
                    className={`rounded-lg p-4 text-sm leading-6 ${
                      message.type === 'bot'
                        ? 'border border-gray-200 bg-white text-gray-700'
                        : 'bg-green-700 text-white'
                    }`}
                  >
                    {message.image && (
                      <img src={message.image} alt="Ảnh đã gửi" className="mb-3 max-h-72 w-full rounded-lg object-cover" />
                    )}
                    {message.type === 'bot' ? (
                      <div className="prose prose-sm max-w-none prose-headings:font-bold prose-headings:text-gray-900 prose-h1:text-base prose-h2:text-sm prose-h3:text-sm prose-p:text-gray-700 prose-p:leading-6 prose-strong:text-gray-900 prose-ul:my-2 prose-ul:space-y-1 prose-ol:my-2 prose-ol:space-y-1 prose-li:text-gray-700 prose-li:leading-6">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p>{message.content}</p>
                    )}
                    {message.source && (
                      <div className="mt-3">
                        <DataSourceBadge data={message.source} />
                      </div>
                    )}

                    {message.analysis && (
                      <div className="mt-4 rounded-lg border border-gray-200 bg-gray-50 p-4 text-left">
                        <div className="text-xs font-semibold uppercase tracking-wide text-green-700">
                          Kết quả tham khảo
                        </div>
                        <div className="mt-2 font-bold text-gray-900">{message.analysis.diagnosis}</div>
                        <div className="mt-3 space-y-2">
                          {message.analysis.details.map((detail) => (
                            <div key={detail} className="text-sm text-gray-700">
                              {detail}
                            </div>
                          ))}
                        </div>
                        <div className="mt-4 space-y-2">
                          {message.analysis.recommendations.map((recommendation) => (
                            <div key={recommendation} className="text-sm text-gray-700">
                              {recommendation}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-gray-500">{message.timestamp}</div>
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-start gap-3">
              <MessageAvatar type="bot" />
              <div className="rounded-lg border border-gray-200 bg-white p-4">
                <div className="mb-2 text-sm text-gray-600">AI dang phan tich...</div>
                <div className="flex gap-2">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:0.15s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:0.3s]" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 bg-white p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            {quickSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setInputMessage(suggestion)}
                className="rounded-lg bg-gray-100 px-3 py-2 text-sm text-gray-700 hover:bg-gray-200"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className="flex items-end gap-2">
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              accept="image/*"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="rounded-lg p-3 text-gray-600 hover:bg-gray-100"
              aria-label="Đính kèm tệp"
            >
              <Paperclip className="h-5 w-5" />
            </button>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="rounded-lg p-3 text-gray-600 hover:bg-gray-100"
              aria-label="Gửi ảnh"
            >
              <ImageIcon className="h-5 w-5" />
            </button>
            <input
              type="text"
              value={inputMessage}
              onChange={(event) => setInputMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !isTyping) handleSendMessage();
              }}
              disabled={isTyping}
              placeholder="Hỏi AgriBot về kỹ thuật, sâu bệnh, giá..."
              className="min-w-0 flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            />
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className="rounded-lg bg-green-700 p-3 text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Gửi tin nhắn"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </section>

      <aside className="hidden w-80 shrink-0 overflow-y-auto rounded-lg border border-gray-200 bg-white p-5 shadow-sm xl:block">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-700">
            <Bot className="h-8 w-8 text-white" />
          </div>
          <h2 className="font-bold text-gray-900">AgriBot AI</h2>
          <p className="mt-2 text-sm text-gray-600">Trợ lý chuyên sâu cho dữ liệu nông nghiệp.</p>
          <div className="mt-3 inline-flex rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">
            Phiên bản demo FE
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wide text-gray-900">Khả năng</h3>
          {capabilities.map((capability) => {
            const Icon = capability.icon;
            return (
              <div key={capability.title} className="flex gap-3 rounded-lg bg-gray-50 p-3">
                <div className="rounded-lg bg-green-100 p-2 text-green-700">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-gray-900">{capability.title}</div>
                  <div className="mt-1 text-xs leading-5 text-gray-600">{capability.description}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-gray-900">Phân tích gần đây</h3>
          {chatHistory.slice(0, 3).map((item) => (
            <div key={item.id} className="rounded-lg bg-gray-50 p-3">
              <div className="text-xs font-semibold text-gray-500">
                {item.created_at ? new Date(item.created_at).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }) : ''}
              </div>
              <div className="mt-1 truncate text-sm font-semibold text-gray-900">
                {item.user_message.length > 45 ? `${item.user_message.slice(0, 45)}…` : item.user_message}
              </div>
              <div className="mt-1 text-xs text-gray-500">{formatHistoryTime(item.created_at)}</div>
            </div>
          ))}
          {chatHistory.length === 0 && !historyLoading && (
            <div className="text-xs text-gray-400">Chưa có phân tích nào.</div>
          )}
        </div>
      </aside>
    </div>
  );
};

export default AIChatPage;
