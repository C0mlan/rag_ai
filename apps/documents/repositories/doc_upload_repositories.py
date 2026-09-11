from apps.documents.models import Document
from apps.common.constants.doc_status import DocStatus

class DocumentUploadRepository:
    @staticmethod
    def find_existing_upload(idem_key, doc_name):
        return Document.objects.select_for_update().filter(
            idempotency_key=idem_key,original_filename=doc_name).first()
    @staticmethod
    def create_document_upload(*, idem_key,doc_name,content_type, file_size):
        return Document.objects.create(
            idempotency_key=idem_key,
            original_filename=doc_name,
            content_type=content_type,
            file_size = file_size,
        )
    @staticmethod
    def set_document_file_url(document_id:str,  file_url: str) -> None:
        document = Document.objects.get(id=document_id)
        document.file_url = file_url
        document.save()
    
    @staticmethod
    def mark_as_failed(document_id: str) -> None:
        document = Document.objects.get(id=document_id)
        document.status = DocStatus.FAILED
        document.save()

   