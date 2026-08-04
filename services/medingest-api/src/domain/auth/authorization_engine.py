"""
authorization_engine.py
Domain service evaluating hierarchical Role-Based (RBAC) and resource-based (ABAC) access control.
"""

class AuthorizationEngine:
    """
    Evaluates access policies based on role inheritance trees and resource ownership attributes.

    Purpose:
        Enforce security boundaries for SaaS tenants and practitioner roles.
    Business Reasoning:
        Clinical platforms require strict access segregation to comply with HIPAA security controls.
    """

    def __init__(self) -> None:
        # Direct parent-child role inheritance mapping
        self._hierarchy: dict[str, list[str]] = {
            "PLATFORM_SUPER_ADMIN": ["TENANT_OWNER"],
            "TENANT_OWNER": ["TENANT_ADMIN"],
            "TENANT_ADMIN": ["ORGANIZATION_ADMIN"],
            "ORGANIZATION_ADMIN": ["REVIEWER", "CLINICAL_REVIEWER"],
            "CLINICAL_REVIEWER": ["REVIEWER", "UPLOADER"],
            "REVIEWER": ["CLINICIAN", "UPLOADER"],
            "CLINICIAN": ["VIEWER"],
            "UPLOADER": ["VIEWER"],
            "AUDITOR": ["VIEWER"],
            "VIEWER": []
        }

        # Direct permissions assigned to standard roles
        self._role_permissions: dict[str, list[str]] = {
            "VIEWER": ["document:read"],
            "AUDITOR": ["audit:read"],
            "UPLOADER": ["document:write"],
            "CLINICIAN": ["fhir:read"],
            "REVIEWER": ["document:verify", "loinc:map"],
            "CLINICAL_REVIEWER": ["document:verify", "loinc:map", "document:write"],
            "ORGANIZATION_ADMIN": ["workspace:manage", "user:invite"],
            "TENANT_ADMIN": ["billing:read", "settings:manage"],
            "TENANT_OWNER": ["billing:write", "apikey:manage"],
            "PLATFORM_SUPER_ADMIN": ["tenant:manage", "global:settings"]
        }

        # Custom roles registry
        self._custom_roles: dict[str, dict] = {}

    def register_custom_role(self, role_name: str, parent_roles: list[str], permissions: list[str]) -> None:
        """
        Registers a dynamic custom role.
        """
        if not role_name.strip():
            raise ValueError("Custom role name cannot be empty")
        
        self._custom_roles[role_name] = {
            "parents": parent_roles,
            "permissions": permissions
        }

    def resolve_permissions(self, role: str) -> set[str]:
        """
        Recursively resolves all direct and inherited permissions for a role.
        """
        permissions = set()

        # Handle custom roles lookup
        if role in self._custom_roles:
            permissions.update(self._custom_roles[role]["permissions"])
            for parent in self._custom_roles[role]["parents"]:
                permissions.update(self.resolve_permissions(parent))
            return permissions

        # Handle standard roles lookup
        if role in self._role_permissions:
            permissions.update(self._role_permissions[role])

        # Traverse inheritance graph recursively
        if role in self._hierarchy:
            for child in self._hierarchy[role]:
                permissions.update(self.resolve_permissions(child))

        return permissions

    def is_authorized(
        self,
        user_role: str,
        user_tenant_id: str,
        required_permission: str,
        target_tenant_id: str | None = None
    ) -> bool:
        """
        Evaluates RBAC permissions and ABAC tenant scopes.
        """
        # Phase 1: RBAC Check (Permission Existence)
        allowed_permissions = self.resolve_permissions(user_role)
        if required_permission not in allowed_permissions:
            return False

        # Phase 2: ABAC Check (Resource Scoping)
        if user_role == "PLATFORM_SUPER_ADMIN":
            return True

        if target_tenant_id and user_tenant_id != target_tenant_id:
            return False

        return True
