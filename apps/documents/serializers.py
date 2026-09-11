from rest_framework import serializers
from apps.common.validators.file_validators import FileValidator
from apps.common.apiexceptions.docsexceptions import (IdempotencyKeyRequired, FileRequired)


class DocumentUploadSerializer(serializers.Serializer):

    """Serializer for document upload requests.

    Validates uploaded file and idempotency key, then enriches validated data
    with the detected MIME type.

    Attributes:
        file:  uploaded file field.
        idem_key:  UUID for idempotent request handling.

    Raises:
        IdempotencyKeyRequired: When idem_key is missing.
        FileRequired: When file is missing.
    """
    file = serializers.FileField(required=False)
    idem_key = serializers.UUIDField(required=False)

    def validate(self, data):
        content_type = FileValidator.validate_file_upload(data.get("file"), data.get("idem_key"))
        data["content_type"] = content_type.mime
        return data




       
