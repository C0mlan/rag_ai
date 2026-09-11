"""
Celery tasks for async session
All tasks are idempotent and retry-safe.
"""
import logging
import uuid

from celery import shared_task, Task
from django.utils import timezone
from apps.documents.repositories.doc_upload_repositories import DocumentUploadRepository
from apps.documents.services.s3_services import S3Service
from django.db import DatabaseError
# from langchain_community.document_loaders import (
#     TextLoader, 
#     PyPDFLoader,
#     Docx2txtLoader)
import tempfile
import os
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    Base task class with common retry configuration.
    """
    autoretry_for = (DatabaseError, Exception)
    retry_backoff = True
    retry_backoff_max = 300  # Cap retry delay at 5 minutes
    retry_kwargs = {"max_retries": 5}
    default_retry_delay = 10  # Start with 10 seconds


@shared_task(bind=True, base=BaseTask)
def upload_to_s3_async(self, document_id: str, doc_name: str, file_content: bytes, content_type: Optional[str])-> str:
    """Asynchronously Upload a document to S3 using a temporary file.

    Writes the in-memory file content to a temporary file, uploads it to S3,
    updates the document record with the resulting URL, and cleans up the temp
    file.

    Args:
        document_id: String UUID of the document record.
        doc_name: Original filename of the uploaded document.
        file_content: Raw bytes of the file to upload.
        content_type: Optional MIME type string for the file.

    Returns:
        str: The S3 URL of the uploaded file.

    Raises:
        Exception: Propagates any S3 or filesystem errors. Cleanup of the temp
            file is guaranteed via the finally block.
    """
    temp_path = None
        
    try:
        logger.info("Starting S3 upload",
            extra={
                "document_id": document_id,"doc_name": doc_name,"file_size": len(file_content),},)
        with tempfile.NamedTemporaryFile(suffix=f'_{doc_name}',delete=False,dir='/tmp') as tmp:
            temp_path = tmp.name
            tmp.write(file_content)
        
        logger.info(
            f"File written to temp: {temp_path}",
            extra={"document_id": document_id})
        file_size = os.path.getsize(temp_path)
        logger.info(f"Temp file size: {file_size} bytes",extra={"document_id": document_id},)

        key = f"documents/{document_id}/{doc_name}"
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        file_url = S3Service.upload_to_s3(file=open(temp_path, 'rb'),key=key,content_type=content_type,document_id = document_id)
        logger.info(f"File uploaded successfully: {file_url}")
        DocumentUploadRepository.set_document_file_url(document_id, file_url)
        return file_url
    finally:
        if temp_path and os.path.exists(temp_path):
            logger.info("Deleting temporary file",
            extra={"document_id": document_id, "temp_path": temp_path},)
            os.unlink(temp_path)
            logger.info("Temporary file deleted successfully",
            extra={"document_id": document_id, "temp_path": temp_path},)