import io
import uuid
import time
from typing import Optional, Dict
from dataclasses import dataclass
from .models import TransferItem, MigrationStatus
from .verification import DriveFileMetadata
from .adapters import TargetAdapter, DriveUploadResult

class DriveError(Exception):
    def __init__(self, message: str, status_code: int = 500, reason: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason

class MockGoogleDriveAdapter(TargetAdapter):
    RESUMABLE_THRESHOLD = 5 * 1024 * 1024  # 5MB

    def __init__(self, auth_manager=None):
        self.auth_manager = auth_manager
        self.mock_sessions = {} # session_uri -> offset
        self.fail_next_upload_with = None

    def upload(self, item: TransferItem, stream: io.BytesIO, **kwargs) -> DriveUploadResult:
        if self.fail_next_upload_with:
            error = self.fail_next_upload_with
            self.fail_next_upload_with = None
            if error == "RATE_LIMIT":
                return DriveUploadResult(error="UPLOAD_PAUSED_RATE_LIMIT")
            elif error == "QUOTA":
                return DriveUploadResult(error="UPLOAD_PAUSED_QUOTA")
            elif error == "FORBIDDEN":
                return DriveUploadResult(error="FAILED_PERMISSION")
            raise DriveError("Mocked failure", status_code=500)

        session_uri = kwargs.get('session_uri')
        if item.source_size > self.RESUMABLE_THRESHOLD:
            if not session_uri:
                session_uri = f"https://mock.upload.drive/{uuid.uuid4()}"
                self.mock_sessions[session_uri] = 0
                return DriveUploadResult(is_completed=False, error=session_uri) # Use error field to return session URI for now

            offset = self.mock_sessions.get(session_uri, 0)
            stream.seek(offset)
            data = stream.read()
            self.mock_sessions[session_uri] += len(data)

            if self.mock_sessions[session_uri] < item.source_size:
                return DriveUploadResult(confirmed_offset=self.mock_sessions[session_uri], is_completed=False)

        else:
            data = stream.read()

        # Complete
        import hashlib
        stream.seek(0)
        full_data = stream.read()
        md5Checksum = hashlib.md5(full_data).hexdigest()
        sha256Checksum = hashlib.sha256(full_data).hexdigest()

        metadata = DriveFileMetadata(
            size=len(full_data),
            md5Checksum=md5Checksum,
            sha256Checksum=sha256Checksum
        )

        file_id = f"drive_file_{uuid.uuid4().hex[:8]}"
        return DriveUploadResult(
            target_drive_file_id=file_id,
            confirmed_offset=len(full_data),
            metadata=metadata,
            is_completed=True
        )
