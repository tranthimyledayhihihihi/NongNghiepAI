import {
  AlertCircle,
  Bot,
  Clock,
  Image as ImageIcon,
  Leaf,
  MoreVertical,
  Paperclip,
  Plus,
  RefreshCw,
  Send,
  Share2,
  Sparkles,
  TrendingUp,
  User
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

const AIChatPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Chào bạn! Tôi là AgriBot AI. Tôi đã nhận được hình ảnh ruộng lúa của bạn. Để có kết quả phân tích chính xác nhất, bạn hãy cung cấp thêm ảnh chụp cận cảnh mặt dưới của lá bị vàng nhé. Tôi sẽ phân tích ngay lập tức!',
      timestamp: '10:45 AM',
      avatar: <Bot className="w-6 h-6 text-white" />
    },
    {
      id: 2,
      type: 'user',
      content: 'Đây là ảnh tôi vừa chụp sáng nay ở ruộng lúa 40 ngày tuổi. Vừa bSánh lại khá nhanh.',
      timestamp: '10:43 AM',
      image: 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&h=400&fit=crop',
      avatar: <User className="w-6 h-6 text-white" />
    },
    {
      id: 3,
      type: 'bot',
      content: 'Phân tích chẩn đoán:',
      timestamp: '10:43 AM',
      avatar: <Bot className="w-6 h-6 text-white" />,
      analysis: {
        title: 'TRÍ TUỆ NHÂN TẠO',
        diagnosis: 'Phân tích chẩn đoán:',
        details: [
          'Bệnh đạo ôn lúa (Pyricularia oryzae)',
          'Mức độ: Trung bình đến nặng',
          'Nguyên nhân: Độ ẩm cao + nhiệt độ 25-28°C',
          'Khuyến nghị xử lý:'
        ],
        recommendations: [
          '1. Phun thuốc Tricyclazole 75% WP (20g/bình 16L)',
          '2. Giảm tưới nước, tăng thông thoáng',
          '3. Bón bổ sung Kali để tăng sức đề kháng',
          '4. Theo dõi sát trong 7-10 ngày tới'
        ]
      }
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Chat history sidebar
  const chatHistory = [
    {
      id: 1,
      title: 'TWVLp sâu bệnh lúa',
      subtitle: 'Bệnh Đạo ôn lá',
      description: 'Dựa trên hình ảnh này...',
      time: '10:45',
      icon: <Leaf className="w-5 h-5 text-green-600" />
    },
    {
      id: 2,
      title: 'DY báo giá cà phê',
      subtitle: 'Thị trường Tây Nguyên',
      description: 'Giá dự báo tăng 2%...',
      time: '08:12',
      icon: <TrendingUp className="w-5 h-5 text-orange-600" />
    },
    {
      id: 3,
      title: 'Kỹ thuật bón phân',
      subtitle: 'Quy trình 4 đợng',
      description: 'Bón phân đạm cần lưu ý...',
      time: 'Hôm qua',
      icon: <AlertCircle className="w-5 h-5 text-blue-600" />
    }
  ];

  // Quick suggestions
  const quickSuggestions = [
    'Lập kế hoạch canh tác',
    'Cảnh báo thời tiết xấu',
    'Dự báo thị trường chính xác',
    'Phân tích lịch bón phân'
  ];

  // AgriBot capabilities
  const capabilities = [
    {
      icon: <Clock className="w-5 h-5" />,
      title: 'Hỗ trợ 24/7 lúc nào',
      description: 'Phản hồi lịch bón phân'
    },
    {
      icon: <Sparkles className="w-5 h-5" />,
      title: 'Dự báo thị trường chính xác',
      description: 'Dự báo thị trường chính xác'
    },
    {
      icon: <Leaf className="w-5 h-5" />,
      title: 'Đa ngôn ngữ & Vùng',
      description: 'Đa ngôn ngữ & Vùng'
    }
  ];

  // Analysis history
  const analysisHistory = [
    {
      id: 1,
      date: '14 Th5',
      title: 'Chẩn đoán Bệnh ôn',
      time: '4 hôm trước'
    },
    {
      id: 2,
      date: '12 Th5',
      title: 'Kiểm tra độ dinh dưỡng',
      time: '6 ngày'
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    const newMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      avatar: <User className="w-6 h-6 text-white" />
    };

    setMessages([...messages, newMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        type: 'bot',
        content: 'Tôi đã nhận được câu hỏi của bạn. Để tư vấn chính xác nhất, bạn có thể cung cấp thêm thông tin về...',
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        avatar: <Bot className="w-6 h-6 text-white" />
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Handle file upload
      console.log('File uploaded:', file);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6">
      {/* Left Sidebar - Chat History */}
      <div className="w-64 bg-white rounded-2xl shadow-sm border border-gray-200 p-4 flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-bold text-gray-900">Lịch sử chat</h2>
          <button className="text-gray-400 hover:text-gray-600">
            <MoreVertical className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center space-x-2 mb-6">
          <button className="flex-1 px-3 py-2 bg-green-700 text-white rounded-lg text-sm font-medium">
            Lịch sử chat
          </button>
          <button className="flex-1 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">
            Gợi ý
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3">
          {chatHistory.map((chat) => (
            <div
              key={chat.id}
              className="p-3 hover:bg-gray-50 rounded-xl cursor-pointer transition"
            >
              <div className="flex items-start space-x-3">
                <div className="bg-gray-100 rounded-lg p-2">
                  {chat.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 text-sm mb-1 truncate">
                    {chat.title}
                  </div>
                  <div className="text-xs text-gray-600 mb-1">
                    {chat.subtitle}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {chat.description}
                  </div>
                </div>
              </div>
              <div className="text-xs text-gray-400 mt-2">{chat.time}</div>
            </div>
          ))}
        </div>

        <button className="w-full mt-4 bg-green-700 text-white py-3 rounded-xl font-medium hover:bg-green-800 transition flex items-center justify-center space-x-2">
          <Plus className="w-5 h-5" />
          <span>Cuộc hội thoại mới</span>
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-green-700 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-gray-900">AgriBot AI</h2>
              <div className="flex items-center space-x-2 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Trí tuệ nhân tạo • Trực tuyến 24/7</span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition">
              <RefreshCw className="w-5 h-5 text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition">
              <Share2 className="w-5 h-5 text-gray-600" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition">
              <MoreVertical className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
          {/* Welcome Message */}
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Bot className="w-8 h-8 text-green-700" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              HÔM NAY, 14 THÁNG 5
            </h3>
            <p className="text-sm text-gray-600 mb-4">PHẢN HỒI TỪ AI</p>
            <p className="text-gray-700 max-w-md mx-auto">
              Chào bạn! Tôi là AgriBot AI. Tôi đã nhận được hình ảnh ruộng lúa của bạn.
              Để có kết quả phân tích chính xác nhất, bạn hãy cung cấp thêm ảnh chụp cận
              cảnh mặt dưới của lá bị vàng nhé. Tôi sẽ phân tích ngay lập tức!
            </p>
          </div>

          {/* Messages */}
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-2xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${message.type === 'bot' ? 'bg-green-700' : 'bg-gray-700'
                  }`}>
                  {message.avatar}
                </div>
                <div className={`flex-1 ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`rounded-2xl p-4 ${message.type === 'bot'
                      ? 'bg-white border border-gray-200'
                      : 'bg-green-700 text-white'
                    }`}>
                    {message.image && (
                      <img
                        src={message.image}
                        alt="Uploaded"
                        className="rounded-xl mb-3 w-full"
                      />
                    )}
                    <p className={`text-sm ${message.type === 'bot' ? 'text-gray-700' : 'text-white'}`}>
                      {message.content}
                    </p>

                    {message.analysis && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                        <div className="text-xs text-gray-500 mb-2">{message.analysis.title}</div>
                        <div className="font-bold text-gray-900 mb-3">{message.analysis.diagnosis}</div>
                        {message.analysis.details.map((detail, idx) => (
                          <div key={idx} className="text-sm text-gray-700 mb-1">
                            {detail}
                          </div>
                        ))}
                        <div className="mt-3 space-y-1">
                          {message.analysis.recommendations.map((rec, idx) => (
                            <div key={idx} className="text-sm text-gray-700">
                              {rec}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className={`text-xs text-gray-500 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'
                    }`}>
                    {message.timestamp}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-green-700 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-4">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestions */}
        <div className="px-6 py-3 border-t border-gray-200 bg-white">
          <div className="flex items-center space-x-2 text-xs text-gray-500 mb-2">
            <Sparkles className="w-4 h-4" />
            <span>GỢI Ý CÂU HỎI</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(suggestion)}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-gray-200 bg-white">
          <div className="flex items-end space-x-3">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept="image/*"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 hover:bg-gray-100 rounded-lg transition"
            >
              <Paperclip className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 hover:bg-gray-100 rounded-lg transition"
            >
              <ImageIcon className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Hỏi AgriBot về kỹ thuật, sâu bệnh, giá..."
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={inputMessage.trim() === ''}
              className="p-3 bg-green-700 text-white rounded-xl hover:bg-green-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>💡 GỢI Ý CÂU HỎI</span>
            <span>✉️ XEM LỊCH SỬ</span>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Bot Info */}
      <div className="w-80 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-green-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot className="w-10 h-10 text-white" />
          </div>
          <h3 className="font-bold text-gray-900 mb-2">
            Thông tin về AgriBot
          </h3>
          <p className="text-sm text-gray-600">
            Trí tuệ nhân tạo chuyên sâu Nông nghiệp
          </p>
          <div className="inline-block bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold mt-3">
            PHIÊN BẢN V2.5
          </div>
        </div>

        <div className="space-y-4 mb-6">
          <h4 className="font-bold text-gray-900 text-sm">KHẢ NĂNG CỦA AI</h4>
          {capabilities.map((capability, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-xl">
              <div className="bg-green-100 rounded-lg p-2 text-green-700">
                {capability.icon}
              </div>
              <div>
                <div className="font-medium text-gray-900 text-sm mb-1">
                  {capability.title}
                </div>
                <div className="text-xs text-gray-600">
                  {capability.description}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-3 mb-6">
          <h4 className="font-bold text-gray-900 text-sm">TÍNH NĂNG GỢI Ý</h4>
          {['Lập kế hoạch canh tác', 'Cảnh báo thời tiết xấu'].map((feature, index) => (
            <button
              key={index}
              className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition text-sm text-gray-700"
            >
              {feature}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <h4 className="font-bold text-gray-900 text-sm flex items-center justify-between">
            <span>LỊCH SỬ PHÂN TÍCH</span>
            <span className="w-6 h-6 bg-orange-100 text-orange-700 rounded-full flex items-center justify-center text-xs font-bold">
              •
            </span>
          </h4>
          {analysisHistory.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-xs font-bold text-gray-700 mb-1">
                  {item.date}
                </div>
                <div className="text-xs text-gray-600">{item.title}</div>
                <div className="text-xs text-gray-500">{item.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AIChatPage;
