# apps/documents/services/s3_service.py
import logging
from django.conf import settings
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from urllib3.exceptions import MaxRetryError
from requests.exceptions import RetryError
from apps.documents.repositories.doc_upload_repositories import DocumentUploadRepository
from typing import Optional


logger = logging.getLogger(__name__)


class S3Service:
    BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
    REGION_NAME = settings.AWS_S3_REGION_NAME

    @staticmethod
    def get_client():
        config = Config(
            retries={
                "mode": "standard",  # or "adaptive"
                "max_attempts": 5,   # 1 initial + up to 4 retries
            },
            connect_timeout=5,
            read_timeout=60,
        )

        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=S3Service.REGION_NAME,
            config=config,
        )

    @staticmethod
    def upload_to_s3(file, key: str, content_type: Optional[str], document_id) -> str:
         """Upload a file-like object to S3 and return its public URL.

        Args:
            file: File-like object (opened in binary mode) to upload.
            key: S3 object key (path) for the uploaded file.
            content_type: Optional MIME type string for the uploaded file.
            document_id: Identifier of the document record for error handling.

        Returns:
            str: Public HTTPS URL of the uploaded S3 object.

        Raises:
            NoCredentialsError: If AWS credentials are missing or misconfigured.
            MaxRetryError: If network retries are exhausted during upload.
            RetryError: If request-level retries are exhausted.
            ClientError: For other S3 client-side errors (e.g., access denied,
                invalid bucket). Non-retryable errors mark the document as failed.
        """
        
        client = S3Service.get_client()

        extra_args = {"ContentType": content_type} if content_type else {}

        try:
            client.upload_fileobj(file, S3Service.BUCKET_NAME, key, ExtraArgs=extra_args)

            file_url = f"https://{S3Service.BUCKET_NAME}.s3.{S3Service.REGION_NAME}.amazonaws.com/{key}"
            return file_url

        except NoCredentialsError:
            DocumentUploadRepository.mark_as_failed(document_id)
            logger.error(
                "AWS credentials not configured",
                extra={"bucket": S3Service.BUCKET_NAME, "key": key},
            )
            raise

        except (MaxRetryError, RetryError) as e:
            # Retries exhausted
            DocumentUploadRepository.mark_as_failed(document_id)
            logger.error(
                f"S3 upload failed after retries: {e}",
                extra={
                    "bucket": S3Service.BUCKET_NAME,
                    "key": key,
                    "error_type": type(e).__name__,
                },
            )
            raise

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")

            non_retryable_codes = {
                "AccessDenied",
                "InvalidAccessKeyId",
                "SignatureDoesNotMatch",
                "InvalidBucketName",
                "NoSuchBucket",
            }

            if error_code in non_retryable_codes:
                DocumentUploadRepository.mark_as_failed(document_id)
                logger.error(
                    f"S3 upload failed (non-retryable): {error_code} – {error_message}",
                    extra={
                        "bucket": S3Service.BUCKET_NAME,
                        "key": key,
                        "error_code": error_code,
                        "error_message": error_message,
                    },
                )
                raise

            DocumentUploadRepository.mark_as_failed(document_id)
            logger.error(
                f"S3 upload failed: {error_code} – {error_message}",
                extra={
                    "bucket": S3Service.BUCKET_NAME,
                    "key": key,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )
            raise