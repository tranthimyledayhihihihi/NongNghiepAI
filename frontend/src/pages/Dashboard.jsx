import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Camera, BarChart3, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const features = [
    {
      title: 'Định giá nông sản',
      description: 'Dự báo giá và phân tích xu hướng thị trường',
      icon: TrendingUp,
      link: '/pricing',
      color: 'bg-blue-500',
    },
    {
      title: 'Kiểm tra chất lượng',
      description: 'Nhận diện chất lượng nông sản qua ảnh',
      icon: Camera,
      link: '/quality',
      color: 'bg-green-500',
    },
    {
      title: 'Dự báo thu hoạch',
      description: 'Dự đoán thời điểm thu hoạch tối ưu',
      icon: BarChart3,
      link: '/harvest',
      color: 'bg-purple-500',
    },
    {
      title: 'Cảnh báo giá',
      description: 'Nhận thông báo khi giá biến động',
      icon: AlertCircle,
      link: '/alerts',
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Chào mừng đến với AgriAI
        </h1>
        <p className="mt-2 text-gray-600">
          Hệ thống AI hỗ trợ nông dân - Dự báo thu hoạch & Định giá nông sản
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.title}
              to={feature.link}
              className="relative group bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <div>
                <span
                  className={`${feature.color} rounded-lg inline-flex p-3 ring-4 ring-white`}
                >
                  <Icon className="h-6 w-6 text-white" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900 group-hover:text-primary-600">
                  {feature.title}
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {feature.description}
                </p>
              </div>
              <span
                className="absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                aria-hidden="true"
              >
                <svg
                  className="h-6 w-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                </svg>
              </span>
            </Link>
          );
        })}
      </div>

      {/* Quick Stats */}
      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Giá trung bình hôm nay
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    20,000 đ/kg
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BarChart3 className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Xu hướng giá
                  </dt>
                  <dd className="text-lg font-medium text-green-600">
                    ↑ Tăng 5%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Camera className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Ảnh đã kiểm tra
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    0
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
