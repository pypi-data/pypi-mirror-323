class Subscriptions:
    def __init__(self, request_handler):
        self.request_handler = request_handler

    def create(self, client_id: str, price_id: str, plan: str) -> dict:
        """
        Create a subscription.
        """
        payload = {"price_id": price_id, "plan": plan}
        return self.request_handler.post(f"/clients/{client_id}/subscriptions", payload)

    def update(self, subscription_id: str, new_price_id: str, new_plan: str) -> dict:
        """
        Update a subscription.
        """
        payload = {"new_price_id": new_price_id, "new_plan": new_plan}
        return self.request_handler.put(f"/subscriptions/{subscription_id}", payload)

    def cancel(self, subscription_id: str) -> dict:
        """
        Cancel a subscription.
        """
        return self.request_handler.delete(f"/subscriptions/{subscription_id}")
