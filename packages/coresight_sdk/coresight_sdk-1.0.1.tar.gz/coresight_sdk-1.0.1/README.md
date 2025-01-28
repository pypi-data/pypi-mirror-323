# Coresight Python SDK

This Python SDK (`coresight_sdk`) provides a convenient interface to the **Multi-Tenant Messaging API** as defined by the provided `openapi.yaml`. It supports:

- **Client Management**: Create, retrieve, and update client information.  
- **User Management**: Create and retrieve both anonymous and authenticated users.  
- **Threads & Messages**: Create new threads, post messages, and retrieve message history.  
- **Feedback**: Provide feedback on messages.  
- **LLM Chat**: Interact with a Large Language Model endpoint.  
- **Subscriptions**: Manage subscriptions, create, update, and cancel.

---

## Installation

1. **Clone** or **download** this repository to your local machine.  
2. **Install Poetry** if you haven't already (see [Poetry Installation](https://python-poetry.org/docs/#installation)).
3. In the project root (where `pyproject.toml` is located), run:
   ```bash
   poetry install
   ```
   This installs all dependencies in a virtual environment and makes the SDK available for import.

---

## Usage

### Basic Example

```python
from coresight_sdk.client import CoresightClient

# 1. Initialize the SDK client
client = CoresightClient(
    base_url="https://myapi.execute-api.myregion.amazonaws.com/Prod",
    api_key="YOUR_API_KEY"  # Optional but required for endpoints needing x-api-key
)

# 2. Sign up a new client
signup_response = client.sign_up(
    name="John Doe",
    email="[email protected]",
    password="Secret123",
    package="Free"  # one of "Free", "Basic", "Premium"
)
print("Sign-up response:", signup_response)

# 3. Log in an existing client
login_response = client.login(
    email="[email protected]",
    password="Secret123"
)
print("Login token:", login_response.get("token"))

# 4. Create a new thread (requires valid x-api-key)
thread_response = client.create_thread(client_id=signup_response["client_id"])
print("New thread:", thread_response)

# 5. Create a message in the thread
message_response = client.create_message(
    client_id=signup_response["client_id"],
    thread_id=thread_response["thread_id"],
    user_input="Hello, I'd like some help with an issue."
)
print("Message created:", message_response)
```

### Additional Endpoints

- **Clients**: `get_client`, `update_client`
- **Anonymous Users**: `create_anonymous_user`, `get_anonymous_user`
- **Authenticated Users**: `create_authenticated_user`, `get_authenticated_user`
- **Threads**: `create_thread`, `get_thread`
- **Messages**: `create_message`, `get_message`, `get_thread_messages`
- **Feedback**: `add_feedback`, `get_feedback`
- **LLM Chat**: `chat_with_llm`
- **Subscriptions**: `create_subscription`, `update_subscription`, `cancel_subscription`

---

## Testing

1. Create a `tests/` folder (if it doesn't exist) and add your test files (e.g., `test_client.py`).
2. Run tests with:
   ```bash
   poetry run pytest
   ```
3. Use mocks or a dedicated test environment to avoid modifying production data during tests.

---

## Contributing

1. **Fork** this repository.
2. Create a **feature branch** for your changes.
3. Submit a **Pull Request**.

---

## License

This project is provided under the [MIT License](./LICENSE). 