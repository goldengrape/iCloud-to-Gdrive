import io
import uuid
import time
from typing import Optional, Dict
from dataclasses import dataclass
from .models import TransferItem, MigrationStatus
from .verification import DriveFileMetadata
from .adapters import TargetAdapter, DriveUploadResult
from .auth import GoogleAuthManager
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

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
                return DriveUploadResult(is_completed=False, session_uri=session_uri)

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
        
        if len(full_data) != item.source_size:
            return DriveUploadResult(error="FAILED_SOURCE_READ")
            
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

class RealGoogleDriveAdapter(TargetAdapter):
    CHUNK_SIZE = 5 * 1024 * 1024 # 5MB

    def __init__(self, auth_manager: GoogleAuthManager, folder_name: str = "iCloud-to-Gdrive-Migration"):
        self.auth_manager = auth_manager
        self.folder_name = folder_name
        self._service = None
        self._folder_id = None

    def _get_service(self):
        if not self._service:
            creds = self.auth_manager.get_credentials()
            if not creds or not creds.valid:
                # 尝试刷新或登录
                self.auth_manager.login()
                creds = self.auth_manager.get_credentials()
                
            if not creds or not creds.valid:
                raise DriveError("Valid credentials could not be obtained.")
            
            self._service = build('drive', 'v3', credentials=creds)
        return self._service

    def _get_or_create_target_folder(self) -> str:
        if self._folder_id:
            return self._folder_id
            
        service = self._get_service()
        # 查找目标文件夹
        query = f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        
        files = response.get('files', [])
        if not files:
            # 创建文件夹
            file_metadata = {
                'name': self.folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            self._folder_id = folder.get('id')
        else:
            self._folder_id = files[0].get('id')
            
        return self._folder_id

    def _map_http_error(self, error: HttpError) -> str:
        status_code = error.status_code
        if status_code in (403, 429):
            reason = error.reason if hasattr(error, 'reason') else str(error)
            if 'quota' in reason.lower() or 'storage' in reason.lower():
                return "UPLOAD_PAUSED_QUOTA"
            return "UPLOAD_PAUSED_RATE_LIMIT"
        elif status_code == 401:
            return "FAILED_PERMISSION"
        return f"FAILED_HTTP_{status_code}"

    def upload(self, item: TransferItem, stream: io.BytesIO, **kwargs) -> DriveUploadResult:
        try:
            service = self._get_service()
            folder_id = self._get_or_create_target_folder()
            
            file_metadata = {
                'name': item.source_display_name,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                stream, 
                mimetype='application/octet-stream', 
                resumable=True, 
                chunksize=self.CHUNK_SIZE
            )
            
            request = service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id, size, md5Checksum, sha256Checksum, headRevisionId'
            )
            
            session_uri = kwargs.get('session_uri')
            if session_uri:
                # 恢复上次的 resumable URI
                request.resumable_uri = session_uri
            
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                except HttpError as e:
                    # 如果发生异常，保留 resumable_uri 以备后用
                    resumable_uri = request.resumable_uri
                    return DriveUploadResult(error=self._map_http_error(e), is_completed=False, session_uri=resumable_uri)
            
            # 上传成功
            metadata = DriveFileMetadata(
                size=int(response.get('size', 0)),
                md5Checksum=response.get('md5Checksum'),
                sha256Checksum=response.get('sha256Checksum'),
                headRevisionId=response.get('headRevisionId')
            )
            
            return DriveUploadResult(
                target_drive_file_id=response.get('id'),
                confirmed_offset=metadata.size,
                metadata=metadata,
                is_completed=True
            )
            
        except HttpError as e:
            return DriveUploadResult(error=self._map_http_error(e))
        except Exception as e:
            return DriveUploadResult(error=f"UPLOAD_FAILED_{type(e).__name__}")
