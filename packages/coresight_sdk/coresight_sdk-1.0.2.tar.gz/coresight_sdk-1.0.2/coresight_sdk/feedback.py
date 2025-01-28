class Feedback:
    def __init__(self, request_handler,project_id):
        self.request_handler = request_handler
        self.project_id = project_id

    def add(self, message_id: str, user_id: str, rating: int, comment: str = "") -> dict:
        """
        Add feedback for a message.
        """
        payload = {"user_id": user_id, "rating": rating, "comment": comment}
        return self.request_handler.post(f"projects/{self.project_id}/threads/{thread_id}/messages/{message_id}/feedback", payload)

    def list(self, message_id: str) -> list:
        """
        List all feedback for a message.
        """
        return self.request_handler.get(f"projects/{self.project_id}/threads/{thread_id}/messages/{message_id}/feedback")
