from abc import ABC, abstractmethod


class BillingService(ABC):
    @abstractmethod
    async def create_customer(self, user_id: str, email: str) -> str:
        """Create a billing customer record. Returns the customer ID."""
        ...

    @abstractmethod
    async def deduct_credits(self, user_id: str, amount: int, description: str) -> bool:
        """Deduct credits from the user's balance. Returns True on success."""
        ...

    @abstractmethod
    async def check_credits(self, user_id: str, required: int) -> bool:
        """Check if the user has at least `required` credits. Returns True if sufficient."""
        ...

    @abstractmethod
    async def get_usage(self, user_id: str) -> dict:
        """Return current usage summary for the user."""
        ...
