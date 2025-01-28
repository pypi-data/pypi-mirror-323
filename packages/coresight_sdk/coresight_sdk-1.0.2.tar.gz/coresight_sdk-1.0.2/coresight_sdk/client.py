from coresight_sdk.users import Users
from coresight_sdk.threads import Threads
from coresight_sdk.messages import Messages
from coresight_sdk.feedback import Feedback
from coresight_sdk.utils import APIRequestHandler

class ProjectClient:
    def __init__(self, api_key: str,base_api_url :str = "http://127.0.0.1:3000/") -> None:
        """
        Initialize the SDK for a specific project.

        :param api_key: API key associated with the project.
        """
        self.api_key = api_key
        self.base_api_url = base_api_url
        self.request_handler = APIRequestHandler(self.base_api_url, self.api_key)
        self.project_id = self.get_from_key()['project_id']
        # Initialize project-scoped modules
        self.users = Users(self.request_handler,self.project_id)
        self.threads = Threads(self.request_handler,self.project_id)
        self.messages = Messages(self.request_handler,self.project_id)
        self.feedback = Feedback(self.request_handler,self.project_id)

    def health_check(self) -> dict:
        """
        Test the API connection with a health check endpoint.
        """
        return self.request_handler.get("/health")

    def get_from_key(self) -> dict:
        """
        Retrieve details of a specific project.
        """
        return self.request_handler.get(f"/projects/from_api_key")