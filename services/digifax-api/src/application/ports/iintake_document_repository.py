"""
iintake_document_repository.py
Outbound port interface for managing IntakeDocument aggregate persistence with tenant-scoping.
"""

import abc

from src.domain.intake.entities import IntakeDocument


class IIntakeDocumentRepository(abc.ABC):
    """
    Outbound port interface for persisting Ingested Document Aggregate state.

    Why It Exists:
        Abstracts storage technologies (S3, local, Postgres) from application layers.
        Enforces tenant partitioning constraints on all database queries.
    """

    @abc.abstractmethod
    def save(self, document: IntakeDocument) -> None:
        """
        Saves or updates the IntakeDocument aggregate.

        Purpose:
            Persist document index metadata.
        Business Reasoning:
            Clinical documents must be saved securely under verified ownership records.
        Inputs:
            document (IntakeDocument): Intake document aggregate.
        Outputs:
            None.
        Assumptions:
            Target database is active and reachable.
        Edge Cases:
            None.
        """
        pass

    @abc.abstractmethod
    def get_by_id(self, id: str, tenant_id: str) -> IntakeDocument | None:
        """
        Retrieves an IntakeDocument aggregate by its unique ID, validated against the owner tenant ID.

        Purpose:
            Verify and load an intake document safely.
        Business Reasoning:
            Passing the requesting tenant's ID is mandatory to block cross-tenant leaks.
        Inputs:
            id (str): Document ID.
            tenant_id (str): Associated owner tenant ID.
        Outputs:
            IntakeDocument | None: The matched aggregate, or None if missing or unauthorized.
        Assumptions:
            None.
        Edge Cases:
            Querying with a valid document ID but matching a different tenant ID returns None to prevent leakage.
        """
        pass
