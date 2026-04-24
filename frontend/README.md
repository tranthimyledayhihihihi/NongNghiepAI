# Frontend - AgriAI

React frontend cho hệ thống AgriAI.

## Structure

```
frontend/
├── src/
│   ├── components/   # Reusable components
│   ├── pages/        # Page components
│   │   ├── Dashboard.jsx
│   │   ├── QualityPage.jsx
│   │   └── PricingPage.jsx
│   ├── services/     # API clients
│   ├── App.jsx       # Main app
│   └── main.jsx      # Entry point
├── public/           # Static files
└── package.json      # Dependencies
```

## Quick Start

### With Docker
```bash
docker-compose up -d frontend
```

### Local Development
```bash
cd frontend
npm install
npm run dev
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Chart.js
- React Router
- Axios

## Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Pages

- `/` - Dashboard (tổng quan)
- `/quality` - Quality check (kiểm tra chất lượng)
- `/pricing` - Pricing (định giá)

## API Integration

API services in `src/services/`:
- `api.js` - Base API client
- `qualityApi.js` - Quality check API
- `pricingApi.js` - Pricing API
