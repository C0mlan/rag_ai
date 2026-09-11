import logging
import filetype
from apps.common.constants.allowed_types import FileType
from apps.common.apiexceptions.docsexceptions import (
    InvalidFileType, 
    FileTypeDetectionFailed, 
    FileTooLarge, 
    FileExtensionMissing, 
    FileTypeNotAllowed,
    IdempotencyKeyRequired, 
    FileRequired)

logger = logging.getLogger(__name__)

# MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_FILE_SIZE = 25 * 1000 * 1000  

class FileValidator:
    @staticmethod
    def validate_file_upload(file=None, idem_key=None) -> None:
        if file is None:
            raise FileRequired()
        if idem_key is None:
            raise FileRequired()
        FileValidator._validate_size(file)
        detected = FileValidator._detect_type(file)
        FileValidator._validate_type_allowed(file, detected)
        return detected


    @staticmethod
    def _validate_size(file) -> None:
        if file.size > MAX_FILE_SIZE:
            raise FileTooLarge(
                detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024:.1f} MB)."
            )
    @staticmethod
    def _detect_type(file) -> filetype.Type:
        chunk = file.read(2048)
        file.seek(0)
        detected = filetype.guess(chunk)
        if detected is None: 
            raise FileTypeNotAllowed()
        return detected

    @staticmethod
    def _validate_type_allowed(file, detected: filetype.Type) -> None:
        if detected.mime not in FileType.ALLOWED_TYPES: 
            raise FileTypeNotAllowed(
                detail=f"File type '{detected.mime}' is not allowed."
            )