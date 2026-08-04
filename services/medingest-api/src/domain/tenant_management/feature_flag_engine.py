"""
feature_flag_engine.py
Domain service executing the multi-tenant feature flag evaluation strategy.
"""

from src.domain.organizations.value_objects import TenantConfiguration


class FeatureFlagEngine:
    """
    Evaluates clinical features availability, beta access gates, license tiers, and usage caps.

    Purpose:
        Enforce operational SaaS rules programmatically.
    Business Reasoning:
        Secures system compute resource availability and controls access permissions dynamically.
    """

    def evaluate_feature(
        self,
        feature_name: str,
        config: TenantConfiguration,
        license_tier: str = "Standard",
        usage_count: int = 0
    ) -> bool:
        """
        Evaluates availability of a feature based on configurations, betas, license, and usage.

        Inputs:
            feature_name (str): Identifier of the feature gate.
            config (TenantConfiguration): Target tenant configs holding flags and caps.
            license_tier (str): Associated subscription level (e.g. Standard, Enterprise).
            usage_count (int): Dynamic usage counters (e.g. daily uploaded files).
        Outputs:
            bool: True if available and compliant, else False.
        """
        # 1. Enforce Explicit Boolean Override Check
        explicit_toggle = config.feature_flags.get(feature_name)
        if explicit_toggle is False:
            return False

        # 2. Enforce Beta Opt-In Gate
        # Designated beta features require the tenant to be in the opt-in listing
        beta_features = ["ai_summarization", "clinical_insights"]
        if feature_name in beta_features:
            opted_in = config.feature_flags.get("beta_opt_in", [])
            if feature_name not in opted_in:
                return False

        # 3. Enforce License Restrictions Gate
        # Premium/computational features are restricted by tier levels
        enterprise_features = ["billing_write", "advanced_analytics"]
        if feature_name in enterprise_features and license_tier != "Enterprise":
            return False

        # 4. Enforce Usage Limits Gate
        # Daily uploads must not breach max daily capacity configurations
        if feature_name == "document_upload":
            if usage_count >= config.max_daily_uploads:
                return False

        # Default fallback: return flag override value or True if not disabled
        return config.feature_flags.get(feature_name, True)
