class EmailClient:
    def send(self, receiver: str, subject: str, message: str) -> dict:
        return {
            "receiver": receiver,
            "subject": subject,
            "message": message,
            "status": "mock_sent",
        }
