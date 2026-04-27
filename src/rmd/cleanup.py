from typing import List, Callable, Dict, Tuple
from dataclasses import dataclass
from .models import ManifestRecord, MigrationStatus
from .verification import DriveFileMetadata

@dataclass
class CleanupCandidate:
    record_id: str
    source_path: str
    target_drive_file_id: str
    is_verified_still_exists: bool = False
    message: str = ""

class CleanupAdvisor:
    def __init__(self, target_checker: Callable[[str], DriveFileMetadata | None]):
        """
        target_checker: A function that takes target_drive_file_id and returns DriveFileMetadata
                        if it still exists in Google Drive, else None.
        """
        self.target_checker = target_checker

    def list_verified_items(self, records: List[ManifestRecord]) -> Tuple[List[CleanupCandidate], List[CleanupCandidate]]:
        # URD-REQ-020: 清理指引，复核目标文件仍存在
        # TDD-TEST-019: 禁止自动删除 (This module only reads and returns lists, no delete actions available)
        candidates = []
        warnings = []

        for record in records:
            if record.status != MigrationStatus.VERIFIED_MATCH:
                continue

            if not record.target_drive_file_id:
                continue

            metadata = self.target_checker(record.target_drive_file_id)

            if not metadata:
                warnings.append(CleanupCandidate(
                    record_id=record.record_id,
                    source_path=record.source_path or record.source_display_name,
                    target_drive_file_id=record.target_drive_file_id,
                    is_verified_still_exists=False,
                    message="Target file no longer exists in Google Drive. Do not delete source."
                ))
                continue

            # Verify size still matches
            if metadata.size != record.target_size:
                warnings.append(CleanupCandidate(
                    record_id=record.record_id,
                    source_path=record.source_path or record.source_display_name,
                    target_drive_file_id=record.target_drive_file_id,
                    is_verified_still_exists=False,
                    message="Target file size changed in Google Drive. Do not delete source."
                ))
                continue

            # Verify hash still matches if available
            hash_match = True
            if metadata.sha256Checksum and record.target_sha256:
                hash_match = metadata.sha256Checksum.lower() == record.target_sha256.lower()
            elif metadata.md5Checksum and record.target_md5:
                hash_match = metadata.md5Checksum.lower() == record.target_md5.lower()

            if not hash_match:
                warnings.append(CleanupCandidate(
                    record_id=record.record_id,
                    source_path=record.source_path or record.source_display_name,
                    target_drive_file_id=record.target_drive_file_id,
                    is_verified_still_exists=False,
                    message="Target file hash changed in Google Drive. Do not delete source."
                ))
                continue

            # OK
            candidates.append(CleanupCandidate(
                record_id=record.record_id,
                source_path=record.source_path or record.source_display_name,
                target_drive_file_id=record.target_drive_file_id,
                is_verified_still_exists=True,
                message="File verified in target. Safe to manually delete in Finder/Photos."
            ))

        return candidates, warnings
