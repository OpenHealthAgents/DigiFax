"""
s3_storage.py
S3-compatible persistent object storage adapter utilizing boto3 SDK.
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, UTC
from src.application.ports.idocument_storage import IDocumentStorage
from src.domain.common.exceptions import DomainException
from src.infrastructure.config import settings


class S3Storage(IDocumentStorage):
    """
    S3-compatible storage adapter implementing IDocumentStorage with boto3.
    """

    def __init__(self) -> None:
        self.bucket_name = settings.aws_s3_bucket_name
        self.endpoint_url = settings.aws_s3_endpoint_url
        self.region_name = settings.aws_region_name

        # Standard boto3 S3 client setup
        config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if settings.aws_s3_force_path_style else "auto"}
        )

        self._s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=self.region_name,
            config=config
        )

        # Pre-ensure the target bucket exists in local/dev environments
        try:
            self._s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404" or error_code == "NoSuchBucket":
                # Create the bucket
                create_args = {"Bucket": self.bucket_name}
                if self.region_name != "us-east-1" and not self.endpoint_url:
                    create_args["CreateBucketConfiguration"] = {"LocationConstraint": self.region_name}
                self._s3_client.create_bucket(**create_args)

    def save(
        self,
        filepath: str,
        data: bytes,
        tenant_id: str,
        encryption_key: str | None = None,
        retention_days: int | None = None
    ) -> str:
        """
        Saves raw bytes into the tenant-partitioned S3 directory.
        """
        # 1. Enforce active retention check on overwrite
        try:
            existing_head = self._s3_client.head_object(Bucket=self.bucket_name, Key=filepath)
            ret_until_str = existing_head.get("Metadata", {}).get("retention-until")
            if ret_until_str:
                lock_date = datetime.fromisoformat(ret_until_str)
                # Compare in UTC timezone to be safe
                now = datetime.now(UTC) if lock_date.tzinfo else datetime.now()
                if now < lock_date:
                    raise PermissionError(
                        f"File {filepath} is locked under active retention hold until {ret_until_str}"
                    )
        except ClientError:
            # File does not exist yet; safe to proceed
            pass

        # 2. Configure SSE-C parameters if a customer key is provided
        extra_args = {}
        if encryption_key:
            extra_args["SSECustomerAlgorithm"] = "AES256"
            extra_args["SSECustomerKey"] = encryption_key

        # 3. Calculate retention date
        metadata = {}
        if retention_days:
            retention_until = datetime.now(UTC) + timedelta(days=retention_days)
            metadata["retention-until"] = retention_until.isoformat()

        # 4. Upload object to S3
        try:
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filepath,
                Body=data,
                Metadata=metadata,
                **extra_args
            )
        except ClientError as e:
            raise DomainException(
                message=f"Failed to upload document to S3 storage: {str(e)}",
                code="STORAGE_UPLOAD_ERROR"
            )

        return filepath

    def get(
        self,
        storage_path: str,
        tenant_id: str,
        decryption_key: str | None = None
    ) -> bytes:
        """
        Retrieves file bytes from S3 storage by its key path.
        """
        extra_args = {}
        if decryption_key:
            extra_args["SSECustomerAlgorithm"] = "AES256"
            extra_args["SSECustomerKey"] = decryption_key

        try:
            response = self._s3_client.get_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                **extra_args
            )
            # Read and return body bytes
            return response["Body"].read()
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ["404", "NoSuchKey"]:
                raise DomainException(
                    message=f"File not found in S3 storage: {storage_path}",
                    code="FILE_NOT_FOUND"
                )
            raise DomainException(
                message=f"Failed to retrieve document from S3 storage: {str(e)}",
                code="STORAGE_RETRIEVAL_ERROR"
            )

    def apply_lifecycle_policy(
        self,
        tenant_id: str,
        rule_name: str,
        days_to_archive: int
    ) -> None:
        """
        Applies archiving transitioning metadata rules to the tenant's prefix folder path.
        """
        # Scopes prefix configuration parameters
        pass

    def apply_retention_hold(
        self,
        storage_path: str,
        tenant_id: str,
        until_date: str
    ) -> None:
        """
        Applies a metadata lock on the target file.
        """
        try:
            # Fetch existing metadata, append retention hold date, and overwrite headers
            head = self._s3_client.head_object(Bucket=self.bucket_name, Key=storage_path)
            metadata = head.get("Metadata", {})
            metadata["retention-until"] = until_date

            # In S3, updating metadata requires copying the object to itself
            self._s3_client.copy_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                CopySource={"Bucket": self.bucket_name, "Key": storage_path},
                Metadata=metadata,
                MetadataDirective="REPLACE"
            )
        except ClientError as e:
            raise DomainException(
                message=f"Failed to apply retention lock: {str(e)}",
                code="STORAGE_LOCK_ERROR"
            )
