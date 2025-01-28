class Messages:
    def __init__(self, request_handler,project_id):
        self.request_handler = request_handler
        self.project_id = project_id

    def create(self, user_id: str, thread_id: str, sender_id: str, content: str) -> dict:
        """
        Create a new message in a thread.
        """
        payload = {"sender": sender_id, "content": content}
        return self.request_handler.post(f"projects/{self.project_id}/users/{user_id}/threads/{thread_id}/messages", payload)

    def list(self,user_id:str, thread_id: str) -> list:
        """
        Retrieve all messages in a thread.
        """
        return self.request_handler.get(f"projects/{self.project_id}/users/{user_id}/threads/{thread_id}/messages")
