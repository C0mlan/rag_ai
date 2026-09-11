class FileType:
    PDF = "application/pdf"
    DOCX = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    )

    ALLOWED_TYPES = {
        PDF,
        DOCX,
    }