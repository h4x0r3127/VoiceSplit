from app.services.billing.base import BillingService
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class StripeStubService(BillingService):
    """
    Permissive billing stub that logs all operations.
    When BILLING_ENABLED=True, raises NotImplementedError until real Stripe logic is wired.
    """

    def _assert_billing_disabled(self) -> None:
        if settings.BILLING_ENABLED:
            raise NotImplementedError(
                "Enable Stripe by implementing StripeService with the stripe SDK. "
                "Set BILLING_ENABLED=False to use the stub."
            )

    async def create_customer(self, user_id: str, email: str) -> str:
        self._assert_billing_disabled()
        customer_id = f"cus_stub_{user_id[:8]}"
        logger.info(
            "billing_create_customer_stub",
            user_id=user_id,
            email=email,
            customer_id=customer_id,
        )
        return customer_id

    async def deduct_credits(self, user_id: str, amount: int, description: str) -> bool:
        self._assert_billing_disabled()
        logger.info(
            "billing_deduct_credits_stub",
            user_id=user_id,
            amount=amount,
            description=description,
        )
        return True

    async def check_credits(self, user_id: str, required: int) -> bool:
        self._assert_billing_disabled()
        logger.info(
            "billing_check_credits_stub",
            user_id=user_id,
            required=required,
        )
        return True

    async def get_usage(self, user_id: str) -> dict:
        self._assert_billing_disabled()
        logger.info("billing_get_usage_stub", user_id=user_id)
        return {
            "user_id": user_id,
            "credits_used": 0,
            "credits_remaining": 300,
            "billing_enabled": False,
        }
