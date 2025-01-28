class Threads:
    def __init__(self, request_handler,project_id):
        self.request_handler = request_handler
        self.project_id = project_id

    def create(self, user_id: str) -> dict:
        """
        Create a new thread in the project.
        """
        print(user_id)
        return self.request_handler.post(f"projects/{self.project_id}/users/{user_id}/threads",payload={"user_id":user_id})

    def get(self, thread_id: str,user_id: str) -> dict:
        """
        Retrieve a specific thread.
        """
        return self.request_handler.get(f"projects/{self.project_id}/users/{user_id}/threads/{thread_id}")

    def list(self,user_id: str) -> list:
        """
        List all threads in the project.
        """
        return self.request_handler.get(f"projects/{self.project_id}/users/{user_id}/threads")
