"""
ibilling_service.py
Outbound port abstraction interface decoupling the application from specific payment processors.
"""

import abc
from src.domain.tenant_management.value_objects import SubscriptionTier


class IBillingService(abc.ABC):
    """
    Outbound port interface for payment/billing system integrations (e.g. Stripe, Recurly).

    Purpose:
        Decouple payment processor infrastructure from domain use cases.
    Business Reasoning:
        Allows exchanging payment services in the future without modifying core subscription logic.
    """

    @abc.abstractmethod
    def create_billing_account(self, tenant_id: str, email: str) -> str:
        """
        Creates a customer billing account in the external processor database.

        Inputs:
            tenant_id (str): Associated tenant context UUID.
            email (str): Billing notification address.
        Outputs:
            str: Resolved external customer account reference ID.
        """
        pass

    @abc.abstractmethod
    def update_subscription_tier(self, tenant_id: str, tier: SubscriptionTier) -> None:
        """
        Updates the active subscription billing tier.

        Inputs:
            tenant_id (str): Associated tenant UUID.
            tier (SubscriptionTier): Target tier level to bind.
        """
        pass

    @abc.abstractmethod
    def report_metered_usage(self, tenant_id: str, usage_type: str, quantity: int) -> None:
        """
        Reports dynamic usage consumption parameters to the external processor ledger.

        Inputs:
            tenant_id (str): Associated tenant UUID.
            usage_type (str): Key identifying the usage bucket (e.g., ocr_pages, api_requests).
            quantity (int): Number of items consumed.
        """
        pass

    @abc.abstractmethod
    def cancel_subscription(self, tenant_id: str) -> None:
        """
        Cancels the active subscription.

        Inputs:
            tenant_id (str): Target tenant.
        """
        pass
