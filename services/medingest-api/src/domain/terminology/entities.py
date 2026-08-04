"""
entities.py
Domain Entities and Aggregate Roots for Concept Mappings and ValueSet overrides.
"""

from src.domain.common.entity import Entity
from src.domain.terminology.value_objects import ConceptMapRule


class TenantConceptMap(Entity):
    """
    Aggregate Root managing a tenant's local-to-standard terminology mappings.
    
    Includes approval workflows, version logs, and rollback logic.
    """

    def __init__(
        self,
        tenant_id: str,
        mapping_key: str,
        rules: list[ConceptMapRule] = None,
        version: int = 1,
        history: list[dict] = None
    ):
        super().__init__(id=f"{tenant_id}:{mapping_key}")
        self.tenant_id = tenant_id
        self.mapping_key = mapping_key
        self.rules = rules or []
        self.version = version
        self.history = history or []

        # Initial history copy if empty
        if not self.history:
            self._save_to_history("Initial map state")

    def propose_rule(
        self,
        source_system: str,
        source_code: str,
        target_system: str,
        target_code: str,
        preferred_display: str | None = None
    ) -> None:
        """Proposes a new mapping (default status is PENDING_APPROVAL)."""
        # Remove any existing rules matching the source to avoid duplicates
        self.rules = [
            r for r in self.rules
            if not (r.source_system == source_system and r.source_code == source_code)
        ]

        new_rule = ConceptMapRule(
            source_system=source_system,
            source_code=source_code,
            target_system=target_system,
            target_code=target_code,
            status="PENDING_APPROVAL",
            preferred_display=preferred_display
        )
        self.rules.append(new_rule)
        
        self.version += 1
        self._save_to_history(f"Proposed mapping for local code {source_code}")

    def approve_rule(
        self,
        source_system: str,
        source_code: str,
        target_system: str,
        target_code: str
    ) -> None:
        """Approves a proposed mapping rule."""
        found = False
        new_rules = []
        for r in self.rules:
            if (r.source_system == source_system and r.source_code == source_code
                    and r.target_system == target_system and r.target_code == target_code):
                # Map to approved
                new_rules.append(
                    ConceptMapRule(
                        source_system=r.source_system,
                        source_code=r.source_code,
                        target_system=r.target_system,
                        target_code=r.target_code,
                        status="APPROVED",
                        preferred_display=r.preferred_display
                    )
                )
                found = True
            else:
                new_rules.append(r)

        if not found:
            raise ValueError("Target mapping rule not found")

        self.rules = new_rules
        self.version += 1
        self._save_to_history(f"Approved mapping for local code {source_code}")

    def rollback_to_version(self, target_version: int) -> None:
        """Restores mapping rules list back to target version index."""
        target_state = None
        for hist in self.history:
            if hist["version"] == target_version:
                target_state = hist
                break

        if not target_state:
            raise ValueError(f"Version {target_version} not found in history logs")

        # Parse rules list back
        reconstituted = []
        for r in target_state["rules"]:
            reconstituted.append(
                ConceptMapRule(
                    source_system=r["source_system"],
                    source_code=r["source_code"],
                    target_system=r["target_system"],
                    target_code=r["target_code"],
                    status=r["status"],
                    preferred_display=r["preferred_display"]
                )
            )

        self.rules = reconstituted
        self.version = target_version
        
        # Trim history list to match rollback point
        self.history = [h for h in self.history if h["version"] <= target_version]
        self._save_to_history(f"Rolled back to version {target_version}")

    def _save_to_history(self, comment: str) -> None:
        """Caches active state layout copies."""
        rules_copy = [
            {
                "source_system": r.source_system,
                "source_code": r.source_code,
                "target_system": r.target_system,
                "target_code": r.target_code,
                "status": r.status,
                "preferred_display": r.preferred_display
            } for r in self.rules
        ]
        self.history.append({
            "version": self.version,
            "rules": rules_copy,
            "comment": comment
        })


class TenantValueSetOverride(Entity):
    """
    Aggregate Root allowing a tenant to override standard terminology codes display names.
    """

    def __init__(self, tenant_id: str, system_url: str, overrides: dict[str, str] = None):
        super().__init__(id=f"{tenant_id}:{system_url}")
        self.tenant_id = tenant_id
        self.system_url = system_url
        self.overrides = overrides or {}

    def set_override(self, code: str, custom_display: str) -> None:
        """Sets custom description overrides for standard code."""
        self.overrides[code] = custom_display
