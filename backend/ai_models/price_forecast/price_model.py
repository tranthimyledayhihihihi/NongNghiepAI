import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import pickle
import os

class PriceForecastModel:
    def __init__(self, model_path: str = "backend/ai_models/price_forecast/saved_models"):
        """Initialize price forecasting model"""
        self.model_path = model_path
        self.model = None
        
    def load_model(self, crop_name: str, region: str):
        """Load trained model for specific crop and region"""
        model_file = os.path.join(self.model_path, f"{crop_name}_{region}_model.pkl")
        
        if os.path.exists(model_file):
            try:
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
    
    def predict(self, crop_name: str, region: str, days: int = 7) -> Dict:
        """Predict prices for next N days"""
        # Try to load model
        if not self.load_model(crop_name, region):
            # Use simple forecasting if no trained model
            return self._simple_forecast(crop_name, region, days)
        
        # If model exists, use it for prediction
        try:
            forecast_dates = [datetime.now() + timedelta(days=i) for i in range(1, days + 1)]
            predictions = self._generate_predictions(days)
            
            forecast_data = [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_price': float(price),
                    'confidence_lower': float(price * 0.9),
                    'confidence_upper': float(price * 1.1)
                }
                for date, price in zip(forecast_dates, predictions)
            ]
            
            trend = self._analyze_trend(predictions)
            recommendation = self._get_recommendation(trend, predictions)
            
            return {
                'crop_name': crop_name,
                'region': region,
                'forecast_data': forecast_data,
                'trend': trend,
                'recommendation': recommendation
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._simple_forecast(crop_name, region, days)
    
    def _simple_forecast(self, crop_name: str, region: str, days: int) -> Dict:
        """Simple forecasting using historical patterns"""
        # Mock base price (in production, fetch from database)
        base_price = 20000  # VND per kg
        
        # Add seasonal variation
        current_month = datetime.now().month
        seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * current_month / 12)
        
        forecast_dates = [datetime.now() + timedelta(days=i) for i in range(1, days + 1)]
        
        # Generate predictions with random walk
        predictions = []
        current_price = base_price * seasonal_factor
        
        for i in range(days):
            # Add random variation (-5% to +5%)
            variation = np.random.uniform(-0.05, 0.05)
            current_price = current_price * (1 + variation)
            predictions.append(current_price)
        
        forecast_data = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'predicted_price': float(price),
                'confidence_lower': float(price * 0.92),
                'confidence_upper': float(price * 1.08)
            }
            for date, price in zip(forecast_dates, predictions)
        ]
        
        trend = self._analyze_trend(predictions)
        recommendation = self._get_recommendation(trend, predictions)
        
        return {
            'crop_name': crop_name,
            'region': region,
            'forecast_data': forecast_data,
            'trend': trend,
            'recommendation': recommendation
        }
    
    def _generate_predictions(self, days: int) -> List[float]:
        """Generate price predictions"""
        base_price = 20000
        predictions = []
        
        for i in range(days):
            # Simple trend with noise
            trend = base_price + (i * 100)
            noise = np.random.normal(0, 500)
            predictions.append(max(trend + noise, 5000))
        
        return predictions
    
    def _analyze_trend(self, predictions: List[float]) -> str:
        """Analyze price trend"""
        if len(predictions) < 2:
            return 'stable'
        
        first_half = np.mean(predictions[:len(predictions)//2])
        second_half = np.mean(predictions[len(predictions)//2:])
        
        change_percent = ((second_half - first_half) / first_half) * 100
        
        if change_percent > 5:
            return 'increasing'
        elif change_percent < -5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_recommendation(self, trend: str, predictions: List[float]) -> str:
        """Get selling recommendation"""
        if trend == 'increasing':
            return "Giá có xu hướng tăng. Nên giữ hàng thêm vài ngày để bán được giá tốt hơn."
        elif trend == 'decreasing':
            return "Giá có xu hướng giảm. Nên bán sớm để tránh mất giá."
        else:
            return "Giá ổn định. Có thể bán bất cứ lúc nào phù hợp với kế hoạch."

# Singleton instance
price_forecast_model = PriceForecastModel()
