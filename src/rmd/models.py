from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

class MigrationStatus(str, Enum):
    PENDING = "PENDING"
    SOURCE_PLACEHOLDER = "SOURCE_PLACEHOLDER"
    SOURCE_DOWNLOADING = "SOURCE_DOWNLOADING"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PRECHECK_FAILED = "PRECHECK_FAILED"
    TRANSFERRING = "TRANSFERRING"
    UPLOAD_PAUSED_RATE_LIMIT = "UPLOAD_PAUSED_RATE_LIMIT"
    UPLOAD_PAUSED_QUOTA = "UPLOAD_PAUSED_QUOTA"
    UPLOADED_UNVERIFIED = "UPLOADED_UNVERIFIED"
    VERIFIED_MATCH = "VERIFIED_MATCH"
    VERIFIED_WEAK = "VERIFIED_WEAK"
    VERIFIED_SIZE_MISMATCH = "VERIFIED_SIZE_MISMATCH"
    VERIFIED_HASH_MISMATCH = "VERIFIED_HASH_MISMATCH"
    CONFLICT_TARGET_EXISTS = "CONFLICT_TARGET_EXISTS"
    SKIPPED_ALREADY_EXISTS = "SKIPPED_ALREADY_EXISTS"
    SKIPPED_BY_USER = "SKIPPED_BY_USER"
    FAILED_PERMISSION = "FAILED_PERMISSION"
    FAILED_SOURCE_READ = "FAILED_SOURCE_READ"
    FAILED_UPLOAD = "FAILED_UPLOAD"
    FAILED_TARGET_VERIFY = "FAILED_TARGET_VERIFY"
    FAILED_UNKNOWN = "FAILED_UNKNOWN"

@dataclass
class PlatformCapabilities:
    os: str
    icloud_drive_available: bool
    icloud_photos_available: bool
    photos_mode: str
    drive_mode: str
    limitations: List[str]

@dataclass
class TransferItem:
    task_id: str
    record_id: str
    source_type: str
    source_display_name: str
    resource_kind: str
    source_size: int
    source_stable_id: Optional[str] = None
    source_path: Optional[str] = None
    resource_group_id: Optional[str] = None
    source_mtime: Optional[str] = None
    mime_type: Optional[str] = None

@dataclass
class DriveUploadSession:
    record_id: str
    upload_session_uri: str
    target_parent_folder_id: str
    confirmed_offset: int
    session_created_at: str
    last_checked_at: str
    target_drive_file_id: Optional[str] = None
    expires_at_estimate: Optional[str] = None

@dataclass
class ManifestRecord:
    task_id: str
    record_id: str
    source_type: str
    source_display_name: str
    source_size: int
    resource_kind: str
    status: MigrationStatus
    record_hash: str
    source_stable_id: Optional[str] = None
    source_path: Optional[str] = None
    source_mtime: Optional[str] = None
    source_md5: Optional[str] = None
    source_sha256: Optional[str] = None
    resource_group_id: Optional[str] = None
    package_original_file_count: int = 0
    package_original_total_size: int = 0
    target_drive_file_id: Optional[str] = None
    target_parent_folder_id: Optional[str] = None
    target_path: Optional[str] = None
    target_size: int = 0
    target_md5: Optional[str] = None
    target_sha1: Optional[str] = None
    target_sha256: Optional[str] = None
    target_head_revision_id: Optional[str] = None
    target_web_view_link: Optional[str] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    started_at: Optional[str] = None
    uploaded_at: Optional[str] = None
    verified_at: Optional[str] = None
