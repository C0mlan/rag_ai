from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = getattr(exc, "default_detail", "Request failed")

        response.data = {
            "success": False,
            "message": str(message),
            "errors": response.data,
            "status_code": response.status_code,
        }

    return response


class InvalidFileType(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "Only PDF and Word (.docx) files are allowed."
    default_code = "INVALID_FILE_TYPE"


class FileTypeDetectionFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "Unable to detect file type."
    default_code = "FILE_TYPE_DETECTION_FAILED"

class FileTooLarge(APIException):
    status_code =  status.HTTP_400_BAD_REQUEST 
    default_detail = "The uploaded file exceeds the maximum allowed size of 25 MB."
    default_code = "FILE_TOO_LARGE"
class FileExtensionMissing(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "File must have an extension."
    default_code = "FILE_EXTENSION_MISSING"
class FileExtensionNotAllowed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "The file extension is not allowed."
    default_code = "FILE_EXTENSION_NOT_ALLOWED"
class FileTypeNotAllowed(APIException):
    status_code = 400
    default_detail = "The file type is not allowed."
    default_code = "FILE_TYPE_NOT_ALLOWED"
class FileRequired(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "A file is required."
    default_code = "FILE_REQUIRED"

class IdempotencyKeyRequired(APIException):
    status_code = status.HTTP_400_BAD_REQUEST 
    default_detail = "An idempotency key is required."
    default_code = "IDEMPOTENCY_KEY_REQUIRED"
