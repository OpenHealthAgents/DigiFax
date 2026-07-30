"""
domain_services.py
Validation pipeline verifying FHIR resource conformity against StructureDefinitions constraints.
"""

from typing import Any
from src.domain.fhir_profile.value_objects import FHIRValidationResult
from src.domain.fhir_profile.entities import FHIRStructureDefinition


class FHIRProfileValidationPipeline:
    """
    Domain service evaluating FHIR resource conformity against active Profile and
    StructureDefinition constraints.
    """

    def validate_resource(
        self,
        tenant_id: str,
        resource: dict[str, Any],
        active_igs: list[str],
        structure_definitions: list[FHIRStructureDefinition]
    ) -> FHIRValidationResult:
        """
        Validates a FHIR resource dictionary against matching structure definitions.
        
        Rules:
            1. Scans resource metadata profile URLs.
            2. Ensures profile IG matches active tenant IGs list.
            3. Verifies required schema paths exist.
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            return FHIRValidationResult(valid=False, errors=["Missing resourceType field"], profile_url=None)

        # Get declared profiles
        meta = resource.get("meta", {})
        profiles = meta.get("profile", [])

        if not profiles:
            # Fallback to search matching default profile for this resourceType among active IGs
            matching_sds = [
                sd for sd in structure_definitions 
                if sd.resource_type == resource_type
            ]
            if not matching_sds:
                # No profiles to validate against, valid by default structural base
                return FHIRValidationResult(valid=True, errors=[], profile_url=None)
            
            # Use the first matching default
            sd_to_use = matching_sds[0]
        else:
            profile_url = profiles[0]
            # Find matching StructureDefinition
            matching_sds = [sd for sd in structure_definitions if sd.url == profile_url]
            if not matching_sds:
                return FHIRValidationResult(
                    valid=False, 
                    errors=[f"StructureDefinition profile not found for URL: {profile_url}"],
                    profile_url=profile_url
                )
            sd_to_use = matching_sds[0]

        # Check if the profile's corresponding implementation guide is active (if it is a standard profile)
        # We can verify that standard URLs match active guides (e.g. US Core, IPS)
        is_standard_ig = "hl7.org/fhir" in sd_to_use.url
        if is_standard_ig:
            # Find if any active IG matches a prefix of the URL
            is_active = False
            for ig_url in active_igs:
                if ig_url in sd_to_use.url:
                    is_active = True
                    break
            
            if not is_active and active_igs: # If tenant has active IGs configured, enforce selection
                return FHIRValidationResult(
                    valid=False,
                    errors=[f"Implementation Guide containing profile {sd_to_use.url} is not active for this tenant."],
                    profile_url=sd_to_use.url
                )

        # Validate required paths
        errors = []
        for path in sd_to_use.required_paths:
            if not self._check_path_exists(resource, path):
                errors.append(f"Required element missing: {path}")

        return FHIRValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            profile_url=sd_to_use.url
        )

    def _check_path_exists(self, data: Any, path: str) -> bool:
        """Helper checking if nested dictionary path matches non-empty elements."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                if part not in current or current[part] is None:
                    return False
                current = current[part]
            elif isinstance(current, list):
                # Check if at least one item contains the remaining path elements
                # For lists, evaluate sub-path against all items
                remaining_path = ".".join(parts[parts.index(part):])
                return any(self._check_path_exists(item, remaining_path) for item in current)
            else:
                return False
        
        # Ensure values aren't empty whitespace or empty lists
        if isinstance(current, str) and not current.strip():
            return False
        if isinstance(current, list) and len(current) == 0:
            return False
        return True
