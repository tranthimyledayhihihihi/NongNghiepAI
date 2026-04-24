import { Link, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import AlertPage from './pages/AlertPage';
import Dashboard from './pages/Dashboard';
import HarvestPage from './pages/HarvestPage';
import MarketPage from './pages/MarketPage';
import PricingPage from './pages/PricingPage';
import QualityPage from './pages/QualityPage';
function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-2xl font-bold text-primary-600">🌾 AgriAI</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Tổng quan
                  </Link>
                  <Link
                    to="/pricing"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Định giá
                  </Link>
                  <Link
                    to="/quality"
                    className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    Kiểm tra chất lượng
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/quality" element={<QualityPage />} />
            <Route path="/harvest" element={<HarvestPage />} />
            <Route path="/market" element={<MarketPage />} />
            <Route path="/alerts" element={<AlertPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
