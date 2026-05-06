import {
  AlertCircle,
  Bot,
  Clock,
  Image as ImageIcon,
  Leaf,
  Menu,
  MoreVertical,
  Paperclip,
  Plus,
  RefreshCw,
  Send,
  Sparkles,
  TrendingUp,
  User,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

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

const chatHistory = [
  {
    id: 1,
    title: 'Tư vấn sâu bệnh lúa',
    subtitle: 'Bệnh đạo ôn lá',
    description: 'Dựa trên ảnh ruộng lúa 40 ngày tuổi...',
    time: '10:45',
    icon: Leaf,
    color: 'text-green-700 bg-green-50',
  },
  {
    id: 2,
    title: 'Dự báo giá cà phê',
    subtitle: 'Thị trường Tây Nguyên',
    description: 'Giá dự báo tăng trong tuần tới...',
    time: '08:12',
    icon: TrendingUp,
    color: 'text-amber-700 bg-amber-50',
  },
  {
    id: 3,
    title: 'Kỹ thuật bón phân',
    subtitle: 'Quy trình 4 đợt',
    description: 'Bón phân đạm cần lưu ý giai đoạn sinh trưởng...',
    time: 'Hôm qua',
    icon: AlertCircle,
    color: 'text-blue-700 bg-blue-50',
  },
];

const quickSuggestions = [
  'Lập kế hoạch canh tác cho vụ tới',
  'Cảnh báo thời tiết xấu tuần này',
  'Dự báo giá cà phê tại Tây Nguyên',
  'Phân tích lịch bón phân cho lúa',
];

const capabilities = [
  {
    icon: Clock,
    title: 'Hỗ trợ liên tục',
    description: 'Gợi ý xử lý nhanh cho giá, thời tiết và mùa vụ.',
  },
  {
    icon: Sparkles,
    title: 'Phân tích theo ngữ cảnh',
    description: 'Kết hợp cây trồng, khu vực và lịch canh tác.',
  },
  {
    icon: Leaf,
    title: 'Tư vấn nông nghiệp',
    description: 'Trả lời về sâu bệnh, dinh dưỡng và thu hoạch.',
  },
];

const analysisHistory = [
  { id: 1, date: '14/05', title: 'Chẩn đoán bệnh đạo ôn', time: '4 hôm trước' },
  { id: 2, date: '12/05', title: 'Kiểm tra dinh dưỡng lá', time: '6 ngày trước' },
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
  const [messages, setMessages] = useState(initialMessages);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const todayLabel = useMemo(
    () => new Date().toLocaleDateString('vi-VN', { day: '2-digit', month: 'long', year: 'numeric' }),
    []
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const createBotResponse = () => ({
    id: crypto.randomUUID(),
    type: 'bot',
    content:
      'Tôi đã nhận được thông tin. Bạn nên bổ sung khu vực canh tác, tuổi cây, ảnh cận cảnh và lịch bón phân gần nhất để tôi phân tích chính xác hơn.',
    timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
  });

  const handleSendMessage = () => {
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage) return;

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

    window.setTimeout(() => {
      setMessages((current) => [...current, createBotResponse()]);
      setIsTyping(false);
    }, 900);
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
      <div className="mb-5 flex items-center justify-between">
        <h2 className="font-bold text-gray-900">Lịch sử chat</h2>
        <button type="button" className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <MoreVertical className="h-5 w-5" />
        </button>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-2">
        <button type="button" className="rounded-lg bg-green-700 px-3 py-2 text-sm font-medium text-white">
          Lịch sử
        </button>
        <button type="button" className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100">
          Gợi ý
        </button>
      </div>

      <div className="space-y-3">
        {chatHistory.map((chat) => {
          const Icon = chat.icon;
          return (
            <button
              key={chat.id}
              type="button"
              onClick={() => setHistoryOpen(false)}
              className="w-full rounded-lg p-3 text-left transition hover:bg-gray-50"
            >
              <div className="flex items-start gap-3">
                <div className={`rounded-lg p-2 ${chat.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-semibold text-gray-900">{chat.title}</div>
                  <div className="mt-1 text-xs text-gray-600">{chat.subtitle}</div>
                  <div className="mt-1 truncate text-xs text-gray-500">{chat.description}</div>
                  <div className="mt-2 text-xs text-gray-400">{chat.time}</div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-green-700 py-3 font-medium text-white hover:bg-green-800"
      >
        <Plus className="h-5 w-5" />
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
                    <p>{message.content}</p>

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
                if (event.key === 'Enter') handleSendMessage();
              }}
              placeholder="Hỏi AgriBot về kỹ thuật, sâu bệnh, giá..."
              className="min-w-0 flex-1 rounded-lg border border-gray-300 px-4 py-3 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
            />
            <button
              type="button"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim()}
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
          {analysisHistory.map((item) => (
            <div key={item.id} className="rounded-lg bg-gray-50 p-3">
              <div className="text-xs font-semibold text-gray-500">{item.date}</div>
              <div className="mt-1 text-sm font-semibold text-gray-900">{item.title}</div>
              <div className="mt-1 text-xs text-gray-500">{item.time}</div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
};

export default AIChatPage;
