class ZaloClient:
    def send(self, receiver: str, message: str) -> dict:
        return {
            "receiver": receiver,
            "message": message,
            "status": "mock_sent",
        }
