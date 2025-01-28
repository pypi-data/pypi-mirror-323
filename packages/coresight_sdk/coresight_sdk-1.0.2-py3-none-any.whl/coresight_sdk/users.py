class Users:
    def __init__(self, request_handler,project_id):
        self.request_handler = request_handler
        self.project_id = project_id

    def create_anonymous(self, session_id: str) -> dict:
        """
        Create an anonymous user in the project.
        """
        payload = {"session_id": session_id}
        return self.request_handler.post(f"/projects/{self.project_id}/anonymous-users", payload)

    def create_authenticated(self, email: str, name: str, metadata: dict = None) -> dict:
        """
        Create an authenticated user in the project.
        """
        payload = {"email": email, "name": name, "metadata": metadata or {}}
        return self.request_handler.post(f"/projects/{self.project_id}/authenticated-users", payload)

    def list(self) -> list:
        """
        List all users in the project.
        """
        return self.request_handler.get(f"/projects/{self.project_id}/users")

    def get(self,email:str):
        payload = {"email": email}
        return self.request_handler.get(f"/projects/{self.project_id}/users",params=payload)