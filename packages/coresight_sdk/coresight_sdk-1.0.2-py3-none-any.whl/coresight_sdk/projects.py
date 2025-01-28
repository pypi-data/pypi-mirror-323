class Projects:
    def __init__(self, request_handler):
        self.request_handler = request_handler

    def create(self, name: str, llm_config: dict) -> dict:
        """
        Create a new project.
        """
        payload = {"name": name, "llm_config": llm_config}
        return self.request_handler.post("/projects", payload)

    def get(self, project_id: str) -> dict:
        """
        Retrieve details of a specific project.
        """
        return self.request_handler.get(f"/projects/{project_id}")

    
    def get_from_key(self, api_key: str) -> dict:
        """
        Retrieve details of a specific project.
        """
        return self.request_handler.get(f"/projects/from_api_key")

    def list(self) -> list:
        """
        List all projects for the client.
        """
        return self.request_handler.get("/projects")

    def update(self, project_id: str, updates: dict) -> dict:
        """
        Update a project's details.
        """
        return self.request_handler.put(f"/projects/{project_id}", updates)

    def delete(self, project_id: str) -> dict:
        """
        Delete a project.
        """
        return self.request_handler.delete(f"/projects/{project_id}")
