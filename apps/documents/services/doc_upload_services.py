from django.conf import settings
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from apps.documents.repositories.doc_upload_repositories import DocumentUploadRepository
from typing import Optional
from django.db import transaction
from apps.documents.tasks import upload_to_s3_async
import uuid
import logging

logger = logging.getLogger(__name__)


class DocumentUploadService:
    @staticmethod
    @transaction.atomic    
    def ingest_document(*, file,  idem_key: uuid.UUID, content_type: Optional[str] = None):
        """Ingest an uploaded document and schedule asynchronous S3 upload.

        Args:
            file: Django UploadedFile instance containing the document bytes.
            idem_key: UUID used as an idempotency key to prevent duplicate uploads.
            content_type: Optional MIME type string for the uploaded file.

        Returns:
            Document: Existing or newly created DocumentUploadRepository model instance.
        """
        document = DocumentUploadRepository.find_existing_upload(idem_key=idem_key,doc_name=file.name)
        if document:
            logger.info("Existing document found for idempotency key",
            extra={
                "document_id": str(document.id),"idempotency_key": str(idem_key),"document_filename": file.name,},)
            return document

        document = DocumentUploadRepository.create_document_upload(
            idem_key=idem_key,doc_name=file.name,content_type=content_type,file_size=file.size)
        logger.info("Document upload record created",
        extra={
            "document_id": str(document.id),
            "document_filename": document.original_filename,
            "file_size": document.file_size,
            "content_type": document.content_type,},)

        file_content = file.read()    
        transaction.on_commit(
            lambda: upload_to_s3_async.delay(
                document_id=str(document.id),
                doc_name=file.name,
                file_content=file_content,
                content_type=document.content_type,   
                )
            )
        return document

