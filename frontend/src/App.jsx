import { useState } from 'react';
import { Route, BrowserRouter as Router, Routes, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import AIChatPage from './pages/AIChatPage';
import AlertManagementPage from './pages/AlertManagementPage';
import AlertPage from './pages/AlertPage';
import CropDetailPage from './pages/CropDetailPage';
import Dashboard from './pages/Dashboard';
import HarvestForecastPage from './pages/HarvestForecastPage';
import HarvestPage from './pages/HarvestPage';
import LandingPage from './pages/LandingPage';
import MarketPage from './pages/MarketPage';
import MarketStrategyPage from './pages/MarketStrategyPage';
import NewDashboard from './pages/NewDashboard';
import PricingDashboard from './pages/PricingDashboard';
import PricingPage from './pages/PricingPage';
import ProfilePage from './pages/ProfilePage';
import QualityCheckPage from './pages/QualityCheckPage';
import QualityPage from './pages/QualityPage';
import ReportsPage from './pages/ReportsPage';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  // Check if current route is landing page
  const isLandingPage = location.pathname === '/';

  // If landing page, render without sidebar/navbar
  if (isLandingPage) {
    return <LandingPage />;
  }

  // Otherwise render with sidebar and navbar
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <Navbar setSidebarOpen={setSidebarOpen} />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          <Routes>
            {/* Dashboard Routes */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/dashboard-new" element={<NewDashboard />} />

            {/* Pricing Routes */}
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/pricing-dashboard" element={<PricingDashboard />} />
            <Route path="/crop/:cropId" element={<CropDetailPage />} />

            {/* Quality Routes */}
            <Route path="/quality" element={<QualityPage />} />
            <Route path="/quality-check" element={<QualityCheckPage />} />

            {/* Harvest Routes */}
            <Route path="/harvest" element={<HarvestPage />} />
            <Route path="/harvest-forecast" element={<HarvestForecastPage />} />
            <Route path="/season-management" element={<SeasonManagementPage />} />

            {/* Market Routes */}
            <Route path="/market" element={<MarketPage />} />
            <Route path="/market-strategy" element={<MarketStrategyPage />} />

            {/* Alert Routes */}
            <Route path="/alerts" element={<AlertPage />} />
            <Route path="/alerts-management" element={<AlertManagementPage />} />

            {/* Reports, AI & Profile Routes */}
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/ai-chat" element={<AIChatPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
