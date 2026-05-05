class WeatherClient:
    def get_current(self, region: str) -> dict:
        return {
            "region": region,
            "temperature": 30.0,
            "rainfall": 2.5,
            "humidity": 78.0,
            "condition": "partly_cloudy",
        }
