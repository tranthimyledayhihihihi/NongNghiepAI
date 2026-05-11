import pandas as pd
import logging
import numpy as np
from datetime import timedelta

logger = logging.getLogger(__name__)

class PricePredictor:
    def predict(self, historical_data: list[dict], days: int = 7) -> list[dict]:
        """
        Dự báo giá sử dụng thuật toán Exponential Moving Average (EMA) nâng cao.
        historical_data: Danh sách dict [{'date': '2023-01-01', 'price': 15000}, ...]
        """
        if not historical_data:
            logger.warning("Không có dữ liệu lịch sử để dự báo.")
            return []
            
        try:
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').set_index('date')
            
            # Đảm bảo có đủ dữ liệu cho tính toán EMA.
            # Một quy tắc chung cho EMA là cần ít nhất 2*span điểm dữ liệu để ổn định.
            # Sử dụng tối thiểu 30 ngày cho EMA 14 ngày để có độ tin cậy nhất định.
            min_data_points = 30 
            if len(df) < min_data_points:
                logger.warning(f"Không đủ dữ liệu lịch sử để dự báo chính xác bằng EMA (Cần >= {min_data_points} ngày).")
                return []

            # Tính toán EMA (ví dụ: EMA 14 ngày, phổ biến cho phân tích ngắn hạn)
            ema_span = 14 # Khoảng thời gian EMA phổ biến cho ngắn hạn
            df['ema'] = df['price'].ewm(span=ema_span, adjust=False).mean()
            
            # Lấy giá trị EMA cuối cùng
            last_ema = df['ema'].iloc[-1]
            
            # Xác định xu hướng đơn giản từ các giá trị EMA gần đây
            # So sánh EMA cuối cùng với EMA từ `trend_period` ngày trước
            trend_period = 7 # Xem xét xu hướng trong 7 ngày gần nhất
            if len(df) >= ema_span + trend_period: 
                ema_past = df['ema'].iloc[-trend_period -1] # Giá trị EMA `trend_period` ngày trước
                trend_per_day = (last_ema - ema_past) / trend_period
            else:
                # Nếu không đủ dữ liệu cho xu hướng mạnh mẽ, giả định xu hướng rất nhẹ hoặc không có xu hướng
                if len(df) > ema_span:
                    trend_per_day = (last_ema - df['ema'].iloc[-ema_span]) / ema_span
                else:
                    trend_per_day = 0 

            # Tạo dự báo cho tương lai
            predictions = []
            for i in range(1, days + 1):
                forecast_date = df.index[-1] + timedelta(days=i)
                # Dự phóng giá trị EMA cuối cùng với xu hướng đã tính
                predicted_price = last_ema + (trend_per_day * i)
                
                # Đảm bảo giá không âm
                predicted_price = max(0.0, predicted_price)
            
                # Thêm khoảng tin cậy (ví dụ: +/- 5% của giá dự báo)
                # Đây là một phương pháp heuristic đơn giản. Một phương pháp mạnh mẽ hơn sẽ liên quan đến biến động lịch sử
                # hoặc khoảng dự báo từ một mô hình phức tạp hơn.
                min_price = predicted_price * 0.95
                max_price = predicted_price * 1.05
                
                predictions.append({
                    "date": forecast_date.strftime('%Y-%m-%d'),
                    "predicted_price": round(predicted_price, 2),
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2)
                })
            
            return predictions
        except Exception as e:
            logger.error(f"Lỗi khi chạy model dự báo EMA: {e}")
            return []